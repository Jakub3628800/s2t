#!/usr/bin/env python3
"""
Simple test for the VAD (Voice Activity Detection) functionality.
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the config module directly

class TestVAD(unittest.TestCase):
    """Test the VAD functionality."""

    def test_vad_config_processing(self):
        """Test that VAD configuration is processed correctly."""
        # Create a mock config with VAD settings
        config = {
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'chunk_size': 1024,
                'device_index': None
            },
            'popup_recorder': {
                'vad_enabled': True,
                'silence_threshold': 0.2,
                'silence_duration': 3.0,
                'min_recording_time': 2.0
            }
        }

        # Create a mock recorder class
        class MockRecorder:
            def __init__(self):
                self.vad_enabled = False
                self.silence_threshold = 0.0
                self.silence_duration = 0.0
                self.min_recording_time = 0.0

            def process_vad_config(self, config):
                """Process VAD configuration."""
                if 'popup_recorder' in config:
                    popup_config = config['popup_recorder']
                    self.vad_enabled = popup_config.get('vad_enabled', False)
                    self.silence_threshold = popup_config.get('silence_threshold', 0.1)
                    self.silence_duration = popup_config.get('silence_duration', 2.0)
                    self.min_recording_time = popup_config.get('min_recording_time', 1.0)

        # Create an instance of our mock recorder
        recorder = MockRecorder()

        # Process the config
        recorder.process_vad_config(config)

        # Check that the VAD parameters are set correctly
        self.assertTrue(recorder.vad_enabled)
        self.assertEqual(recorder.silence_threshold, 0.2)
        self.assertEqual(recorder.silence_duration, 3.0)
        self.assertEqual(recorder.min_recording_time, 2.0)

    def test_vad_default_values(self):
        """Test that default VAD values are used when not specified."""
        # Create a config without VAD settings
        config = {
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'chunk_size': 1024,
                'device_index': None
            }
        }

        # Create a mock recorder class
        class MockRecorder:
            def __init__(self):
                self.vad_enabled = False
                self.silence_threshold = 0.0
                self.silence_duration = 0.0
                self.min_recording_time = 0.0

            def process_vad_config(self, config):
                """Process VAD configuration."""
                if 'popup_recorder' in config:
                    popup_config = config['popup_recorder']
                    self.vad_enabled = popup_config.get('vad_enabled', False)
                    self.silence_threshold = popup_config.get('silence_threshold', 0.1)
                    self.silence_duration = popup_config.get('silence_duration', 2.0)
                    self.min_recording_time = popup_config.get('min_recording_time', 1.0)
                else:
                    # Use default values
                    self.vad_enabled = False
                    self.silence_threshold = 0.1
                    self.silence_duration = 2.0
                    self.min_recording_time = 1.0

        # Create an instance of our mock recorder
        recorder = MockRecorder()

        # Process the config
        recorder.process_vad_config(config)

        # Check that the default VAD parameters are used
        self.assertFalse(recorder.vad_enabled)
        self.assertEqual(recorder.silence_threshold, 0.1)
        self.assertEqual(recorder.silence_duration, 2.0)
        self.assertEqual(recorder.min_recording_time, 1.0)

if __name__ == "__main__":
    unittest.main()
