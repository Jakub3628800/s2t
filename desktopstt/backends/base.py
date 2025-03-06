"""
Base class for speech-to-text backends.
"""

import abc
import logging

logger = logging.getLogger(__name__)

class STTBackend(abc.ABC):
    """Abstract base class for speech-to-text backends."""

    def __init__(self, config):
        """
        Initialize the STT backend with the given configuration.

        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.name = "base"

    @abc.abstractmethod
    def transcribe(self, audio_file_path):
        """
        Transcribe the given audio file to text.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            A dictionary containing the transcription results:
            {
                'text': str,  # The transcribed text
                'language': str,  # The detected language (if available)
                'segments': list,  # List of segments with timestamps (if available)
                'duration': float,  # Duration of the audio in seconds
            }
        """
        pass

    @abc.abstractmethod
    def is_available(self):
        """
        Check if the backend is available and properly configured.

        Returns:
            bool: True if the backend is available, False otherwise
        """
        pass

    def get_name(self):
        """
        Get the name of the backend.

        Returns:
            str: The name of the backend
        """
        return self.name
