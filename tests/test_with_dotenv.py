#!/usr/bin/env python3
"""
Test script that loads the OpenAI API key from a .env file and tests the transcription functionality.
"""

import os
import sys
import time
import logging
from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test audio recording and transcription with API key from .env file."""
    # Load environment variables from .env file
    if not load_dotenv():
        logger.warning("Failed to load .env file, checking for existing API key...")

    # Check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        logger.error("Please create a .env file with your API key: OPENAI_API_KEY=your-api-key")
        return 1
    else:
        logger.info("OpenAI API key found in environment variables")

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Set the API key in the config
    config["backends"]["whisper_api"]["api_key"] = api_key

    # Initialize components
    recorder = AudioRecorder(config)
    backend = get_backend(config)

    # Check if backend is available
    if not backend.is_available():
        logger.error("Speech-to-text backend is not available")
        return 1
    else:
        logger.info("Speech-to-text backend is available")

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
