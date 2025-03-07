"""
OpenAI Whisper API backend for speech-to-text conversion.
"""

import logging
import os

import openai

from desktopstt.backends.base import STTBackend

logger = logging.getLogger(__name__)


class WhisperAPIBackend(STTBackend):
    """OpenAI Whisper API backend for speech-to-text conversion."""

    def __init__(self, config):
        """
        Initialize the Whisper API backend with the given configuration.

        Args:
            config: Application configuration dictionary
        """
        super().__init__(config)
        self.name = "whisper_api"
        self.backend_config = config["backends"]["whisper_api"]

        # Set API key from config or environment variable
        api_key = self.backend_config.get("api_key", "")
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY", "")

        self.api_key = api_key
        self.model = self.backend_config.get("model", "whisper-1")
        self.language = self.backend_config.get("language", "en")

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
            A dictionary containing the transcription results:
            {
                'text': str,  # The transcribed text
                'language': str,  # The detected language
                'segments': list,  # List of segments with timestamps
                'duration': float,  # Duration of the audio in seconds
            }
        """
        if not self.is_available():
            raise ValueError("Whisper API backend is not available")

        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            logger.info(f"Transcribing audio file: {audio_file_path}")

            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    language=self.language if self.language else None,
                    response_format="verbose_json",
                )

            # Extract the transcription results
            result = {
                "text": response.text,
                "language": response.language,
                "segments": response.segments,
                "duration": response.duration,
            }

            logger.info(f"Transcription successful: {len(result['text'])} characters")
            return result

        except Exception as e:
            logger.error(f"Error transcribing audio with Whisper API: {e}")
            return {
                "text": f"Error: {str(e)}",
                "language": self.language,
                "segments": [],
                "duration": 0.0,
            }

    def is_available(self):
        """
        Check if the Whisper API backend is available and properly configured.

        Returns:
            bool: True if the backend is available, False otherwise
        """
        return bool(self.api_key and self.client)
