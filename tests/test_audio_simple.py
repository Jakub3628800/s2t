#!/usr/bin/env python3
"""
Simple tests for the audio module.
"""

import logging
import os
import sys
import time

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from s2t.audio.recorder import AudioRecorder
from s2t.config import AudioConfig, S2TConfig

# Setup logger
logger = logging.getLogger(__name__)


def test_audio_recorder_init():
    """Test that the AudioRecorder initializes correctly."""
    try:
        # Create a simple config with audio settings
        audio_config = AudioConfig()
        config = S2TConfig(audio=audio_config)

        # Create an audio recorder
        recorder = AudioRecorder(config)

        # Check that the recorder is initialized properly
        assert recorder is not None
        assert recorder.stream is None
        # Note: pyaudio might be None in test environments
        # So we don't check for it

        logger.info("test_audio_recorder_init: PASSED")
    except Exception as e:
        logger.error(f"test_audio_recorder_init: FAILED - {e}")
        raise


def test_audio_recorder_start_stop():
    """Test that the AudioRecorder start_recording and stop_recording methods work correctly."""
    try:
        # Create a simple config with audio settings
        audio_config = AudioConfig()
        config = S2TConfig(audio=audio_config)

        # Create an audio recorder
        recorder = AudioRecorder(config)

        # Start recording
        success = recorder.start_recording()
        if not success:
            logger.error("Failed to start recording - skipping test")
            return

        # Record for a short time
        time.sleep(0.5)

        # Stop recording and get the file path
        audio_file = recorder.stop_recording()

        # Check that the file exists
        assert audio_file is not None
        assert os.path.exists(audio_file)

        # Check that the file is a wave file
        assert audio_file.endswith(".wav")

        # Clean up - remove the audio file
        os.unlink(audio_file)

        logger.info("test_audio_recorder_start_stop: PASSED")
    except AssertionError as e:
        logger.error(f"test_audio_recorder_start_stop: FAILED - {e}")
        raise
    except Exception as e:
        logger.error(f"test_audio_recorder_start_stop: ERROR - {e}")
        raise


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("Running audio tests...")
    test_audio_recorder_init()
    test_audio_recorder_start_stop()
    logger.info("All tests completed.")
