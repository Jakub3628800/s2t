#!/usr/bin/env python3
"""
Tests for the convenience scripts.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock sys.argv before importing any modules
sys.argv = ["test_convenience_scripts"]


def test_popup_silent_script_exists():
    """Test that the popup silent script exists."""
    assert os.path.exists("s2t-popup-silent.sh")
    assert os.access("s2t-popup-silent.sh", os.X_OK)


def test_silent_script_exists():
    """Test that the silent script exists."""
    assert os.path.exists("s2t-silent.sh")
    assert os.access("s2t-silent.sh", os.X_OK)


@patch("subprocess.run")
def test_popup_silent_script_content(mock_run):
    """Test that the popup silent script contains the expected content."""
    # Read the script content
    with open("s2t-popup-silent.sh") as f:
        content = f.read()

    # Check for key components
    assert "#!/bin/bash" in content
    assert "s2t.immediate_popup" in content
    assert "wtype" in content


@patch("subprocess.run")
def test_silent_script_content(mock_run):
    """Test that the silent script contains the expected content."""
    # Read the script content
    with open("s2t-silent.sh") as f:
        content = f.read()

    # Check for key components
    assert "#!/bin/bash" in content
    assert "s2t.headless_recorder" in content
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
        assert os.access("s2t-popup-silent.sh", os.X_OK)
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
        assert os.access("s2t-silent.sh", os.X_OK)
    except Exception as e:
        pytest.fail(f"Failed to execute silent script: {e}")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
