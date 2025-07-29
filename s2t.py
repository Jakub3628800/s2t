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
from typing import Optional, List
from pywhispercpp.model import Model

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


class WhisperTranscriber:
    def __init__(self) -> None:
        self.model: Optional[Model] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load whisper model"""
        try:
            self.model = Model('small', print_realtime=False, print_progress=False)
        except Exception:
            try:
                self.model = Model('tiny', print_realtime=False, print_progress=False)
            except Exception:
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
        except Exception:
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
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(RECORDER.channels)
                wf.setsampwidth(RECORDER.audio.get_sample_size(RECORDER.format))
                wf.setframerate(RECORDER.rate)
                wf.writeframes(b''.join(FRAMES))
            
            transcription = TRANSCRIBER.transcribe(temp_file.name)
            os.unlink(temp_file.name)
            
            if transcription:
                print(transcription)
                
                # Send to tmux if requested
                if args.tmux:
                    try:
                        subprocess.run(['tmux', 'send-keys', '-t', args.tmux, transcription], check=True)
                        subprocess.run(['tmux', 'send-keys', '-t', args.tmux, 'C-m'], check=True)
                    except subprocess.CalledProcessError:
                        pass
                
                # Type if requested
                if args.type:
                    try:
                        subprocess.run(['wtype', transcription], check=True)
                    except subprocess.CalledProcessError:
                        pass
        
        if RECORDER:
            RECORDER.cleanup()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Suppress ALSA warnings
    os.environ['ALSA_PCM_CARD'] = '0'
    os.environ['ALSA_PCM_DEVICE'] = '0'

    # Initialize components
    try:
        RECORDER = AudioRecorder()
        TRANSCRIBER = WhisperTranscriber()
    except Exception:
        sys.exit(1)

    try:
        if args.enter:
            # Enter key mode
            local_frames = []
            local_is_recording = True
            
            local_stream = RECORDER.audio.open(
                format=RECORDER.format,
                channels=RECORDER.channels,
                rate=RECORDER.rate,
                input=True,
                frames_per_buffer=RECORDER.chunk
            )
            
            def record() -> None:
                while local_is_recording and local_stream:
                    data = local_stream.read(RECORDER.chunk, exception_on_overflow=False)
                    local_frames.append(data)
            
            record_thread = threading.Thread(target=record)
            record_thread.start()
            
            input()  # Wait for Enter
            
            local_is_recording = False
            record_thread.join()
            
            local_stream.stop_stream()
            local_stream.close()
            
            transcription: Optional[str] = None
            
            if local_frames:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                with wave.open(temp_file.name, 'wb') as wf:
                    wf.setnchannels(RECORDER.channels)
                    wf.setsampwidth(RECORDER.audio.get_sample_size(RECORDER.format))
                    wf.setframerate(RECORDER.rate)
                    wf.writeframes(b''.join(local_frames))
                
                transcription = TRANSCRIBER.transcribe(temp_file.name)
                os.unlink(temp_file.name)
                
                if transcription:
                    print(transcription)
                    
                    if args.tmux:
                        try:
                            subprocess.run(['tmux', 'send-keys', '-t', args.tmux, transcription], check=True)
                            subprocess.run(['tmux', 'send-keys', '-t', args.tmux, 'C-m'], check=True)
                        except subprocess.CalledProcessError:
                            pass
                    
                    if args.type:
                        try:
                            subprocess.run(['wtype', transcription], check=True)
                        except subprocess.CalledProcessError:
                            pass
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