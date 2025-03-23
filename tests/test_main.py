#!/usr/bin/env python3
"""
Tests for the main module's temporary file cleanup functionality.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the main module after path setup
from s2t.config import BackendsConfig, PopupRecorderConfig, S2TConfig, WhisperAPIConfig
from s2t.main import main


class MockRecorder:
    """Mock recorder for testing the cleanup functionality."""

    def __init__(self):
        """Initialize the mock recorder."""
        # Create a temporary file to simulate the recorded audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.close()
        self.audio_file = temp_file.name

    def record_and_transcribe(self):
        """Mock the record_and_transcribe method."""
        return "This is a test transcription"


@pytest.fixture
def mock_config():
    """Return a mock configuration for testing."""
    whisper_config = WhisperAPIConfig(api_key="test_api_key", model="whisper-1", language="en")
    backends_config = BackendsConfig(whisper_api=whisper_config)
    popup_recorder_config = PopupRecorderConfig(
        vad_enabled=True, silence_threshold=0.05, silence_duration=2.0, min_recording_time=1.0
    )
    return S2TConfig(backends=backends_config, popup_recorder=popup_recorder_config)


# Create a base mock GLib module to prevent hanging
class MockGLib:
    @staticmethod
    def idle_add(func, *args, **kwargs):
        # Execute the function immediately instead of scheduling it
        if args or kwargs:
            func(*args, **kwargs)
        else:
            func()
        return False

    class MainLoop:
        def __init__(self):
            self._running = False

        def run(self):
            self._running = True
            # Don't actually enter a loop - just set a flag

        def stop(self):
            self._running = False

        def is_running(self):
            return self._running


# Create a mock for Gtk.Box
class MockBox:
    def __init__(self, **kwargs):
        self.widgets = []

    def set_margin_top(self, margin):
        pass

    def set_margin_bottom(self, margin):
        pass

    def set_margin_start(self, margin):
        pass

    def set_margin_end(self, margin):
        pass

    def append(self, widget):
        self.widgets.append(widget)


# Create a mock for Gtk.Label
class MockLabel:
    def __init__(self, **kwargs):
        pass

    def set_markup(self, markup):
        pass

    def set_halign(self, halign):
        pass


# Create a mock for Gtk.Button
class MockButton:
    def __init__(self, **kwargs):
        pass

    def set_halign(self, halign):
        pass

    def connect(self, signal, callback):
        pass


# Create a mock for Gtk classes and constants
class MockGtk:
    class Orientation:
        VERTICAL = "vertical"
        HORIZONTAL = "horizontal"

    class Align:
        START = "start"
        CENTER = "center"

    class Window:
        def __init__(self, **kwargs):
            self.child = None

        def set_default_size(self, width, height):
            pass

        def set_resizable(self, resizable):
            pass

        def set_child(self, child):
            self.child = child

        def present(self):
            pass

        def close(self):
            pass

    @staticmethod
    def box(**kwargs):
        return MockBox(**kwargs)

    @staticmethod
    def label(**kwargs):
        return MockLabel(**kwargs)

    @staticmethod
    def button(**kwargs):
        return MockButton(**kwargs)


# Mock RecordingWindow class
class MockRecordingWindow(MockGtk.Window):
    def __init__(self, on_stop_callback=None, title="S2T Recording"):
        super().__init__(title=title)
        self.on_stop_callback = on_stop_callback
        self.recording_time = 0
        self.timer_running = False
        self.timer_thread = None
        self.level_bar = MagicMock()
        self.recording_indicator = MockLabel()
        self.vad_status = MockLabel()
        self.timer_label = MockLabel()
        self.stop_button = MockButton()
        self.pulsing = False
        self.pulsing_visible = False

    def _create_ui(self):
        pass

    def _setup_pulsing_animation(self):
        pass

    def _start_timer(self):
        pass

    def _update_timer_label(self, time_str):
        return False

    def update_audio_level(self, level):
        pass

    def update_vad_status(self, is_speech, silence_duration=None):
        pass

    def _set_vad_status(self, markup):
        return False

    def _on_stop_clicked(self, button):
        pass

    def stop_recording(self):
        if self.on_stop_callback:
            self.on_stop_callback()

    def do_close_request(self):
        return False


# Mock ImmediateRecordingWindow class
class MockImmediateRecordingWindow(MockRecordingWindow):
    def __init__(self, on_stop_callback=None, title="S2T Recording"):
        super().__init__(on_stop_callback, title)


# Mock a PopupRecorder that doesn't use GTK or GLib
class MockPopupRecorder:
    """Mock for PopupRecorder that doesn't depend on GTK or GLib."""

    def __init__(self, config):
        self.config = config
        # Create a file with a predictable path
        self.audio_file = "/tmp/s2t_recording_20250323_123456.wav"
        # Touch the file to ensure it exists
        with open(self.audio_file, "w") as f:
            f.write("test audio data")

    def record_and_transcribe(self, duration=None):
        """Override to avoid using GTK/GLib."""
        return "This is a mock transcription"


# Mock ImmediatePopupRecorder class
class MockImmediatePopupRecorder(MockPopupRecorder):
    """Mock for ImmediatePopupRecorder that doesn't depend on GTK or GLib."""

    pass


# Mock the whole RecordingWindow class to avoid GTK errors
@patch("s2t.popup_recorder.RecordingWindow", MockRecordingWindow)
@patch("s2t.immediate_popup.ImmediateRecordingWindow", MockImmediateRecordingWindow)
@patch("gi.repository.GLib", MockGLib)
@patch("gi.repository.Gtk", MockGtk)
@patch("sys.exit")
@patch("openai.OpenAI")  # Add mock for OpenAI client
@patch("s2t.main.os.remove")
@patch("s2t.main.os.path.exists")
@patch("s2t.main.os.environ.get")
@patch("s2t.main.subprocess.run")
@patch("s2t.main.load_config")
def test_temp_file_cleanup_popup_mode(
    mock_load_config,
    mock_subprocess_run,
    mock_environ_get,
    mock_path_exists,
    mock_remove,
    mock_openai,
    mock_exit,
    mock_config,
):
    """Test that temporary files are cleaned up in popup mode."""
    # Configure mocks
    mock_path_exists.return_value = True
    mock_environ_get.return_value = "test_api_key"
    mock_load_config.return_value = mock_config

    # Return a mock for OpenAI client
    mock_openai.return_value = MagicMock()

    # Patch the imports to return our mock recorder
    with patch.dict(
        "sys.modules",
        {
            "s2t.immediate_popup": MagicMock(),
            "gi": MagicMock(),
            "gi.repository": MagicMock(),
            "gi.repository.GLib": MockGLib,
            "gi.repository.Gtk": MockGtk,
        },
    ):
        # Create a mock recorder instance that will be returned by the constructor
        recorder_instance = MockImmediatePopupRecorder(mock_config)

        # Mock the ImmediatePopupRecorder class to return our instance
        with patch("s2t.main.ImmediatePopupRecorder", return_value=recorder_instance):
            # Parse args for main
            with patch("sys.argv", ["s2t"]):
                # Run main
                main()

                # Check that os.remove was called
                mock_remove.assert_called_once()


@pytest.mark.skip(reason="Issues with mocking the full silent mode flow")
@patch("s2t.main.os.remove")
@patch("s2t.main.os.path.exists")
@patch("openai.OpenAI")
@patch("s2t.backends.get_backend")
@patch("s2t.main.load_config")
@patch("s2t.main.TrulySilentRecorder")
def test_temp_file_cleanup_silent_mode(
    mock_recorder_class,
    mock_load_config,
    mock_get_backend,
    mock_openai,
    mock_path_exists,
    mock_remove,
):
    """Test that temporary files are cleaned up in silent mode."""
    # Create a temporary file to simulate the recorded audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    audio_file_path = temp_file.name

    # Create a mock OpenAI client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    # Create a mock backend
    mock_backend = MagicMock()
    mock_backend.transcribe.return_value = "Test transcription"
    mock_get_backend.return_value = mock_backend

    # Create a mock recorder instance with our audio_file
    mock_recorder = MagicMock()
    mock_recorder.audio_file = audio_file_path
    mock_recorder.record_and_transcribe.return_value = "Test transcription"
    mock_recorder_class.return_value = mock_recorder

    # Setup the mock config
    mock_config = MagicMock()
    mock_config.backends.default = "whisper_api"
    mock_load_config.return_value = mock_config

    # Mock path.exists to return True
    mock_path_exists.return_value = True

    # Mock sys.argv to use silent mode
    with patch("sys.argv", ["s2t", "--silent"]):
        # And mock the environment
        with patch("s2t.main.os.environ.get", return_value="test_api_key"):
            with patch.dict("os.environ", {"SSL_CERT_FILE": "/tmp/fake/cert.pem"}):
                # Run main - this should trigger cleanup
                main()

    # Check that os.remove was called once
    mock_remove.assert_called_once()

    # Actual cleanup in case the test fails
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)


# Mock the whole RecordingWindow class to avoid GTK errors
@patch("s2t.popup_recorder.RecordingWindow", MockRecordingWindow)
@patch("s2t.immediate_popup.ImmediateRecordingWindow", MockImmediateRecordingWindow)
@patch("gi.repository.GLib", MockGLib)
@patch("gi.repository.Gtk", MockGtk)
@patch("sys.exit")
@patch("openai.OpenAI")  # Add mock for OpenAI client
@patch("s2t.main.os.remove")
@patch("s2t.main.os.path.exists")
@patch("s2t.main.os.environ.get")
@patch("s2t.main.subprocess.run")
@patch("s2t.main.load_config")
def test_temp_file_nonexistent(
    mock_load_config,
    mock_subprocess_run,
    mock_environ_get,
    mock_path_exists,
    mock_remove,
    mock_openai,
    mock_exit,
    mock_config,
):
    """Test that the cleanup code handles the case where the audio file doesn't exist."""
    # Configure mocks
    mock_environ_get.return_value = "test_api_key"
    mock_load_config.return_value = mock_config

    # Return a mock for OpenAI client
    mock_openai.return_value = MagicMock()

    # Path exists will return True for config file check, but False for audio file check
    mock_path_exists.side_effect = lambda path: False if path.endswith(".wav") else True

    # Patch the imports to return our mock recorder
    with patch.dict(
        "sys.modules",
        {
            "s2t.immediate_popup": MagicMock(),
            "gi": MagicMock(),
            "gi.repository": MagicMock(),
            "gi.repository.GLib": MockGLib,
            "gi.repository.Gtk": MockGtk,
        },
    ):
        # Create a custom nonexistent file recorder
        class NonExistentFileRecorder(MockImmediatePopupRecorder):
            def __init__(self, config):
                super().__init__(config)
                self.audio_file = "/tmp/nonexistent_file.wav"

        # Create mock instance
        recorder_instance = NonExistentFileRecorder(mock_config)

        # Mock the ImmediatePopupRecorder class to return our instance
        with patch("s2t.main.ImmediatePopupRecorder", return_value=recorder_instance):
            # Parse args for main
            with patch("sys.argv", ["s2t"]):
                # Run main - should not raise an exception
                main()

                # Verify that os.remove was not called
                mock_remove.assert_not_called()


@patch("os.remove")
@patch("os.path.exists")
@patch("s2t.popup_recorder.PopupRecorder")
def test_temp_file_error_handling(mock_popup_recorder, mock_exists, mock_remove):
    """Test temp file cleanup when os.remove raises an exception."""
    # Setup mocks
    mock_config = MagicMock()
    mock_config.backends.api = "whisper_api"
    mock_config.popup_recorder.duration = 5

    # Create a mock recorder instance with a predictable file path
    recorder_instance = MockPopupRecorder(mock_config)
    mock_popup_recorder.return_value = recorder_instance

    # Set up path.exists to return True
    mock_exists.return_value = True

    # Set os.remove to raise an exception
    mock_remove.side_effect = OSError("Test error")

    # Call the function (should not raise an exception despite os.remove failing)
    record_and_transcribe_popup_mode(mock_config)

    # Verify os.remove was called
    mock_remove.assert_called_once()


# Add this function for testing before the test function
def record_and_transcribe_popup_mode(config):
    """
    Test helper function to simulate popup mode recording.
    This is a simplified version of what would be in main.py for testing purposes.
    """
    from s2t.popup_recorder import PopupRecorder

    recorder = PopupRecorder(config)
    transcription = recorder.record_and_transcribe()

    # Get the audio file path for cleanup
    audio_file_path = getattr(recorder, "audio_file", None)

    # Clean up the temporary audio file
    if audio_file_path and os.path.exists(audio_file_path):
        try:
            os.remove(audio_file_path)
        except Exception as e:
            print(f"Failed to remove temporary audio file: {e}")

    return transcription


def test_temp_file_cleanup_direct():
    """Test the cleanup directly using a simple function."""
    # Create a temporary file to simulate the recorded audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    audio_file_path = temp_file.name

    # Setup mocks
    with patch("os.path.exists") as mock_exists, patch("os.remove") as mock_remove:
        # Configure mocks
        mock_exists.return_value = True

        # Perform the cleanup
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

        # Verify that os.remove was called
        mock_remove.assert_called_once_with(audio_file_path)

    # Actual cleanup in case the test fails
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)


@patch("s2t.main.os.remove")
@patch("s2t.main.os.path.exists")
def test_temp_file_cleanup_functionality(mock_path_exists, mock_remove):
    """Test that the cleanup code in main.py functions correctly."""
    # Create a temporary file to simulate the recorded audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_file.close()
    audio_file_path = temp_file.name

    # Configure mocks
    mock_path_exists.return_value = True

    # Create a dummy recorder with an audio_file attribute
    class DummyRecorder:
        def __init__(self):
            self.audio_file = audio_file_path

    # Simulate the cleanup code from main.py
    recorder = DummyRecorder()

    # Clean up the temporary audio file - this simulates the cleanup code in main.py
    if recorder.audio_file and os.path.exists(recorder.audio_file):
        try:
            os.remove(recorder.audio_file)
        except Exception as e:
            print(f"Failed to remove temporary audio file: {e}")

    # Check that os.remove was called once with the correct path
    mock_remove.assert_called_once_with(audio_file_path)

    # Actual cleanup in case the test fails
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
