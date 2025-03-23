"""
OpenAI Whisper API backend for S2T.
"""

import logging
import os

import openai

from s2t.backends.base import STTBackend

logger = logging.getLogger(__name__)


class WhisperAPIBackend(STTBackend):
    """OpenAI Whisper API backend for speech-to-text conversion."""

    def __init__(self, config):
        """
        Initialize the Whisper API backend with the given configuration.

        Args:
            config: Application configuration (Pydantic model)
        """
        super().__init__(config)
        self.name = "whisper_api"

        # Get configuration from Pydantic model
        self.backend_config = config.backends.whisper_api
        api_key = self.backend_config.api_key
        self.model = self.backend_config.model
        self.language = self.backend_config.language
        self.temperature = self.backend_config.temperature
        self.response_format = self.backend_config.response_format

        # Try environment variable if no API key in config
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")

        self.api_key = api_key

        # Configure the OpenAI client
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("No API key provided for Whisper API backend")

    def transcribe(self, audio_file_path):
        """
        Transcribe the given audio file to text using the Whisper API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            A dictionary with the transcription result, or None if an error occurred
        """
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file not found: {audio_file_path}")
            return None

        if not self.client:
            logger.error("OpenAI client not initialized (missing API key?)")
            return None

        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")
            logger.debug(f"Using model: {self.model}, language: {self.language}")

            with open(audio_file_path, "rb") as audio_file:
                result = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=self.language,
                    temperature=self.temperature,
                    response_format=self.response_format,
                )

            # Handle different types of responses based on the response format
            if self.response_format == "json":
                text = result.text
            elif hasattr(result, "text"):
                text = result.text
            else:
                text = str(result)

            logger.info(f"Transcription successful: {len(text)} characters")
            return {"text": text}

        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None

    def is_available(self):
        """Check if the Whisper API backend is available."""
        return bool(self.api_key) and bool(self.client)
