#!/usr/bin/env python3
"""
Tests for the audio recording functionality.
"""

import logging
import sys
import time

from s2t.audio import AudioRecorder
from s2t.config import DEFAULT_CONFIG_PATH, load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Test audio recording."""
    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Initialize recorder
    recorder = AudioRecorder(config)

    # Start recording
    logger.info("Starting recording...")
    if not recorder.start_recording():
        logger.error("Failed to start recording")
        return 1

    # Record for 5 seconds
    logger.info("Recording for 5 seconds...")
    time.sleep(5)

    # Stop recording
    logger.info("Stopping recording...")
    audio_file = recorder.stop_recording()

    if not audio_file:
        logger.error("Failed to save recording")
        return 1

    logger.info(f"Saved recording to {audio_file}")
    logger.info(f"You can play it with: aplay {audio_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
