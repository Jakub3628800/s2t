#!/usr/bin/env python3
"""
S2T (Speech to Text) - A command-line tool for speech recognition and transcription.

This script provides a unified interface for speech recognition using OpenAI's Whisper API.
It captures audio from your microphone, transcribes it, and types the result using wtype.

Features:
- Popup mode (default): Shows a GUI window with audio level and recording status
- Silent mode: Records without a GUI, using desktop notifications for feedback
- Automatic silence detection to stop recording
- Configurable parameters for silence detection
- Option to add a newline character after the transcription

Usage:
  s2t.py [options]

Options:
  --silent       Use silent mode (no GUI window, only notifications)
  --newline      Add a newline character after the transcription
  --threshold N  Set silence threshold (0.0-1.0, default: 0.05)
  --duration N   Set silence duration in seconds (default: 2.0)
  --debug        Enable debug output
  --help         Show this help message

Examples:
  s2t.py                     # Run in popup mode (default)
  s2t.py --silent            # Run in silent mode
  s2t.py --newline           # Add newline after transcription
  s2t.py --threshold 0.03    # Set custom silence threshold
  s2t.py --duration 1.5      # Set custom silence duration
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Import S2T modules directly
try:
    from s2t.config import DEFAULT_CONFIG_PATH, load_config
    from s2t.headless_recorder import TrulySilentRecorder
    from s2t.immediate_popup import ImmediatePopupRecorder
except ImportError:
    print("Error: S2T modules not found. Make sure you're in the S2T repository directory.")
    sys.exit(1)


def main():
    """Main function to run the script."""
    # Check for OpenAI API key in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        # Use full path for notify-send
        notify_send_path = shutil.which("notify-send")
        if notify_send_path:
            subprocess.run(
                [
                    notify_send_path,
                    "-u",
                    "critical",
                    "S2T Error",
                    "OPENAI_API_KEY environment variable not set.",
                ],
                check=False,
            )
        sys.exit(1)

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="S2T (Speech to Text) - A command-line tool for speech recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--silent", action="store_true", help="Use silent mode (no GUI window)")
    parser.add_argument(
        "--newline", action="store_true", help="Add a newline character after the transcription"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.05, help="Silence threshold (0.0-1.0, default: 0.05)"
    )
    parser.add_argument(
        "--duration", type=float, default=2.0, help="Silence duration in seconds (default: 2.0)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    # Path to the s2t repository
    s2t_path = Path.home() / "repos" / "s2t"

    # Change to the s2t directory
    try:
        os.chdir(s2t_path)
    except Exception as e:
        print(f"Error: Could not find s2t repository at {s2t_path}: {e}")
        # Use full path for notify-send
        notify_send_path = shutil.which("notify-send")
        if notify_send_path:
            subprocess.run(
                [
                    notify_send_path,
                    "-u",
                    "critical",
                    "S2T Error",
                    f"Could not find s2t repository at {s2t_path}",
                ],
                check=False,
            )
        sys.exit(1)

    # Notify that recording is starting
    notify_send_path = shutil.which("notify-send")
    if notify_send_path:
        subprocess.run([notify_send_path, "S2T", "Starting recording... Speak now"], check=False)

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Set the API key in the config
    config["backends"]["whisper_api"]["api_key"] = api_key

    # Update config with command-line parameters
    config["popup_recorder"] = config.get("popup_recorder", {})
    config["popup_recorder"]["silence_threshold"] = args.threshold
    config["popup_recorder"]["silence_duration"] = args.duration
    config["popup_recorder"]["vad_enabled"] = True

    try:
        # Determine which recorder to use based on mode
        if args.silent:
            # Silent mode - use TrulySilentRecorder
            recorder = TrulySilentRecorder(config)
        else:
            # Popup mode (default) - use ImmediatePopupRecorder
            recorder = ImmediatePopupRecorder(config)

        # Record and transcribe
        transcription = recorder.record_and_transcribe()

        # Remove TRANSCRIPTION_START: and :TRANSCRIPTION_END markers if present
        if transcription:
            match = re.search(r"TRANSCRIPTION_START:(.*):TRANSCRIPTION_END", transcription)
            if match:
                transcription = match.group(1)

        # Type the transcription if we have one
        if transcription and transcription != "0 characters":
            print(f"Transcription: {transcription}")

            # Add newline if requested
            if args.newline:
                transcription += "\n"
                print("Adding newline character")

            subprocess.run(["wtype", transcription])
        else:
            print("No speech detected or transcription was empty")
            if args.debug:
                print("No transcription returned from recorder")
            subprocess.run(["notify-send", "S2T", "No speech detected or transcription was empty"])

    except Exception as e:
        print(f"Error: {e}")
        subprocess.run(["notify-send", "-u", "critical", "S2T Error", f"Error: {e}"])
        sys.exit(1)


if __name__ == "__main__":
    main()
