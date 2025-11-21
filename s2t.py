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
from typing import Optional, List
from pywhispercpp.model import Model

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Global variables for signal handling
IS_RECORDING: bool = False
FRAMES: List[bytes] = []
STREAM: Optional[pyaudio.Stream] = None
RECORDER: Optional['AudioRecorder'] = None
TRANSCRIBER: Optional['WhisperTranscriber'] = None


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


def process_transcription(frames: List[bytes], recorder: 'AudioRecorder', transcriber: 'WhisperTranscriber', args) -> Optional[str]:
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

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    try:
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(recorder.channels)
            wf.setsampwidth(recorder.audio.get_sample_size(recorder.format))
            wf.setframerate(recorder.rate)
            wf.writeframes(b''.join(frames))

        transcription = transcriber.transcribe(temp_file.name)

        if transcription:
            print(transcription)

            # Send to tmux if requested
            if args.tmux:
                try:
                    subprocess.run(['tmux', 'send-keys', '-t', args.tmux, transcription], check=True)
                    subprocess.run(['tmux', 'send-keys', '-t', args.tmux, 'C-m'], check=True)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to send to tmux: {e}")

            # Type if requested
            if args.type:
                try:
                    subprocess.run(['wtype', transcription], check=True)
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to type transcription: {e}")

        return transcription
    finally:
        os.unlink(temp_file.name)


class WhisperTranscriber:
    def __init__(self) -> None:
        self.model: Optional[Model] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load whisper model"""
        try:
            self.model = Model('small', print_realtime=False, print_progress=False)
        except (OSError, RuntimeError) as e:
            logger.warning(f"Failed to load 'small' model: {e}, trying 'tiny'")
            try:
                self.model = Model('tiny', print_realtime=False, print_progress=False)
            except (OSError, RuntimeError) as e:
                logger.error(f"Failed to load 'tiny' model: {e}")
                sys.exit(1)

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio file"""
        if not self.model:
            return None

        try:
            segments = self.model.transcribe(audio_file_path)
            if segments and hasattr(segments[0], 'text'):
                transcription = " ".join([segment.text for segment in segments])
            else:
                transcription = str(segments)

            return transcription.strip()
        except (OSError, RuntimeError) as e:
            logger.error(f"Transcription failed: {e}")
            return None


def main() -> None:
    parser = argparse.ArgumentParser(description='Speech-to-Text tool using whisper.cpp')
    parser.add_argument('--tmux', '-t', metavar='SESSION',
                       help='Send transcription to specified tmux session')
    parser.add_argument('--type', action='store_true',
                       help='Type transcription at cursor location using wtype')
    parser.add_argument('--enter', action='store_true',
                       help='Use Enter key controls (press Enter to start/stop recording)')
    args = parser.parse_args()

    # Use global variables for signal handler
    global IS_RECORDING, FRAMES, STREAM, RECORDER, TRANSCRIBER

    def signal_handler(signum: int, frame) -> None:
        global IS_RECORDING, FRAMES, STREAM
        IS_RECORDING = False

        if STREAM:
            STREAM.stop_stream()
            STREAM.close()

        # Process transcription
        if FRAMES and RECORDER and TRANSCRIBER:
            process_transcription(FRAMES, RECORDER, TRANSCRIBER, args)

        if RECORDER:
            RECORDER.cleanup()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Suppress ALSA warnings
    os.environ['ALSA_PCM_CARD'] = '0'
    os.environ['ALSA_PCM_DEVICE'] = '0'

    # Suppress whisper model loading logs
    logging.getLogger('pywhispercpp').setLevel(logging.ERROR)

    # Initialize components (suppress stderr from whisper C library)
    try:
        # Suppress C library output by redirecting file descriptor 2 (stderr)
        import io
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        old_stderr_fd = os.dup(2)
        os.dup2(devnull_fd, 2)

        try:
            RECORDER = AudioRecorder()
            TRANSCRIBER = WhisperTranscriber()
        finally:
            # Restore stderr
            os.dup2(old_stderr_fd, 2)
            os.close(devnull_fd)
            os.close(old_stderr_fd)
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
                frames_per_buffer=RECORDER.chunk
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
            IS_RECORDING = True
            STREAM = RECORDER.audio.open(
                format=RECORDER.format,
                channels=RECORDER.channels,
                rate=RECORDER.rate,
                input=True,
                frames_per_buffer=RECORDER.chunk
            )
            
            def record() -> None:
                global FRAMES
                while IS_RECORDING:
                    try:
                        data = STREAM.read(RECORDER.chunk, exception_on_overflow=False)
                        FRAMES.append(data)
                    except Exception:
                        break
            
            record_thread = threading.Thread(target=record)
            record_thread.start()
            
            # Record until killed by signal
            try:
                while True:
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