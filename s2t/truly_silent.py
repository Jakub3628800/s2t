#!/usr/bin/env python3
"""
Truly silent recorder for S2T.

This module provides a recorder that runs without any GUI or notifications.
"""

import argparse
import logging
import os
import shutil
import signal
import sys
import threading
import time
import warnings
from typing import Any

# Suppress all warnings
warnings.filterwarnings("ignore")

# Set up logging
logger = logging.getLogger(__name__)

# Disable logging
logging.disable(logging.CRITICAL)

# Import gi and set the required version
try:
    import gi

    gi.require_version("Gtk", "3.0")
    GUI_AVAILABLE = True
except (ImportError, ValueError):
    GUI_AVAILABLE = False

# Import our modules
from s2t.audio import AudioRecorder
from s2t.backends import get_backend
from s2t.config import DEFAULT_CONFIG_PATH, S2TConfig, load_config


class TrulySilentRecorder:
    """Records audio and transcribes it without any GUI or notifications."""

    def __init__(self, config: S2TConfig) -> None:
        """
        Initialize the recorder with the given configuration.

        Args:
            config: Configuration settings for the recorder
        """
        self.config = config
        self.recorder = AudioRecorder(config)
        self.backend = get_backend(config)
        self.is_recording = False
        self.stop_event = threading.Event()

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def start_recording(self) -> bool:
        """
        Start recording audio.

        Returns:
            bool: True if recording started successfully, False otherwise
        """
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

    def stop_recording(self) -> str | None:
        """
        Stop recording audio and return the path to the recorded file.

        Returns:
            str | None: Path to the recorded file, or None if recording failed
        """
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

    def transcribe(self, audio_file: str) -> str | None:
        """
        Transcribe the given audio file to text.

        Args:
            audio_file: Path to the audio file to transcribe

        Returns:
            str | None: Transcribed text, or None if transcription failed
        """
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

    def record_and_transcribe(self, duration: float | None = None) -> str | None:
        """
        Record audio for the specified duration and transcribe it.

        Args:
            duration: Optional recording duration in seconds

        Returns:
            str | None: Transcribed text, or None if recording or transcription failed
        """
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

    def _handle_interrupt(self, signum: int, frame: Any) -> None:
        """
        Handle interrupt signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        if self.is_recording:
            self.stop_recording()
        sys.exit(0)


def check_system_dependencies():
    """Check if required system dependencies are installed."""
    missing_deps = []

    # Check for libgirepository (required for all modes)
    try:
        # Instead of using subprocess to check for the gobject-introspection package,
        # we'll check if the required module can be imported directly, which is safer
        pkg_config_path = shutil.which("pkg-config")
        if pkg_config_path is None:
            missing_deps.append("pkg-config")
        else:
            # The gi module should be available if libgirepository is installed
            # We've already imported gi at the top of the file, so we can just check
            # if it's available
            if not GUI_AVAILABLE:
                missing_deps.append("libgirepository1.0-dev")
    except Exception:
        missing_deps.append("libgirepository1.0-dev")

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
    """Main entry point for the truly silent recorder."""
    # Only check dependencies if GUI is available
    if GUI_AVAILABLE:
        missing_deps = check_system_dependencies()
        if missing_deps:
            print_dependency_warning(missing_deps)
            logger.warning("Note: S2T can still run in minimal mode without these dependencies.")
    else:
        logger.info("Running in minimal mode without GUI dependencies.")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="S2T Truly Silent CLI")
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to config file (default: {DEFAULT_CONFIG_PATH}). Supported formats: YAML, JSON",
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

    # Redirect stderr to /dev/null to suppress ALSA warnings
    stderr_fd = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)

    try:
        # Environment variables loaded automatically

        # Load configuration
        config = load_config(args.config)

        # Check if API key is set in environment variables
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            # Set the API key in the Pydantic config
            config.backends.whisper_api.api_key = api_key

        # Create recorder
        recorder = TrulySilentRecorder(config)

        # Record and transcribe
        text = recorder.record_and_transcribe(duration=args.time)

        if text:
            # Output the transcription to stdout
            logger.info(text)
            return 0
        else:
            logger.error("Failed to transcribe audio")
            return 1

    finally:
        # Restore stderr
        os.dup2(stderr_fd, 2)
        os.close(stderr_fd)


if __name__ == "__main__":
    sys.exit(main())
