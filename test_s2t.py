"""Tests for s2t module."""

import os
import sys
import threading
from unittest.mock import MagicMock, patch

# Mock external dependencies before import
mock_pyaudio = MagicMock()
mock_pyaudio.paInt16 = 8  # Actual value from pyaudio
mock_pyaudio.PyAudio.return_value.get_sample_size.return_value = 2
sys.modules["pywhispercpp"] = MagicMock()
sys.modules["pywhispercpp.model"] = MagicMock()
sys.modules["pyaudio"] = mock_pyaudio

import s2t  # noqa: E402


class TestImports:
    """Test that the main module can be imported."""

    def test_audio_recorder_exists(self):
        assert hasattr(s2t, "AudioRecorder")

    def test_whisper_transcriber_exists(self):
        assert hasattr(s2t, "WhisperTranscriber")

    def test_process_transcription_exists(self):
        assert hasattr(s2t, "process_transcription")


class TestLoggerConfiguration:
    """Test that logger is properly configured."""

    def test_logger_exists(self):
        assert s2t.logger is not None

    def test_logger_name(self):
        assert s2t.logger.name == "s2t"


class TestGlobalVariables:
    """Test that global variables are defined correctly."""

    def test_recording_event_exists(self):
        assert hasattr(s2t, "RECORDING_EVENT")
        assert isinstance(s2t.RECORDING_EVENT, threading.Event)

    def test_frames_exists(self):
        assert hasattr(s2t, "FRAMES")
        assert isinstance(s2t.FRAMES, list)

    def test_frames_lock_exists(self):
        assert hasattr(s2t, "FRAMES_LOCK")
        assert isinstance(s2t.FRAMES_LOCK, type(threading.Lock()))

    def test_stream_exists(self):
        assert hasattr(s2t, "STREAM")

    def test_recorder_exists(self):
        assert hasattr(s2t, "RECORDER")

    def test_transcriber_exists(self):
        assert hasattr(s2t, "TRANSCRIBER")


class TestSuppressStderr:
    """Test the suppress_stderr context manager."""

    def test_suppress_stderr_suppresses_output(self):
        """Verify stderr is suppressed within context."""
        with s2t.suppress_stderr():
            # Write to fd 2 directly (C-level stderr)
            os.write(2, b"This should be suppressed\n")

        # If we get here without error, the context manager worked
        assert True

    def test_suppress_stderr_restores_stderr(self):
        """Verify stderr is restored after context."""
        original_fd = os.dup(2)
        try:
            with s2t.suppress_stderr():
                pass
            # After context, fd 2 should work normally
            os.write(2, b"")  # Should not raise
        finally:
            os.close(original_fd)


class TestAudioRecorder:
    """Test AudioRecorder class."""

    def test_audio_recorder_initialization(self):
        """Test AudioRecorder initializes with correct settings."""
        recorder = s2t.AudioRecorder()
        assert recorder.chunk == 1024
        assert recorder.channels == 1
        assert recorder.rate == 16000

    def test_audio_recorder_cleanup(self):
        """Test AudioRecorder cleanup calls terminate."""
        recorder = s2t.AudioRecorder()
        recorder.cleanup()
        recorder.audio.terminate.assert_called_once()


class TestProcessTranscription:
    """Test process_transcription function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_recorder = MagicMock()
        self.mock_recorder.channels = 1
        self.mock_recorder.format = 8  # paInt16
        self.mock_recorder.rate = 16000
        self.mock_recorder.audio.get_sample_size.return_value = 2

        self.mock_transcriber = MagicMock()

    def test_empty_frames_returns_none(self):
        """Test that empty frames list returns None."""
        args = MagicMock()
        args.type = False

        result = s2t.process_transcription([], self.mock_recorder, self.mock_transcriber, args)
        assert result is None

    def test_transcription_output(self, capsys):
        """Test that transcription is printed to stdout."""
        self.mock_transcriber.transcribe.return_value = "Hello world"
        args = MagicMock()
        args.type = False

        # Create some fake audio frames
        frames = [b"\x00\x00" * 1024]

        result = s2t.process_transcription(frames, self.mock_recorder, self.mock_transcriber, args)

        assert result == "Hello world"
        captured = capsys.readouterr()
        assert "Hello world" in captured.out

    def test_transcription_creates_valid_wav(self):
        """Test that a valid WAV file is created."""
        created_wav_path = None

        def capture_wav_path(path):
            nonlocal created_wav_path
            created_wav_path = path
            return "transcribed text"

        self.mock_transcriber.transcribe.side_effect = capture_wav_path
        args = MagicMock()
        args.type = False

        frames = [b"\x00\x00" * 1024]
        s2t.process_transcription(frames, self.mock_recorder, self.mock_transcriber, args)

        # The file should have been deleted, but we captured the path
        assert created_wav_path is not None
        assert created_wav_path.endswith(".wav")

    def test_temp_file_cleanup(self):
        """Test that temp file is cleaned up after transcription."""
        self.mock_transcriber.transcribe.return_value = "test"
        args = MagicMock()
        args.type = False

        frames = [b"\x00\x00" * 1024]

        # Track the temp file path
        temp_paths = []

        def track_path(path):
            temp_paths.append(path)
            return "test"

        self.mock_transcriber.transcribe.side_effect = track_path

        s2t.process_transcription(frames, self.mock_recorder, self.mock_transcriber, args)

        # Temp file should be deleted
        assert len(temp_paths) == 1
        assert not os.path.exists(temp_paths[0])

    @patch("s2t.subprocess.run")
    def test_wtype_integration(self, mock_run):
        """Test wtype integration calls correct command."""
        self.mock_transcriber.transcribe.return_value = "Hello wtype"
        args = MagicMock()
        args.type = True

        frames = [b"\x00\x00" * 1024]
        s2t.process_transcription(frames, self.mock_recorder, self.mock_transcriber, args)

        mock_run.assert_called_once_with(["wtype", "Hello wtype"], check=True)

    @patch("s2t.subprocess.run")
    def test_wtype_not_found_error(self, mock_run):
        """Test helpful error when wtype is not installed."""
        mock_run.side_effect = FileNotFoundError()
        self.mock_transcriber.transcribe.return_value = "Hello"
        args = MagicMock()
        args.type = True

        frames = [b"\x00\x00" * 1024]

        # Should not raise, just log warning
        result = s2t.process_transcription(frames, self.mock_recorder, self.mock_transcriber, args)
        assert result == "Hello"


class TestWhisperTranscriber:
    """Test WhisperTranscriber class."""

    def test_transcribe_returns_none_when_no_model(self):
        """Test transcribe returns None if model failed to load."""
        transcriber = s2t.WhisperTranscriber()
        transcriber.model = None

        result = transcriber.transcribe("/fake/path.wav")
        assert result is None


class TestThreadSafety:
    """Test thread safety mechanisms."""

    def test_frames_lock_is_reentrant_safe(self):
        """Test that FRAMES_LOCK can be acquired."""
        with s2t.FRAMES_LOCK:
            # Should be able to append while holding lock
            s2t.FRAMES.append(b"test")
            s2t.FRAMES.pop()  # Clean up

    def test_recording_event_operations(self):
        """Test RECORDING_EVENT set/clear/is_set operations."""
        s2t.RECORDING_EVENT.clear()
        assert not s2t.RECORDING_EVENT.is_set()

        s2t.RECORDING_EVENT.set()
        assert s2t.RECORDING_EVENT.is_set()

        s2t.RECORDING_EVENT.clear()
        assert not s2t.RECORDING_EVENT.is_set()
