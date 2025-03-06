#!/usr/bin/env python3
"""
Script to find and transcribe previously recorded audio files.
"""

import os
import sys
import glob
import logging
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_wav_files(directory="/tmp"):
    """Find WAV files in the specified directory."""
    pattern = os.path.join(directory, "desktopstt_recording_*.wav")
    files = glob.glob(pattern)
    files.sort(key=os.path.getmtime, reverse=True)  # Sort by modification time, newest first
    return files

def transcribe_file(audio_file, backend):
    """Transcribe a single audio file."""
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        return None

    try:
        logger.info(f"Transcribing audio file: {audio_file}")
        result = backend.transcribe(audio_file)
        text = result.get('text', '')

        if not text:
            logger.error("No transcription result")
            return None

        logger.info(f"Transcription successful: {len(text)} characters")
        logger.info(f"Transcription: {text}")
        return text

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def main():
    """Find and transcribe previously recorded audio files."""
    # Load environment variables from .env file
    if load_dotenv():
        logger.info("Loaded environment variables from .env file")

    # Check if API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        logger.error("Please create a .env file with your API key: OPENAI_API_KEY=your-api-key")
        return 1
    else:
        logger.info("OpenAI API key found in environment variables")
        logger.info(f"API key length: {len(api_key)}")

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Set the API key in the config
    config["backends"]["whisper_api"]["api_key"] = api_key

    # Initialize backend
    backend = get_backend(config)

    # Check if backend is available
    if not backend.is_available():
        logger.error("Speech-to-text backend is not available")
        return 1
    else:
        logger.info("Speech-to-text backend is available")

    # Find WAV files
    wav_files = find_wav_files()
    if not wav_files:
        logger.error("No WAV files found")
        return 1

    logger.info(f"Found {len(wav_files)} WAV files")

    # Transcribe the most recent file
    recent_file = wav_files[0]
    logger.info(f"Transcribing most recent file: {recent_file}")

    text = transcribe_file(recent_file, backend)
    if text:
        print(f"Transcription of {os.path.basename(recent_file)}:")
        print("-" * 40)
        print(text)
        print("-" * 40)
        return 0
    else:
        logger.error("Failed to transcribe audio")
        return 1

if __name__ == "__main__":
    sys.exit(main())
