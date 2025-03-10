#!/usr/bin/env python3
"""
Tests for the truly_silent module.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import gi
import pytest

gi.require_version("Gtk", "4.0")

# Mock sys.argv before importing truly_silent
sys.argv = ["truly_silent"]

from s2t.truly_silent import TrulySilentRecorder


@pytest.fixture
def mock_config():
    """Return a mock configuration for testing."""
    return {
        "backends": {
            "whisper_api": {
                "api_key": "test_api_key",
                "model": "whisper-1",
                "language": "en",
            }
        },
        "silent_recorder": {
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


@patch("s2t.truly_silent.get_backend")
@patch("s2t.truly_silent.AudioRecorder")
def test_silent_recorder_init(mock_audio_recorder_class, mock_get_backend, mock_config):
    """Test TrulySilentRecorder initialization."""
    mock_audio_recorder_class.return_value = MagicMock()
    mock_get_backend.return_value = MagicMock()

    recorder = TrulySilentRecorder(mock_config)

    # Check that configuration values are properly set
    assert recorder.config == mock_config
    assert recorder.is_recording is False


@patch("s2t.truly_silent.get_backend")
@patch("s2t.truly_silent.AudioRecorder")
def test_start_recording(
    mock_audio_recorder_class,
    mock_get_backend,
    mock_config,
    mock_audio_recorder,
    mock_backend,
):
    """Test starting recording."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = TrulySilentRecorder(mock_config)

    result = recorder.start_recording()

    assert result is True
    assert recorder.is_recording is True
    assert mock_audio_recorder.start_recording.called


@patch("s2t.truly_silent.get_backend")
@patch("s2t.truly_silent.AudioRecorder")
def test_stop_recording(
    mock_audio_recorder_class,
    mock_get_backend,
    mock_config,
    mock_audio_recorder,
    mock_backend,
):
    """Test stopping recording."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = TrulySilentRecorder(mock_config)
    recorder.is_recording = True
    recorder.recorder = mock_audio_recorder

    audio_file = recorder.stop_recording()

    assert recorder.is_recording is False
    assert mock_audio_recorder.stop_recording.called
    assert audio_file == mock_audio_recorder.stop_recording.return_value


@patch("s2t.truly_silent.get_backend")
@patch("s2t.truly_silent.AudioRecorder")
def test_transcribe(
    mock_audio_recorder_class,
    mock_get_backend,
    mock_config,
    mock_audio_recorder,
    mock_backend,
):
    """Test transcription."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    recorder = TrulySilentRecorder(mock_config)

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


@patch("s2t.truly_silent.get_backend")
@patch("s2t.truly_silent.AudioRecorder")
@patch("builtins.input", side_effect=KeyboardInterrupt)
def test_record_and_transcribe(
    mock_input,
    mock_audio_recorder_class,
    mock_get_backend,
    mock_config,
    mock_audio_recorder,
    mock_backend,
):
    """Test record and transcribe functionality."""
    mock_audio_recorder_class.return_value = mock_audio_recorder
    mock_get_backend.return_value = mock_backend

    # Create a recorder with mocked components
    recorder = TrulySilentRecorder(mock_config)
    recorder.recorder = mock_audio_recorder

    # Mock the start_recording method
    recorder.start_recording = MagicMock(return_value=True)

    # Mock the stop_recording method
    recorder.stop_recording = MagicMock(
        return_value=mock_audio_recorder.stop_recording.return_value
    )

    # Mock the transcribe method
    recorder.transcribe = MagicMock(return_value="This is a test transcription")

    # Call the method under test with a duration to avoid waiting for input
    text = recorder.record_and_transcribe(duration=0.1)

    # Verify the results
    assert recorder.start_recording.called
    assert recorder.stop_recording.called
    assert recorder.transcribe.called
    assert text == "This is a test transcription"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
