#!/usr/bin/env python3
"""
Tests for the convenience scripts.
"""

import os
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock

# Mock sys.argv before importing any modules
sys.argv = ['test_convenience_scripts']


def test_popup_silent_script_exists():
    """Test that the popup silent script exists."""
    assert os.path.exists("desktopstt-popup-silent.sh")
    assert os.access("desktopstt-popup-silent.sh", os.X_OK)


def test_silent_script_exists():
    """Test that the silent script exists."""
    assert os.path.exists("desktopstt-silent.sh")
    assert os.access("desktopstt-silent.sh", os.X_OK)


@patch("subprocess.run")
def test_popup_silent_script_content(mock_run):
    """Test that the popup silent script contains the expected content."""
    # Read the script content
    with open("desktopstt-popup-silent.sh", "r") as f:
        content = f.read()

    # Check for key components
    assert "popup_recorder_immediate.py" in content
    assert "ImmediateRecordingWindow" in content
    assert "ImmediatePopupRecorder" in content
    assert "silence_threshold" in content
    assert "silence_duration" in content
    assert "min_recording_time" in content  # Just check for the variable name
    assert "wtype" in content


@patch("subprocess.run")
def test_silent_script_content(mock_run):
    """Test that the silent script contains the expected content."""
    # Read the script content
    with open("desktopstt-silent.sh", "r") as f:
        content = f.read()

    # Check for key components
    assert "silent_recorder.py" in content  # Check for the script name
    assert "SilentRecorder" in content
    assert "silence_threshold" in content
    assert "silence_duration" in content
    assert "wtype" in content


@patch("subprocess.Popen")
def test_popup_silent_script_execution(mock_popen):
    """Test that the popup silent script can be executed."""
    # Mock the Popen return value
    process_mock = MagicMock()
    process_mock.returncode = 0
    mock_popen.return_value = process_mock

    # Try to execute the script (without actually running it)
    try:
        # Just check if the script is executable
        assert os.access("desktopstt-popup-silent.sh", os.X_OK)
    except Exception as e:
        pytest.fail(f"Failed to execute popup silent script: {e}")


@patch("subprocess.Popen")
def test_silent_script_execution(mock_popen):
    """Test that the silent script can be executed."""
    # Mock the Popen return value
    process_mock = MagicMock()
    process_mock.returncode = 0
    mock_popen.return_value = process_mock

    # Try to execute the script (without actually running it)
    try:
        # Just check if the script is executable
        assert os.access("desktopstt-silent.sh", os.X_OK)
    except Exception as e:
        pytest.fail(f"Failed to execute silent script: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
