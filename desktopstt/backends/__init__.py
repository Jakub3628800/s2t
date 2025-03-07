"""
Speech-to-text backend interfaces for DesktopSTT.
"""

from desktopstt.backends.base import STTBackend
from desktopstt.backends.whisper_api import WhisperAPIBackend

__all__ = ["STTBackend", "WhisperAPIBackend", "get_backend"]


def get_backend(config):
    """
    Get the appropriate STT backend based on configuration.

    Args:
        config: Application configuration dictionary

    Returns:
        An instance of the configured STT backend
    """
    backend_name = config["backends"]["default"]

    if backend_name == "whisper_api":
        return WhisperAPIBackend(config)

    # Add more backends here as they are implemented

    raise ValueError(f"Unknown backend: {backend_name}")
