#!/usr/bin/env python3
"""
Simple command-line interface for DesktopSTT without GUI dependencies.
Works well with Wayland/Sway environments.
"""

import os
import sys
import time
import logging
import argparse
import signal
import threading
import traceback

from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleRecorder:
    """Simple command-line recorder without GUI dependencies."""

    def __init__(self, config, silent=False):
        """
        Initialize the simple recorder.

        Args:
            config: Application configuration dictionary
            silent: Whether to suppress output and logging
        """
        self.config = config
        self.silent = silent
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
            if not self.silent:
                logger.warning("Recording is already in progress")
            return False

        if not self.backend.is_available():
            if not self.silent:
                logger.error("Speech-to-text backend is not available")
                logger.error(f"API key set: {bool(self.config['backends']['whisper_api']['api_key'])}")
            return False

        success = self.recorder.start_recording()
        if success:
            self.is_recording = True
            if not self.silent:
                logger.info("Started recording")

            # Start the recording indicator in a separate thread if not silent
            if not self.silent:
                self._start_indicator()

            return True
        else:
            if not self.silent:
                logger.error("Failed to start recording")
            return False

    def stop_recording(self):
        """Stop recording audio and return the path to the recorded file."""
        if not self.is_recording:
            if not self.silent:
                logger.warning("No recording in progress")
            return None

        self.is_recording = False
        self.stop_event.set()

        # Stop recording and get the audio file
        audio_file = self.recorder.stop_recording()

        if audio_file:
            if not self.silent:
                logger.info(f"Stopped recording, saved to {audio_file}")
            return audio_file
        else:
            if not self.silent:
                logger.error("Failed to save recording")
            return None

    def transcribe(self, audio_file):
        """
        Transcribe the given audio file to text.

        Args:
            audio_file: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        if not audio_file or not os.path.exists(audio_file):
            if not self.silent:
                logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            if not self.silent:
                logger.info(f"Transcribing audio file: {audio_file}")
                logger.info(f"Using backend: {self.backend.get_name()}")
                logger.info(f"API key set: {bool(self.config['backends']['whisper_api']['api_key'])}")

            result = self.backend.transcribe(audio_file)
            text = result.get('text', '')

            if not text:
                if not self.silent:
                    logger.error("No transcription result")
                return None

            if not self.silent:
                logger.info(f"Transcription successful: {len(text)} characters")
            return text

        except Exception as e:
            if not self.silent:
                logger.error(f"Error transcribing audio: {e}")
                logger.error(traceback.format_exc())
            return None

    def record_and_transcribe(self, duration=None):
        """
        Record audio for the specified duration and transcribe it.

        Args:
            duration: Duration in seconds to record, or None to wait for user input

        Returns:
            The transcribed text, or None if recording or transcription failed
        """
        # Start recording
        if not self.start_recording():
            return None

        try:
            # Wait for the specified duration or user input
            if duration:
                if not self.silent:
                    logger.info(f"Recording for {duration} seconds...")
                time.sleep(duration)
                audio_file = self.stop_recording()
            else:
                # Wait for user input
                if not self.silent:
                    logger.info("Recording... Press Enter to stop")
                try:
                    input()
                except KeyboardInterrupt:
                    pass
                audio_file = self.stop_recording()

            if not audio_file:
                if not self.silent:
                    logger.error("No audio file was created")
                return None

            # Transcribe the audio
            if not self.silent:
                logger.info(f"Transcribing audio file: {audio_file}")
            return self.transcribe(audio_file)

        except Exception as e:
            if not self.silent:
                logger.error(f"Error in record_and_transcribe: {e}")
                logger.error(traceback.format_exc())
            if self.is_recording:
                self.stop_recording()
            return None

    def _start_indicator(self):
        """Start a simple recording indicator in the terminal."""
        def show_indicator():
            seconds = 0
            spinner = ['|', '/', '-', '\\']
            try:
                while self.is_recording and not self.stop_event.is_set():
                    minutes, secs = divmod(seconds, 60)
                    time_str = f"{minutes:02d}:{secs:02d}"

                    # Clear the line and show the indicator
                    sys.stdout.write(f"\r[{spinner[seconds % 4]}] Recording... {time_str} (Press Enter to stop)")
                    sys.stdout.flush()

                    time.sleep(1)
                    seconds += 1
            except Exception as e:
                if not self.silent:
                    logger.error(f"Error in indicator thread: {e}")
            finally:
                # Clear the line when done
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()

        indicator_thread = threading.Thread(target=show_indicator)
        indicator_thread.daemon = True
        indicator_thread.start()

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals."""
        if not self.silent:
            logger.info("Received interrupt signal, stopping recording...")
        if self.is_recording:
            self.stop_recording()
        sys.exit(0)


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='DesktopSTT Simple CLI')
    parser.add_argument(
        '--config',
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f'Path to config file (default: {DEFAULT_CONFIG_PATH})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--time',
        type=float,
        help='Record for specified number of seconds and then stop'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        default='.env',
        help='Path to .env file containing API key (default: .env)'
    )
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Silent mode - output only the transcribed text'
    )
    args = parser.parse_args()

    # Set up logging
    if args.silent:
        # Disable logging in silent mode
        logging.disable(logging.CRITICAL)
    else:
        log_level = logging.DEBUG if args.debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Load environment variables from .env file
    if not args.silent:
        if load_dotenv(args.env_file):
            logger.info(f"Loaded environment variables from {args.env_file}")
    else:
        load_dotenv(args.env_file)

    # Load configuration
    config = load_config(args.config)

    # Check if API key is set in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        # Set the API key in the config
        config["backends"]["whisper_api"]["api_key"] = api_key
        if not args.silent:
            logger.info("Using OpenAI API key from environment variables")
            logger.debug(f"API key length: {len(api_key)}")

    # Check if API key is set in config
    if not config["backends"]["whisper_api"]["api_key"] and not args.silent:
        logger.warning("No OpenAI API key found in config or environment variables")
        logger.warning("Transcription may fail. Set OPENAI_API_KEY in .env file or config.")

    # Create simple recorder
    recorder = SimpleRecorder(config, silent=args.silent)

    # Record and transcribe
    text = recorder.record_and_transcribe(duration=args.time)

    if text:
        # Output the transcription
        if args.output:
            with open(args.output, 'w') as f:
                f.write(text)
            if not args.silent:
                logger.info(f"Transcription saved to {args.output}")
        else:
            # Output to stdout
            print(text)
        return 0
    else:
        if not args.silent:
            logger.error("Failed to transcribe audio")
        return 1

if __name__ == "__main__":
    sys.exit(main())
