#!/usr/bin/env python3
"""
Simple tests for the configuration module.
"""

import json
import logging
import os
import sys
import tempfile

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from s2t.config import S2TConfig, load_config

# Setup logger
logger = logging.getLogger(__name__)


def verify_default_config_values(config):
    """Verify that the default config values exist."""
    # Check that essential sections exist
    assert hasattr(config, "audio")
    assert hasattr(config, "ui")
    assert hasattr(config, "backends")
    assert hasattr(config, "output")
    assert hasattr(config, "popup_recorder")


def test_default_config():
    """Test that the default configuration is loaded correctly."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("{}")  # Empty config
        config_path = f.name

    try:
        # Load the config
        config = load_config(config_path)
        assert config is not None
        assert isinstance(config, S2TConfig)

        verify_default_config_values(config)

        logger.info("test_default_config: PASSED")
    except Exception as e:
        logger.error(f"test_default_config: FAILED - {e}")
        raise
    finally:
        # Clean up
        os.unlink(config_path)


def test_merge_config():
    """Test that user configuration is merged with defaults."""
    # Create a temporary config file with custom settings
    custom_config = {"audio": {"sample_rate": 44100}}

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        json.dump(custom_config, f)
        config_path = f.name

    try:
        # Load the config
        config = load_config(config_path)
        assert config is not None
        assert isinstance(config, S2TConfig)

        # Check that the merged config has our custom values
        assert config.audio.sample_rate == 44100

        logger.info("test_merge_config: PASSED")
    except Exception as e:
        logger.error(f"test_merge_config: FAILED - {e}")
        raise
    finally:
        # Clean up
        os.unlink(config_path)


if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    logger.info("Running configuration tests...")
    test_default_config()
    test_merge_config()
    logger.info("All tests completed.")
