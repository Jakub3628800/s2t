#!/usr/bin/env python3
"""
Immediate popup recorder for DesktopSTT.
This version starts recording immediately without waiting for speech.
"""

import os
import sys
import argparse
import tempfile
import logging
from desktopstt.popup_recorder import PopupRecorder, RecordingWindow
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv
from gi.repository import GLib

# Set up logging
logger = logging.getLogger(__name__)


class ImmediateRecordingWindow(RecordingWindow):
    """Modified recording window that shows 'Recording in progress' instead of 'Waiting for speech'."""

    def __init__(self, on_stop_callback=None, title="DesktopSTT Recording"):
        super().__init__(on_stop_callback, title)
        # Set the VAD status to show recording in progress immediately
        self.update_vad_status(True)


class ImmediatePopupRecorder(PopupRecorder):
    """Modified popup recorder that starts recording immediately without waiting for speech."""

    def _show_window(self):
        """Show the recording window with immediate recording status."""
        self.window = ImmediateRecordingWindow(on_stop_callback=self._on_window_stop)
        self.window.connect("close-request", self._on_window_close)
        self.window.present()
        # Set speech detection to true immediately
        self.is_speech = True


def main():
    """Command-line entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Immediate recording popup recorder')
    parser.add_argument('--output', type=str, help='Output file for transcription')
    parser.add_argument('--silence-threshold', type=float, default=0.05, help='Threshold for silence detection (0.0-1.0)')
    parser.add_argument('--silence-duration', type=float, default=3.0, help='Duration of silence before stopping (seconds)')
    parser.add_argument('--env-file', type=str, default='.env', help='Path to .env file (default: .env)')
    parser.add_argument('--wtype', action='store_true', help='Output transcription using wtype')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--silent', action='store_true', help='Suppress all output except the transcription')
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    if args.silent:
        log_level = logging.ERROR  # Suppress most logs in silent mode

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load environment variables from .env file
    if load_dotenv(args.env_file):
        logger.info(f"Loaded environment variables from {args.env_file}")

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Check if API key is set in environment variables
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
    if api_key:
        # Set the API key in the config
        config["backends"]["whisper_api"]["api_key"] = api_key
        logger.info("Using OpenAI API key from environment variables")
    else:
        logger.warning("No OpenAI API key found in environment variables")

    # Set popup recorder configuration
    config["popup_recorder"] = config.get("popup_recorder", {})
    config["popup_recorder"]["silence_threshold"] = args.silence_threshold
    config["popup_recorder"]["silence_duration"] = args.silence_duration
    config["popup_recorder"]["vad_enabled"] = True
    config["popup_recorder"]["min_recording_time"] = 0.0  # Start VAD immediately

    # Create recorder
    recorder = ImmediatePopupRecorder(config)

    # Record and transcribe
    text = recorder.record_and_transcribe()

    # Handle the transcription result
    if text:
        if args.wtype:
            # Create a temporary file for wtype
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                temp_file.write(text + "\n")
                temp_output = temp_file.name

            # Use wtype to type the transcription
            try:
                import subprocess
                subprocess.run(["wtype", "-"], input=f"{text}\n".encode(), check=True)
                logger.info("Transcription typed using wtype")
            except Exception as e:
                logger.error(f"Error using wtype: {e}")
                # Fall back to printing
                print(text)
            finally:
                # Clean up temporary file
                os.unlink(temp_output)
        elif args.output:
            # Write to output file
            with open(args.output, 'w') as f:
                f.write(text + "\n")  # Add newline at the end
            logger.info(f"Transcription saved to {args.output}")
        else:
            # Output to stdout
            print(text)
        return 0
    else:
        logger.error("Failed to transcribe audio")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 