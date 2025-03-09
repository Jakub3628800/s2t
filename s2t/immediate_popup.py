#!/usr/bin/env python3
"""
Immediate popup recorder for S2T.

This module provides a popup recorder that starts recording immediately when launched.
"""

import os
import sys
import argparse
import tempfile
import logging
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from s2t.popup_recorder import PopupRecorder, RecordingWindow
from s2t.config import load_config, DEFAULT_CONFIG_PATH
from s2t.utils import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)


class ImmediateRecordingWindow(RecordingWindow):
    """Recording window that starts recording immediately."""

    def __init__(self, on_stop_callback=None, title="S2T Recording"):
        super().__init__(on_stop_callback, title)
        # Start with "Recording in progress" status
        self._set_vad_status("<span foreground='red'>Recording in progress</span>")


class ImmediatePopupRecorder(PopupRecorder):
    """Popup recorder that starts recording immediately."""

    def _show_window(self):
        """Show the recording window."""
        self.window = ImmediateRecordingWindow(
            on_stop_callback=self._on_window_stop,
            title="S2T Immediate Recording"
        )
        self.window.present()
        return self.window


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

    # Configure logging to stderr instead of stdout
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
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
        # Output the transcription to stdout with a special marker for easy extraction
        print(f"TRANSCRIPTION_START:{text}:TRANSCRIPTION_END")

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
            finally:
                # Clean up temporary file
                os.unlink(temp_output)
        elif args.output:
            # Write to output file
            with open(args.output, 'w') as f:
                f.write(text + "\n")  # Add newline at the end
            logger.info(f"Transcription saved to {args.output}")
        return 0
    else:
        logger.error("Failed to transcribe audio")
        return 1


if __name__ == "__main__":
    sys.exit(main())
