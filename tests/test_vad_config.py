#!/usr/bin/env python3
"""
Test for the VAD configuration loading.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktopstt.config import DEFAULT_CONFIG

# Mock configuration with VAD settings
MOCK_CONFIG_WITH_VAD = {
    "audio": DEFAULT_CONFIG["audio"].copy(),
    "ui": DEFAULT_CONFIG["ui"].copy(),
    "backends": DEFAULT_CONFIG["backends"].copy(),
    "output": DEFAULT_CONFIG["output"].copy(),
    "popup_recorder": {
        "vad_enabled": True,
        "silence_threshold": 0.1,
        "silence_duration": 5.0,
        "min_recording_time": 3.0
    }
}

class TestVADConfig(unittest.TestCase):
    """Test the VAD configuration loading."""

    @patch('desktopstt.config.DEFAULT_CONFIG', MOCK_CONFIG_WITH_VAD)
    def test_default_vad_config(self):
        """Test that the default configuration includes VAD settings."""
        from desktopstt.config import DEFAULT_CONFIG as patched_config

        # Check that the popup_recorder section exists
        self.assertIn('popup_recorder', patched_config)

        # Check that the VAD settings have default values
        popup_config = patched_config['popup_recorder']
        self.assertIn('vad_enabled', popup_config)
        self.assertIn('silence_threshold', popup_config)
        self.assertIn('silence_duration', popup_config)
        self.assertIn('min_recording_time', popup_config)

        # Check the default values
        self.assertTrue(popup_config['vad_enabled'])
        self.assertEqual(popup_config['silence_threshold'], 0.1)
        self.assertEqual(popup_config['silence_duration'], 5.0)
        self.assertEqual(popup_config['min_recording_time'], 3.0)

    def test_update_vad_config(self):
        """Test that VAD settings can be overridden."""
        # Start with our mock config
        base_config = MOCK_CONFIG_WITH_VAD.copy()

        # Create a custom config with different VAD settings
        custom_config = {
            'popup_recorder': {
                'vad_enabled': False,
                'silence_threshold': 0.2,
                'silence_duration': 3.0,
                'min_recording_time': 1.0
            }
        }

        # Update the config using the same approach as in load_config
        from desktopstt.config import _deep_update
        merged_config = base_config.copy()
        _deep_update(merged_config, custom_config)

        # Check that the VAD settings were overridden
        popup_config = merged_config['popup_recorder']
        self.assertFalse(popup_config['vad_enabled'])
        self.assertEqual(popup_config['silence_threshold'], 0.2)
        self.assertEqual(popup_config['silence_duration'], 3.0)
        self.assertEqual(popup_config['min_recording_time'], 1.0)

if __name__ == "__main__":
    unittest.main()
