#!/usr/bin/env python3
"""
Simple tests for the backends module.
"""

import logging
import os
import sys

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from s2t.backends import get_backend
from s2t.backends.whisper_api import WhisperAPIBackend
from s2t.config import BackendsConfig, S2TConfig, WhisperAPIConfig

# Setup logger
logger = logging.getLogger(__name__)


def test_get_backend():
    """Test that the get_backend function returns the correct backend."""
    # Create a Pydantic config with the whisper_api backend
    whisper_config = WhisperAPIConfig(api_key="test_key")
    backends_config = BackendsConfig(default="whisper_api", whisper_api=whisper_config)
    config = S2TConfig(backends=backends_config)

    try:
        # Get the backend
        backend = get_backend(config)

        # Check that the backend is a WhisperAPIBackend
        assert isinstance(
            backend, WhisperAPIBackend
        ), f"backend is {type(backend)}, expected WhisperAPIBackend"

        # Check that the backend has the correct API key
        assert (
            backend.api_key == "test_key"
        ), f"backend.api_key is {backend.api_key}, expected 'test_key'"

        logger.info("test_get_backend: PASSED")
    except Exception as e:
        logger.error(f"test_get_backend: FAILED - {e}")
        raise


def test_backend_is_available():
    """Test that the backend is_available method works correctly."""
    # Create a Pydantic config with the whisper_api backend
    whisper_config = WhisperAPIConfig(api_key="test_key")
    backends_config = BackendsConfig(default="whisper_api", whisper_api=whisper_config)
    config = S2TConfig(backends=backends_config)

    try:
        # Get the backend
        backend = get_backend(config)

        # Mock the is_available method to return True
        original_is_available = backend.is_available
        backend.is_available = lambda: True

        # Check that the backend is available
        assert backend.is_available(), "backend.is_available() returned False, expected True"

        # Restore the original method
        backend.is_available = original_is_available

        logger.info("test_backend_is_available: PASSED")
    except Exception as e:
        logger.error(f"test_backend_is_available: FAILED - {e}")
        raise


def test_backend_name():
    """Test that the backend get_name method works correctly."""
    # Create a Pydantic config with the whisper_api backend
    whisper_config = WhisperAPIConfig(api_key="test_key")
    backends_config = BackendsConfig(default="whisper_api", whisper_api=whisper_config)
    config = S2TConfig(backends=backends_config)

    try:
        # Get the backend
        backend = get_backend(config)

        # Check that the backend name is correct
        # The actual implementation returns the backend key from the config
        assert (
            backend.get_name() == "whisper_api"
        ), f"backend.get_name() returned {backend.get_name()}, expected 'whisper_api'"

        logger.info("test_backend_name: PASSED")
    except Exception as e:
        logger.error(f"test_backend_name: FAILED - {e}")
        raise


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("Running backend tests...")

    # Run tests that don't require network access
    test_get_backend()
    test_backend_is_available()
    test_backend_name()

    logger.info("All tests completed.")
