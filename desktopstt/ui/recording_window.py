"""
Simple recording window for DesktopSTT CLI mode.
"""

import gi
import logging
import threading
import time

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

logger = logging.getLogger(__name__)

class RecordingWindow(Gtk.Window):
    """Simple window shown during recording in CLI mode."""

    def __init__(self, on_stop_callback=None):
        """
        Initialize the recording window.

        Args:
            on_stop_callback: Callback function to call when the stop button is clicked
        """
        super().__init__(title="DesktopSTT Recording")

        self.on_stop_callback = on_stop_callback
        self.recording_time = 0
        self.timer_running = False
        self.timer_thread = None

        # Set window properties
        self.set_default_size(400, 200)
        self.set_resizable(False)

        # Create UI
        self._create_ui()

        # Start the timer
        self._start_timer()

    def _create_ui(self):
        """Create the user interface."""
        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)
        self.set_child(main_box)

        # Recording indicator
        indicator_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        indicator_box.set_halign(Gtk.Align.CENTER)

        recording_label = Gtk.Label()
        recording_label.set_markup("<span size='x-large' weight='bold'>Recording</span>")
        indicator_box.append(recording_label)

        # Pulsing red circle
        self.recording_indicator = Gtk.Label()
        self.recording_indicator.set_markup("<span size='x-large' foreground='red'>●</span>")
        indicator_box.append(self.recording_indicator)

        main_box.append(indicator_box)

        # Timer
        self.timer_label = Gtk.Label(label="00:00")
        self.timer_label.set_markup("<span size='xx-large' weight='bold'>00:00</span>")
        self.timer_label.set_halign(Gtk.Align.CENTER)
        main_box.append(self.timer_label)

        # Instructions
        instructions_label = Gtk.Label()
        instructions_label.set_markup(
            "<span size='small'>Press <b>Stop</b> or close this window to stop recording</span>"
        )
        instructions_label.set_halign(Gtk.Align.CENTER)
        main_box.append(instructions_label)

        # Stop button
        self.stop_button = Gtk.Button(label="Stop Recording")
        self.stop_button.set_halign(Gtk.Align.CENTER)
        self.stop_button.connect("clicked", self._on_stop_clicked)
        main_box.append(self.stop_button)

        # Set up the pulsing animation
        self._setup_pulsing_animation()

    def _setup_pulsing_animation(self):
        """Set up the pulsing animation for the recording indicator."""
        self.pulsing = True
        self.pulsing_visible = True

        def pulse_animation():
            if not self.pulsing:
                return False

            self.pulsing_visible = not self.pulsing_visible

            if self.pulsing_visible:
                self.recording_indicator.set_markup("<span size='x-large' foreground='red'>●</span>")
            else:
                self.recording_indicator.set_markup("<span size='x-large' foreground='white'>●</span>")

            return True

        # Update every 500ms
        GLib.timeout_add(500, pulse_animation)

    def _start_timer(self):
        """Start the recording timer."""
        self.recording_time = 0
        self.timer_running = True

        def update_timer():
            while self.timer_running:
                self.recording_time += 1

                # Update the timer label
                minutes = self.recording_time // 60
                seconds = self.recording_time % 60
                time_str = f"{minutes:02d}:{seconds:02d}"

                GLib.idle_add(self._update_timer_label, time_str)

                time.sleep(1)

        self.timer_thread = threading.Thread(target=update_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

    def _update_timer_label(self, time_str):
        """Update the timer label with the given time string."""
        self.timer_label.set_markup(f"<span size='xx-large' weight='bold'>{time_str}</span>")
        return False

    def _on_stop_clicked(self, button):
        """Handle stop button click."""
        self.stop_recording()

    def stop_recording(self):
        """Stop recording and close the window."""
        self.timer_running = False
        self.pulsing = False

        if self.on_stop_callback:
            self.on_stop_callback()

        self.close()

    def do_close_request(self):
        """Handle window close request."""
        self.stop_recording()
        return False  # Allow the window to close
