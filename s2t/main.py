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

import logging
import os
import re
import subprocess
import sys

# Import config functions
from s2t.config import get_validated_config, send_notification

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


def main():
    """Main function to run the script."""
    try:
        # Get and validate configuration
        config = get_validated_config()

        # Determine which recorder to use based on mode and available dependencies
        if config.cli.silent or not gui_available:
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
    except ValueError as e:
        # Handle configuration errors (like missing API key)
        logger.error(str(e))
        # Send a notification about the error
        send_notification("S2T Error", str(e), urgency="critical")
        sys.exit(1)

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

        # Print the transcription to stdout
        print(f"Transcription: {transcription}")

        # Add newline if requested
        if config.cli.newline:
            transcription += "\n"
            logger.debug("Adding newline character")

        subprocess.run(["wtype", transcription])
    else:
        # Log at INFO level when transcription is empty
        logger.info("No speech detected or transcription was empty")
        print("No speech detected or transcription was empty")
        if config.cli.debug:
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
