#!/usr/bin/env python3
"""
Simple test for the audio module.
"""

import os
import sys
import tempfile
import unittest.mock as mock
import pyaudio  # Add import for pyaudio

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktopstt.audio.recorder import AudioRecorder

def test_audio_recorder_init():
    """Test that the AudioRecorder initializes correctly."""
    # Create a simple config
    config = {
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'chunk_size': 1024,
            'device_index': None
        }
    }

    try:
        # Initialize the recorder
        recorder = AudioRecorder(config)

        # Check that the recorder has the correct attributes
        assert recorder.sample_rate == 16000, f"recorder.sample_rate is {recorder.sample_rate}, expected 16000"
        assert recorder.channels == 1, f"recorder.channels is {recorder.channels}, expected 1"
        assert recorder.chunk_size == 1024, f"recorder.chunk_size is {recorder.chunk_size}, expected 1024"
        assert recorder.format == pyaudio.paInt16, f"recorder.format is {recorder.format}, expected pyaudio.paInt16"
        assert recorder.device_index is None, f"recorder.device_index is {recorder.device_index}, expected None"

        print("test_audio_recorder_init: PASSED")
    except AssertionError as e:
        print(f"test_audio_recorder_init: FAILED - {e}")

def test_audio_recorder_start_stop():
    """Test that the AudioRecorder start_recording and stop_recording methods work correctly."""
    # Create a simple config
    config = {
        'audio': {
            'sample_rate': 16000,
            'channels': 1,
            'chunk_size': 1024,
            'device_index': None
        }
    }

    try:
        # Initialize the recorder
        recorder = AudioRecorder(config)

        # Mock the _record_thread method to avoid actually recording
        recorder._record_thread = mock.MagicMock()

        # Mock the _save_to_temp_file method to return a fake file path
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        recorder._save_to_temp_file = mock.MagicMock(return_value=temp_file.name)

        # Start recording
        result = recorder.start_recording()

        # Check that start_recording returned True
        assert result is True, f"recorder.start_recording() returned {result}, expected True"

        # Check that _record_thread was called
        assert recorder._record_thread.called, "recorder._record_thread was not called"

        # Stop recording
        audio_file = recorder.stop_recording()

        # Check that stop_recording returned a file path
        assert audio_file == temp_file.name, f"recorder.stop_recording() returned {audio_file}, expected {temp_file.name}"

        # Check that _save_to_temp_file was called
        assert recorder._save_to_temp_file.called, "recorder._save_to_temp_file was not called"

        # Clean up
        os.unlink(temp_file.name)

        print("test_audio_recorder_start_stop: PASSED")
    except AssertionError as e:
        print(f"test_audio_recorder_start_stop: FAILED - {e}")
    except Exception as e:
        print(f"test_audio_recorder_start_stop: ERROR - {e}")

if __name__ == "__main__":
    print("Running audio tests...")
    test_audio_recorder_init()
    test_audio_recorder_start_stop()
    print("All tests completed.")
