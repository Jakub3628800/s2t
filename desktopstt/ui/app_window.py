"""
Main application window for DesktopSTT.
"""

import os
import gi
import logging
import threading

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk

from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend

logger = logging.getLogger(__name__)

class AppWindow(Gtk.ApplicationWindow):
    """Main application window for DesktopSTT."""

    def __init__(self, app, config):
        """
        Initialize the application window.

        Args:
            app: The Gtk.Application instance
            config: Application configuration dictionary
        """
        super().__init__(application=app, title="DesktopSTT")

        self.config = config
        self.ui_config = config["ui"]

        # Set window properties
        self.set_default_size(
            self.ui_config["window_width"],
            self.ui_config["window_height"]
        )

        # Initialize components
        self.recorder = AudioRecorder(config)
        self.backend = get_backend(config)

        # State variables
        self.is_recording = False
        self.current_audio_file = None
        self.transcription_in_progress = False

        # Create UI
        self._create_ui()
        self._setup_shortcuts()

    def _create_ui(self):
        """Create the user interface."""
        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        self.set_child(main_box)

        # Header with title
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>DesktopSTT</span>")
        header_box.append(title_label)
        main_box.append(header_box)

        # Status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.append(self.status_label)

        # Text view for transcription output
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(True)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_buffer = self.text_view.get_buffer()

        scrolled_window.set_child(self.text_view)
        main_box.append(scrolled_window)

        # Control buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_box.set_halign(Gtk.Align.CENTER)

        self.record_button = Gtk.Button(label="Start Recording")
        self.record_button.connect("clicked", self._on_record_clicked)
        button_box.append(self.record_button)

        self.clear_button = Gtk.Button(label="Clear")
        self.clear_button.connect("clicked", self._on_clear_clicked)
        button_box.append(self.clear_button)

        self.copy_button = Gtk.Button(label="Copy to Clipboard")
        self.copy_button.connect("clicked", self._on_copy_clicked)
        button_box.append(self.copy_button)

        self.save_button = Gtk.Button(label="Save")
        self.save_button.connect("clicked", self._on_save_clicked)
        button_box.append(self.save_button)

        main_box.append(button_box)

        # Backend status
        backend_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        backend_box.set_halign(Gtk.Align.END)

        backend_label = Gtk.Label(label=f"Backend: {self.backend.get_name()}")
        backend_status = Gtk.Label()

        if self.backend.is_available():
            backend_status.set_markup("<span foreground='green'>✓</span>")
        else:
            backend_status.set_markup("<span foreground='red'>✗</span>")

        backend_box.append(backend_label)
        backend_box.append(backend_status)
        main_box.append(backend_box)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        shortcut_controller = Gtk.ShortcutController()

        # Ctrl+R to start/stop recording
        record_shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Control>r"),
            Gtk.CallbackAction.new(self._on_record_shortcut)
        )
        shortcut_controller.add_shortcut(record_shortcut)

        # Ctrl+C to copy text
        copy_shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Control>c"),
            Gtk.CallbackAction.new(self._on_copy_shortcut)
        )
        shortcut_controller.add_shortcut(copy_shortcut)

        # Ctrl+S to save text
        save_shortcut = Gtk.Shortcut.new(
            Gtk.ShortcutTrigger.parse_string("<Control>s"),
            Gtk.CallbackAction.new(self._on_save_shortcut)
        )
        shortcut_controller.add_shortcut(save_shortcut)

        self.add_controller(shortcut_controller)

    def _on_record_clicked(self, button):
        """Handle record button click."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _on_clear_clicked(self, button):
        """Handle clear button click."""
        self.text_buffer.set_text("")

    def _on_copy_clicked(self, button):
        """Handle copy button click."""
        self._copy_to_clipboard()

    def _on_save_clicked(self, button):
        """Handle save button click."""
        self._save_transcription()

    def _on_record_shortcut(self):
        """Handle record keyboard shortcut."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
        return True

    def _on_copy_shortcut(self):
        """Handle copy keyboard shortcut."""
        self._copy_to_clipboard()
        return True

    def _on_save_shortcut(self):
        """Handle save keyboard shortcut."""
        self._save_transcription()
        return True

    def _start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            return

        if not self.backend.is_available():
            self._show_error("Speech-to-text backend is not available")
            return

        success = self.recorder.start_recording()
        if success:
            self.is_recording = True
            self.record_button.set_label("Stop Recording")
            self.status_label.set_text("Recording...")
            logger.info("Started recording")
        else:
            self._show_error("Failed to start recording")

    def _stop_recording(self):
        """Stop recording audio and start transcription."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.record_button.set_label("Start Recording")
        self.status_label.set_text("Processing...")

        # Stop recording and get the audio file
        self.current_audio_file = self.recorder.stop_recording()

        if self.current_audio_file:
            logger.info(f"Stopped recording, saved to {self.current_audio_file}")

            # Start transcription in a separate thread
            self.transcription_in_progress = True
            threading.Thread(target=self._transcribe_audio).start()
        else:
            self.status_label.set_text("Ready")
            self._show_error("Failed to save recording")

    def _transcribe_audio(self):
        """Transcribe the recorded audio."""
        try:
            # Transcribe the audio
            result = self.backend.transcribe(self.current_audio_file)

            # Update the UI with the transcription result
            GLib.idle_add(self._update_transcription, result)

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            GLib.idle_add(self._show_error, f"Transcription error: {str(e)}")

        finally:
            self.transcription_in_progress = False
            GLib.idle_add(self.status_label.set_text, "Ready")

    def _update_transcription(self, result):
        """Update the UI with the transcription result."""
        if not result:
            return

        text = result.get('text', '')
        if not text:
            self._show_error("No transcription result")
            return

        # Get current text and append the new transcription
        start_iter = self.text_buffer.get_end_iter()

        # Add a newline if there's already text
        if self.text_buffer.get_char_count() > 0:
            self.text_buffer.insert(start_iter, "\n\n")
            start_iter = self.text_buffer.get_end_iter()

        # Insert the transcribed text
        self.text_buffer.insert(start_iter, text)

        # Auto-save if configured
        if self.config["output"]["save_transcriptions"]:
            self._save_transcription_to_file()

        # Auto-copy if configured
        if self.config["output"]["auto_copy_to_clipboard"]:
            self._copy_to_clipboard()

    def _copy_to_clipboard(self):
        """Copy the transcription text to clipboard."""
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_text(start_iter, end_iter, False)

        if not text:
            return

        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set_text(text)

        self.status_label.set_text("Copied to clipboard")
        logger.info("Copied transcription to clipboard")

    def _save_transcription(self):
        """Save the transcription text to a file."""
        self._save_transcription_to_file()
        self.status_label.set_text("Transcription saved")

    def _save_transcription_to_file(self):
        """Save the transcription text to a file."""
        start_iter = self.text_buffer.get_start_iter()
        end_iter = self.text_buffer.get_end_iter()
        text = self.text_buffer.get_text(start_iter, end_iter, False)

        if not text:
            return

        # Create the transcriptions directory if it doesn't exist
        transcriptions_dir = self.config["output"]["transcriptions_dir"]
        os.makedirs(transcriptions_dir, exist_ok=True)

        # Generate a filename based on the current date and time
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(transcriptions_dir, f"transcription_{timestamp}.txt")

        # Save the transcription to the file
        try:
            with open(filename, 'w') as f:
                f.write(text)
            logger.info(f"Saved transcription to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving transcription: {e}")
            self._show_error(f"Error saving transcription: {str(e)}")
            return False

    def _show_error(self, message):
        """Show an error message dialog."""
        dialog = Gtk.AlertDialog.new(message)
        dialog.show(self)
        logger.error(message)
