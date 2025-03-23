"""
Tests for the configuration module.
"""

import json
import os
import tempfile
import unittest

from s2t.config import S2TConfig, load_config


class TestConfig(unittest.TestCase):
    """Tests for the configuration module."""

    def test_default_config(self):
        """Test that the default configuration is loaded correctly."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{}")  # Empty config
            config_path = f.name

        try:
            # Load the config
            config = load_config(config_path)

            # Check that the config is a Pydantic model
            self.assertIsInstance(config, S2TConfig)

            # Check that default values are set
            self.assertEqual(config.backends.default, "whisper_api")
            self.assertEqual(config.backends.whisper_api.api_key, "")

            # Check audio settings
            self.assertEqual(config.audio.sample_rate, 16000)
        finally:
            # Clean up
            os.unlink(config_path)

    def test_custom_config(self):
        """Test that user configuration values are properly loaded."""
        # Create a temporary config file with custom settings
        custom_config = {"audio": {"sample_rate": 44100}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(custom_config, f)
            config_path = f.name

        try:
            # Load the config
            config = load_config(config_path)

            # Check that the config is a Pydantic model
            self.assertIsInstance(config, S2TConfig)

            # Check that the custom value is used
            self.assertEqual(config.audio.sample_rate, 44100)

            # Check that default values for other settings are still present
            self.assertEqual(config.backends.default, "whisper_api")
        finally:
            # Clean up
            os.unlink(config_path)


if __name__ == "__main__":
    unittest.main()
