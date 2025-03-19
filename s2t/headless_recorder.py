#!/usr/bin/env python3
"""
Headless recorder for S2T.

This module provides a recorder that runs without a GUI but shows desktop notifications.
"""

import argparse
import logging
import os
import sys
import tempfile

import gi

gi.require_version("Notify", "0.7")
from gi.repository import Notify

from s2t.config import DEFAULT_CONFIG_PATH, load_config
from s2t.truly_silent import TrulySilentRecorder

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def show_notification(title, message, urgency="low"):
    """Show a desktop notification."""
    try:
        notification = Notify.Notification.new(title, message, "dialog-information")
        if urgency == "critical":
            notification.set_urgency(Notify.Urgency.CRITICAL)
        notification.show()
    except Exception as e:
        logger.error(f"Failed to show notification: {e}")


def main():
    """Command-line entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Headless recorder with notification support")
    parser.add_argument("--output", type=str, help="Output file for transcription")
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=0.05,
        help="Threshold for silence detection (0.0-1.0)",
    )
    parser.add_argument(
        "--silence-duration",
        type=float,
        default=3.0,
        help="Duration of silence before stopping (seconds)",
    )
    parser.add_argument(
        "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
    )
    parser.add_argument("--wtype", action="store_true", help="Output transcription using wtype")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress all output except the transcription",
    )
    parser.add_argument(
        "--no-notifications", action="store_true", help="Disable desktop notifications"
    )
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    if args.silent:
        log_level = logging.ERROR  # Suppress most logs in silent mode

    # Configure logging to stderr instead of stdout
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Check for environment variables
    logger.info(f"Using env file: {args.env_file} (parsed automatically)")

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

    # Set silent recorder configuration
    if "silent_recorder" not in config:
        config["silent_recorder"] = {}

    config["silent_recorder"]["silence_threshold"] = args.silence_threshold
    config["silent_recorder"]["silence_duration"] = args.silence_duration
    config["silent_recorder"]["vad_enabled"] = True
    config["silent_recorder"]["min_recording_time"] = 1.0

    # Create recorder
    recorder = TrulySilentRecorder(config)

    # Initialize notifications
    Notify.init("S2T")

    # Show notification that recording is starting
    if not args.no_notifications:
        show_notification("S2T", "Recording started. Speak now...")

    # Record and transcribe
    text = recorder.record_and_transcribe()

    # Handle the transcription result
    if text:
        # Output the transcription to stdout with a special marker for easy extraction
        print(f"TRANSCRIPTION_START:{text}:TRANSCRIPTION_END")

        # Show notification that transcription was successful
        if not args.no_notifications:
            show_notification("S2T", "Transcription successful")

        if args.wtype:
            # Create a temporary file for wtype
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_file.write(text + "\n")
                temp_output = temp_file.name

            # Use wtype to type the transcription
            try:
                subprocess.run(["wtype", "-"], input=f"{text}\n".encode(), check=True)
                logger.info("Transcription typed using wtype")
            except Exception as e:
                logger.error(f"Error using wtype: {e}")
            finally:
                # Clean up temporary file
                os.unlink(temp_output)
        elif args.output:
            # Write to output file
            with open(args.output, "w") as f:
                f.write(text + "\n")  # Add newline at the end
            logger.info(f"Transcription saved to {args.output}")
        return 0
    else:
        # Show notification that transcription failed
        if not args.no_notifications:
            show_notification("S2T Error", "Failed to transcribe audio", "critical")

        logger.error("Failed to transcribe audio")
        return 1


if __name__ == "__main__":
    sys.exit(main())
