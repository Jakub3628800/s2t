"""
Command-line interface for DesktopSTT.
"""

import os
import sys
import time
import logging
import argparse
import signal
import threading
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.ui.recording_window import RecordingWindow

logger = logging.getLogger(__name__)

class CLIRecorder:
    """Command-line interface for recording and transcribing audio."""

    def __init__(self, config, show_ui=False):
        """
        Initialize the CLI recorder.

        Args:
            config: Application configuration dictionary
            show_ui: Whether to show a UI during recording
        """
        self.config = config
        self.show_ui = show_ui
        self.recorder = AudioRecorder(config)
        self.backend = get_backend(config)
        self.is_recording = False
        self.recording_thread = None
        self.ui_window = None
        self.stop_event = threading.Event()

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False

        if not self.backend.is_available():
            logger.error("Speech-to-text backend is not available")
            return False

        success = self.recorder.start_recording()
        if success:
            self.is_recording = True
            logger.info("Started recording")

            # Show UI if requested
            if self.show_ui:
                self._show_ui()

            return True
        else:
            logger.error("Failed to start recording")
            return False

    def stop_recording(self):
        """Stop recording audio and return the path to the recorded file."""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None

        self.is_recording = False

        # Hide UI if it was shown
        if self.show_ui and self.ui_window:
            GLib.idle_add(self._hide_ui)

        # Stop recording and get the audio file
        audio_file = self.recorder.stop_recording()

        if audio_file:
            logger.info(f"Stopped recording, saved to {audio_file}")
            return audio_file
        else:
            logger.error("Failed to save recording")
            return None

    def transcribe(self, audio_file):
        """
        Transcribe the given audio file to text.

        Args:
            audio_file: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        if not audio_file or not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            logger.info(f"Transcribing audio file: {audio_file}")
            result = self.backend.transcribe(audio_file)
            text = result.get('text', '')

            if not text:
                logger.error("No transcription result")
                return None

            logger.info(f"Transcription successful: {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    def record_and_transcribe(self, duration=None):
        """
        Record audio for the specified duration and transcribe it.

        Args:
            duration: Duration in seconds to record, or None to wait for user input

        Returns:
            The transcribed text, or None if recording or transcription failed
        """
        # Start recording
        if not self.start_recording():
            return None

        try:
            # Wait for the specified duration or user input
            if duration:
                logger.info(f"Recording for {duration} seconds...")
                time.sleep(duration)
                self.stop_recording()
            elif self.show_ui:
                # If showing UI, wait for the stop event from the UI
                logger.info("Recording... Close the window or press Stop to end recording")
                self.stop_event.wait()
            else:
                # Otherwise, wait for user input
                logger.info("Recording... Press Enter to stop")
                try:
                    input()
                except KeyboardInterrupt:
                    pass
                self.stop_recording()

            # Get the audio file (if not already stopped by UI)
            audio_file = self.recorder.stop_recording() if self.is_recording else None

            if not audio_file:
                return None

            # Transcribe the audio
            logger.info("Transcribing audio...")
            return self.transcribe(audio_file)

        except Exception as e:
            logger.error(f"Error in record_and_transcribe: {e}")
            if self.is_recording:
                self.stop_recording()
            return None

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals."""
        logger.info("Received interrupt signal, stopping recording...")
        if self.is_recording:
            self.stop_recording()
        sys.exit(0)

    def _show_ui(self):
        """Show a simple UI during recording."""
        def run_ui():
            # Create and show the recording window
            self.ui_window = RecordingWindow(on_stop_callback=self._on_ui_stop)
            self.ui_window.connect("close-request", self._on_ui_close)
            self.ui_window.present()

            # Start a GTK main loop
            Gtk.main()

        # Run the UI in a separate thread
        ui_thread = threading.Thread(target=run_ui)
        ui_thread.daemon = True
        ui_thread.start()

    def _hide_ui(self):
        """Hide the UI."""
        if self.ui_window:
            self.ui_window.close()
            self.ui_window = None
            Gtk.main_quit()

    def _on_ui_stop(self):
        """Callback for when the UI stop button is clicked."""
        logger.info("Stop button clicked in UI")
        self.stop_recording()
        self.stop_event.set()

    def _on_ui_close(self, window):
        """Callback for when the UI window is closed."""
        logger.info("UI window closed")
        self.stop_recording()
        self.stop_event.set()
        Gtk.main_quit()
        return False


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='DesktopSTT CLI')
    parser.add_argument(
        '--config',
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f'Path to config file (default: {DEFAULT_CONFIG_PATH})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--time',
        type=float,
        help='Record for specified number of seconds and then stop'
    )
    parser.add_argument(
        '--ui',
        action='store_true',
        help='Show a simple UI during recording'
    )
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load configuration
    config = load_config(args.config)

    # Create CLI recorder
    cli = CLIRecorder(config, show_ui=args.ui)

    # Record and transcribe
    text = cli.record_and_transcribe(duration=args.time)

    if text:
        # Output the transcription
        if args.output:
            with open(args.output, 'w') as f:
                f.write(text)
            logger.info(f"Transcription saved to {args.output}")
        else:
            # Output to stdout
            print(text)
        return 0
    else:
        logger.error("Failed to transcribe audio")
        return 1

if __name__ == "__main__":
    sys.exit(main())
