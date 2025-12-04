#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pywhispercpp>=1.3.0",
#     "pyaudio>=0.2.11",
#     "setuptools>=61.0",
# ]
# ///

"""Speech-to-Text tool using whisper.cpp"""

import os
import sys
import tempfile
import wave
import pyaudio
import threading
import time
import argparse
import signal
import subprocess
import logging
import types
from contextlib import contextmanager
from typing import Optional, List
from pywhispercpp.model import Model

# Configure logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Global variables for signal handling
RECORDING_EVENT: threading.Event = threading.Event()
FRAMES: List[bytes] = []
FRAMES_LOCK: threading.Lock = threading.Lock()
RECORD_THREAD: Optional[threading.Thread] = None
STREAM: Optional[pyaudio.Stream] = None
RECORDER: Optional["AudioRecorder"] = None
TRANSCRIBER: Optional["WhisperTranscriber"] = None


@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr from C libraries."""
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    old_stderr_fd = os.dup(2)
    os.dup2(devnull_fd, 2)
    try:
        yield
    finally:
        os.dup2(old_stderr_fd, 2)
        os.close(devnull_fd)
        os.close(old_stderr_fd)


class AudioRecorder:
    def __init__(self) -> None:
        self.audio = pyaudio.PyAudio()
        # Audio settings
        self.chunk: int = 1024
        self.format = pyaudio.paInt16
        self.channels: int = 1
        self.rate: int = 16000

    def cleanup(self) -> None:
        """Clean up audio resources"""
        self.audio.terminate()


def process_transcription(
    frames: List[bytes], recorder: "AudioRecorder", transcriber: "WhisperTranscriber", args: argparse.Namespace
) -> Optional[str]:
    """Process recorded audio frames and output transcription.

    Args:
        frames: List of audio data frames
        recorder: AudioRecorder instance
        transcriber: WhisperTranscriber instance
        args: Parsed command-line arguments

    Returns:
        The transcription text, or None if no transcription
    """
    if not frames:
        return None

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    try:
        with wave.open(temp_file.name, "wb") as wf:
            wf.setnchannels(recorder.channels)
            wf.setsampwidth(recorder.audio.get_sample_size(recorder.format))
            wf.setframerate(recorder.rate)
            wf.writeframes(b"".join(frames))

        transcription = transcriber.transcribe(temp_file.name)

        if transcription:
            print(transcription)

            # Type if requested
            if args.type:
                try:
                    subprocess.run(["wtype", transcription], check=True)
                except FileNotFoundError:
                    logger.error("wtype not found. Install wtype to use --type option (Wayland only).")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to type transcription: {e}")

        return transcription
    finally:
        try:
            os.unlink(temp_file.name)
        except OSError as e:
            logger.warning(f"Failed to delete temp file {temp_file.name}: {e}")


class WhisperTranscriber:
    def __init__(self) -> None:
        self.model: Optional[Model] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load whisper model"""
        try:
            self.model = Model("small", print_realtime=False, print_progress=False)
        except (OSError, RuntimeError) as e:
            logger.warning(f"Failed to load 'small' model: {e}, trying 'tiny'")
            try:
                self.model = Model("tiny", print_realtime=False, print_progress=False)
            except (OSError, RuntimeError) as e:
                logger.error(f"Failed to load 'tiny' model: {e}")
                sys.exit(1)

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file"""
        if not self.model:
            return None

        try:
            segments = self.model.transcribe(audio_file_path)
            if segments and hasattr(segments[0], "text"):
                transcription = " ".join([segment.text for segment in segments])
            else:
                transcription = str(segments)

            return transcription.strip()
        except (OSError, RuntimeError) as e:
            logger.error(f"Transcription failed: {e}")
            return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Speech-to-Text tool using whisper.cpp")
    parser.add_argument("--type", action="store_true", help="Type transcription at cursor location using wtype")
    parser.add_argument(
        "--enter", action="store_true", help="Use Enter key controls (press Enter to start/stop recording)"
    )
    args = parser.parse_args()

    # Use global variables for signal handler
    global RECORDING_EVENT, FRAMES, FRAMES_LOCK, RECORD_THREAD, STREAM, RECORDER, TRANSCRIBER

    def signal_handler(signum: int, frame: Optional[types.FrameType]) -> None:
        global RECORDING_EVENT, FRAMES, RECORD_THREAD, STREAM
        # Signal the recording thread to stop
        RECORDING_EVENT.clear()

        # Wait for recording thread to finish (with timeout)
        if RECORD_THREAD and RECORD_THREAD.is_alive():
            RECORD_THREAD.join(timeout=1.0)

        # Now safe to close stream - recording thread has stopped
        if STREAM:
            STREAM.stop_stream()
            STREAM.close()

        # Process transcription with thread-safe frame access
        with FRAMES_LOCK:
            frames_copy = FRAMES.copy()
        if frames_copy and RECORDER and TRANSCRIBER:
            process_transcription(frames_copy, RECORDER, TRANSCRIBER, args)

        # Exit without cleanup - it will be handled in finally block
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Suppress ALSA warnings
    os.environ["ALSA_PCM_CARD"] = "0"
    os.environ["ALSA_PCM_DEVICE"] = "0"

    # Suppress whisper model loading logs
    logging.getLogger("pywhispercpp").setLevel(logging.ERROR)

    with suppress_stderr():
        # Initialize components
        try:
            RECORDER = AudioRecorder()
            TRANSCRIBER = WhisperTranscriber()
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            sys.exit(1)

        try:
            if args.enter:
                # Enter key mode
                local_frames = []
                is_recording_event = threading.Event()
                is_recording_event.set()

                local_stream = RECORDER.audio.open(
                    format=RECORDER.format,
                    channels=RECORDER.channels,
                    rate=RECORDER.rate,
                    input=True,
                    frames_per_buffer=RECORDER.chunk,
                )

                def record() -> None:
                    while is_recording_event.is_set() and local_stream:
                        try:
                            data = local_stream.read(RECORDER.chunk, exception_on_overflow=False)
                            local_frames.append(data)
                        except Exception as e:
                            logger.error(f"Error reading audio: {e}")
                            break

                record_thread = threading.Thread(target=record)
                record_thread.start()

                input()  # Wait for Enter

                is_recording_event.clear()
                record_thread.join()

                local_stream.stop_stream()
                local_stream.close()

                if local_frames:
                    process_transcription(local_frames, RECORDER, TRANSCRIBER, args)
            else:
                # Push-to-talk mode (record until killed)
                RECORDING_EVENT.set()
                STREAM = RECORDER.audio.open(
                    format=RECORDER.format,
                    channels=RECORDER.channels,
                    rate=RECORDER.rate,
                    input=True,
                    frames_per_buffer=RECORDER.chunk,
                )

                def record() -> None:
                    global FRAMES
                    while RECORDING_EVENT.is_set():
                        try:
                            data = STREAM.read(RECORDER.chunk, exception_on_overflow=False)
                            with FRAMES_LOCK:
                                FRAMES.append(data)
                        except Exception as e:
                            logger.error(f"Error reading audio: {e}")
                            break

                RECORD_THREAD = threading.Thread(target=record)
                RECORD_THREAD.start()

                # Record until killed by signal
                try:
                    while RECORDING_EVENT.is_set():
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    signal_handler(signal.SIGINT, None)
        except KeyboardInterrupt:
            pass
        finally:
            if RECORDER:
                RECORDER.cleanup()


if __name__ == "__main__":
    main()
