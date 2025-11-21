"""Basic tests for s2t module."""

import sys
from unittest.mock import MagicMock, patch

# Mock external dependencies before import
sys.modules['pywhispercpp'] = MagicMock()
sys.modules['pywhispercpp.model'] = MagicMock()
sys.modules['pyaudio'] = MagicMock()

import s2t


def test_imports():
    """Test that the main module can be imported."""
    assert hasattr(s2t, 'AudioRecorder')
    assert hasattr(s2t, 'WhisperTranscriber')
    assert hasattr(s2t, 'process_transcription')


def test_logger_configuration():
    """Test that logger is properly configured."""
    assert s2t.logger is not None
    assert s2t.logger.name == 's2t'


def test_global_variables_exist():
    """Test that global variables are defined."""
    assert hasattr(s2t, 'IS_RECORDING')
    assert hasattr(s2t, 'FRAMES')
    assert hasattr(s2t, 'STREAM')
    assert hasattr(s2t, 'RECORDER')
    assert hasattr(s2t, 'TRANSCRIBER')
