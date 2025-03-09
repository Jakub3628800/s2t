#!/usr/bin/env python3
"""
Tests for the popup recorder module.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Mock sys.argv before importing popup_recorder
sys.argv = ["popup_recorder"]

import gi

gi.require_version("Gtk", "4.0")

from s2t.popup_recorder import PopupRecorder


@pytest.fixture
def mock_config():
    """Return a mock configuration for testing."""
    return {
        "backends": {
            "whisper_api": {"api_key": "test_api_key", "model": "whisper-1", "language": "en"}
        },
        "popup_recorder": {
            "vad_enabled": True,
            "silence_threshold": 0.1,
            "silence_duration": 2.0,
            "min_recording_time": 1.0,
        },
    }


@pytest.fixture
def mock_backend():
    """Return a mock backend for testing."""
    backend = MagicMock()
    backend.is_available.return_value = True
    backend.transcribe.return_value = {"text": "This is a test transcription"}
    return backend


@pytest.fixture
def mock_audio_recorder():
    """Return a mock audio recorder for testing."""
    recorder = MagicMock()
    recorder.start_recording.return_value = True

    # Create a temporary file for the recording
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()

    recorder.stop_recording.return_value = temp_file.name
    return recorder


@patch("s2t.popup_recorder.get_backend")
@patch("s2t.popup_recorder.AudioRecorder")
def test_popup_recorder_init(mock_audio_recorder_class, mock_get_backend, mock_config):
    """Test PopupRecorder initialization."""
    mock_audio_recorder_class.return_value = MagicMock()
    mock_get_backend.return_value = MagicMock()

    recorder = PopupRecorder(mock_config)

    assert recorder.vad_enabled == mock_config["popup_recorder"]["vad_enabled"]
    assert recorder.silence_threshold == mock_config["popup_recorder"]["silence_threshold"]
    assert recorder.silence_duration == mock_config["popup_recorder"]["silence_duration"]
    assert recorder.min_recording_time == mock_config["popup_recorder"]["min_recording_time"]
    assert recorder.is_recording is False
    assert recorder.window is None


@patch("s2t.popup_recorder.get_backend")
@patch("s2t.popup_recorder.AudioRecorder")
def test_start_recording(
    mock_audio_recorder_class, mock_get_backend, mock_config, mock_audio_recorder, mock_backend
):
    """Test starting recording."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = PopupRecorder(mock_config)

    # Mock the _show_window method to avoid GTK issues in tests
    recorder._show_window = MagicMock()

    result = recorder.start_recording()

    assert result is True
    assert recorder.is_recording is True
    assert mock_audio_recorder.start_recording.called
    assert recorder._show_window.called


@patch("s2t.popup_recorder.get_backend")
@patch("s2t.popup_recorder.AudioRecorder")
def test_stop_recording(
    mock_audio_recorder_class, mock_get_backend, mock_config, mock_audio_recorder, mock_backend
):
    """Test stopping recording."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = PopupRecorder(mock_config)
    recorder.is_recording = True

    audio_file = recorder.stop_recording()

    assert recorder.is_recording is False
    assert mock_audio_recorder.stop_recording.called
    assert audio_file == mock_audio_recorder.stop_recording.return_value


@patch("s2t.popup_recorder.get_backend")
@patch("s2t.popup_recorder.AudioRecorder")
def test_transcribe(
    mock_audio_recorder_class, mock_get_backend, mock_config, mock_audio_recorder, mock_backend
):
    """Test transcription."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = PopupRecorder(mock_config)

    # Create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()

    try:
        text = recorder.transcribe(temp_file.name)

        assert text == "This is a test transcription"
        assert mock_backend.transcribe.called
        assert mock_backend.transcribe.call_args[0][0] == temp_file.name
    finally:
        # Clean up the temporary file
        os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
