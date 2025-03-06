#!/usr/bin/env python3
"""
Simple script to test audio recording and transcription.
"""

import os
import sys
import time
import logging
from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test audio recording and transcription."""
    # Check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY environment variable is not set")
        logger.warning("You can set it with: export OPENAI_API_KEY='your-api-key'")
        logger.warning("Or edit the config file: ~/.config/desktopstt/config.yaml")

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Check if API key is in config
    if not config["backends"]["whisper_api"]["api_key"] and not api_key:
        logger.error("No OpenAI API key found in config or environment variables")
        logger.error("Please set your API key and try again")
        return 1

    # Initialize components
    recorder = AudioRecorder(config)
    backend = get_backend(config)

    # Check if backend is available
    if not backend.is_available():
        logger.error("Speech-to-text backend is not available")
        return 1

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

    # Transcribe the audio
    logger.info("Transcribing audio...")
    try:
        result = backend.transcribe(audio_file)
        text = result.get('text', '')

        if not text:
            logger.error("No transcription result")
            return 1

        logger.info(f"Transcription successful: {len(text)} characters")
        logger.info(f"Transcription: {text}")
        return 0

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
