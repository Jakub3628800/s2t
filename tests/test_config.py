"""
Tests for the configuration module.
"""

import os
import tempfile
import unittest
from desktopstt.config import load_config

class TestConfig(unittest.TestCase):
    """Tests for the configuration module."""

    def test_default_config(self):
        """Test that the default configuration is loaded correctly."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{}')  # Empty config
            config_path = f.name

        try:
            # Load the config
            config = load_config(config_path)

            # Check that the default values are set
            self.assertIn('backends', config)
            self.assertIn('whisper_api', config['backends'])
            self.assertIn('api_key', config['backends']['whisper_api'])

            # Check audio settings
            self.assertIn('audio', config)
            self.assertEqual(config['audio']['sample_rate'], 16000)
        finally:
            # Clean up
            os.unlink(config_path)

    def test_merge_config(self):
        """Test that user configuration is merged with defaults."""
        # Create a temporary config file with custom settings
        custom_config = {
            'audio': {
                'sample_rate': 44100
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            import yaml
            yaml.dump(custom_config, f)
            config_path = f.name

        try:
            # Load the config
            config = load_config(config_path)

            # Check that the custom value is used
            self.assertEqual(config['audio']['sample_rate'], 44100)

            # Check that default values for other settings are still present
            self.assertIn('backends', config)
            self.assertIn('whisper_api', config['backends'])
        finally:
            # Clean up
            os.unlink(config_path)

if __name__ == "__main__":
    unittest.main()
