#!/usr/bin/env python3
"""
Truly silent recorder for S2T.

This module provides a recorder that runs without any GUI or notifications.
"""

import argparse
import logging
import os
import signal
import sys
import threading
import time
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

# Disable logging
logging.disable(logging.CRITICAL)

# Import gi and set the required version
import gi

gi.require_version("Gtk", "4.0")

# Import our modules
from s2t.audio import AudioRecorder
from s2t.backends import get_backend
from s2t.config import DEFAULT_CONFIG_PATH, load_config
from s2t.utils import load_dotenv


class TrulySilentRecorder:
    """Records audio and transcribes it without any GUI or notifications."""

    def __init__(self, config):
        """Initialize the recorder with the given configuration."""
        self.config = config
        self.recorder = AudioRecorder(config)
        self.backend = get_backend(config)
        self.is_recording = False
        self.stop_event = threading.Event()

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            return False

        if not self.backend.is_available():
            return False

        success = self.recorder.start_recording()
        if success:
            self.is_recording = True
            return True
        else:
            return False

    def stop_recording(self):
        """Stop recording audio and return the path to the recorded file."""
        if not self.is_recording:
            return None

        self.is_recording = False
        self.stop_event.set()

        # Stop recording and get the audio file
        audio_file = self.recorder.stop_recording()

        if audio_file:
            return audio_file
        else:
            return None

    def transcribe(self, audio_file):
        """Transcribe the given audio file to text."""
        if not audio_file or not os.path.exists(audio_file):
            return None

        try:
            result = self.backend.transcribe(audio_file)
            text = result.get("text", "")

            if not text:
                return None

            return text

        except Exception:
            return None

    def record_and_transcribe(self, duration=None):
        """Record audio for the specified duration and transcribe it."""
        # Start recording
        if not self.start_recording():
            return None

        try:
            # Wait for the specified duration or user input
            if duration:
                time.sleep(duration)
                audio_file = self.stop_recording()
            else:
                try:
                    input()
                except KeyboardInterrupt:
                    pass
                audio_file = self.stop_recording()

            if not audio_file:
                return None

            # Transcribe the audio
            return self.transcribe(audio_file)

        except Exception:
            if self.is_recording:
                self.stop_recording()
            return None

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals."""
        if self.is_recording:
            self.stop_recording()
        sys.exit(0)


def main():
    """Main entry point for the truly silent recorder."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="S2T Truly Silent CLI")
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument(
        "--time",
        type=float,
        help="Record for specified number of seconds and then stop",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to .env file containing API key (default: .env)",
    )
    args = parser.parse_args()

    # Redirect stderr to /dev/null to suppress ALSA warnings
    stderr_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)

    try:
        # Load environment variables from .env file
        load_dotenv(args.env_file)

        # Load configuration
        config = load_config(args.config)

        # Check if API key is set in environment variables
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            # Set the API key in the config
            config["backends"]["whisper_api"]["api_key"] = api_key

        # Create recorder
        recorder = TrulySilentRecorder(config)

        # Record and transcribe
        text = recorder.record_and_transcribe(duration=args.time)

        if text:
            # Output the transcription
            if args.output:
                with open(args.output, "w") as f:
                    f.write(text)
            else:
                # Output to stdout
                print(text)
            return 0
        else:
            return 1

    finally:
        # Restore stderr
        os.dup2(stderr_fd, 2)
        os.close(stderr_fd)


if __name__ == "__main__":
    sys.exit(main())
