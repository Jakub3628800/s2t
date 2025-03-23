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
  s2t [options]

Options:
  --silent       Use silent mode (no GUI window, only notifications)
  --newline      Add a newline character after the transcription
  --threshold N  Set silence threshold (0.0-1.0, default: 0.05)
  --duration N   Set silence duration in seconds (default: 2.0)
  --debug        Enable debug output
  --help         Show this help message

Examples:
  s2t                     # Run in popup mode (default)
  s2t --silent            # Run in silent mode
  s2t --newline           # Add newline after transcription
  s2t --threshold 0.03    # Set custom silence threshold
  s2t --duration 1.5      # Set custom silence duration
"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys

# Import config directly
from s2t.config import DEFAULT_CONFIG_PATH, load_config

# Configure logger
logger = logging.getLogger("s2t")

# Try to import GUI dependencies, set gui_available flag based on success
gui_available = False
try:
    import gi

    gi.require_version("Gtk", "4.0")
    # We don't need to import Gtk directly, just ensure gi is available
    import gi.repository

    gui_available = True
except (ImportError, ValueError):
    gui_available = False
    logger.info("GUI dependencies not available. Popup mode disabled.")

# Try to import recorder classes - these will be None if import fails
silent_recorder_class = None
try:
    from s2t.truly_silent import TrulySilentRecorder

    silent_recorder_class = TrulySilentRecorder
except ImportError:
    logger.debug("Could not import TrulySilentRecorder")

popup_recorder_class = None
try:
    from s2t.immediate_popup import ImmediatePopupRecorder

    popup_recorder_class = ImmediatePopupRecorder
except ImportError:
    logger.debug("Could not import ImmediatePopupRecorder")


# Function to check system dependencies
def check_system_dependencies():
    """Check if required system dependencies are installed."""
    missing_deps = []

    # Check for libgirepository (for GUI mode)
    try:
        subprocess.run(
            ["pkg-config", "--exists", "gobject-introspection-1.0"], check=True, capture_output=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgirepository1.0-dev")

    # Check for GTK4 (for popup mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gtk4"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgtk-4-dev")

    # Check for wtype (for typing)
    try:
        subprocess.run(["which", "wtype"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("wtype")

    return missing_deps


def print_dependency_warning(missing_deps):
    """Print a warning about missing dependencies."""
    logger.warning("\n⚠️  Missing system dependencies detected! ⚠️")
    logger.warning("The following system packages are required but not found:")
    for dep in missing_deps:
        logger.warning(f"  - {dep}")
    logger.warning("\nOn Ubuntu/Debian, install them with:")
    logger.warning(f"  sudo apt-get install {' '.join(missing_deps)}")
    logger.warning("\nCannot continue without these dependencies.\n")


def setup_logging(debug=False):
    """Configure the logging system based on debug flag."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure s2t logger
    logger.setLevel(log_level)

    # Add console handler if not already present
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def main():
    """Main function to run the script."""
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
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to configuration file (YAML or JSON, default: {DEFAULT_CONFIG_PATH})",
    )
    args = parser.parse_args()

    # Setup logging based on debug flag
    setup_logging(args.debug)

    # Validate the config file extension
    if args.config:
        if not os.path.exists(args.config):
            # This will create a default config at the specified path
            logger.info(f"Config file not found, will create a default config at: {args.config}")
        # Ensure the config file has a valid extension
        elif not args.config.endswith((".yaml", ".yml", ".json")):
            logger.warning(
                f"Config file should have .yaml, .yml, or .json extension. Found: {args.config}"
            )
            logger.warning("Will attempt to load it anyway, assuming YAML format.")

    # Load configuration from specified path
    config = load_config(args.config)

    # Check for OpenAI API key in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set.")
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

    # Set the API key in the config
    config.backends.whisper_api.api_key = api_key

    # Override config with command-line arguments if provided
    if args.threshold:
        config.popup_recorder.silence_threshold = args.threshold
    if args.duration:
        config.popup_recorder.silence_duration = args.duration
    config.popup_recorder.vad_enabled = True

    # Determine which recorder to use based on mode and available dependencies
    if args.silent or not gui_available:
        # Silent mode - use TrulySilentRecorder
        if silent_recorder_class is None:
            # Last attempt to import if not available at module level
            try:
                from s2t.truly_silent import TrulySilentRecorder

                recorder_class = TrulySilentRecorder
            except ImportError:
                logger.error("Could not import TrulySilentRecorder")
                sys.exit(1)
        else:
            recorder_class = silent_recorder_class
        recorder = recorder_class(config)
    else:
        # Popup mode (default) - use ImmediatePopupRecorder
        if popup_recorder_class is None:
            # Last attempt to import if not available at module level
            try:
                from s2t.immediate_popup import ImmediatePopupRecorder

                recorder_class = ImmediatePopupRecorder
            except ImportError:
                logger.error("Could not import ImmediatePopupRecorder")
                sys.exit(1)
        else:
            recorder_class = popup_recorder_class
        recorder = recorder_class(config)

    # Record and transcribe
    transcription = recorder.record_and_transcribe()

    # Get the audio file path for cleanup later
    audio_file_path = getattr(recorder, "audio_file", None)

    # Remove TRANSCRIPTION_START: and :TRANSCRIPTION_END markers if present
    if transcription:
        match = re.search(r"TRANSCRIPTION_START:(.*):TRANSCRIPTION_END", transcription)
        if match:
            transcription = match.group(1)

    # Type the transcription if we have one
    if transcription and transcription != "0 characters":
        logger.info(f"Transcription: {transcription}")

        # Add newline if requested
        if args.newline:
            transcription += "\n"
            logger.debug("Adding newline character")

        subprocess.run(["wtype", transcription])
    else:
        logger.info("No speech detected or transcription was empty")
        if args.debug:
            logger.debug("No transcription returned from recorder")

    # Clean up the temporary audio file
    if audio_file_path and os.path.exists(audio_file_path):
        try:
            os.remove(audio_file_path)
            logger.debug(f"Removed temporary audio file: {audio_file_path}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary audio file: {e}")


if __name__ == "__main__":
    main()
