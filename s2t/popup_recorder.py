#!/usr/bin/env python3
"""
Popup recorder for S2T.

This module provides a graphical popup window for recording with visual feedback.
"""

import argparse
import logging
import os
import signal
import sys
import threading
import time

# Import gi and set the required versions
import gi
import numpy as np  # Add NumPy import

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib, Gtk

# Import our modules
from s2t.audio import AudioRecorder  # noqa: E402
from s2t.backends import get_backend  # noqa: E402
from s2t.config import DEFAULT_CONFIG_PATH, load_config  # noqa: E402

# Parse command line arguments
parser = argparse.ArgumentParser(description="Record audio and transcribe it with a popup window.")
parser.add_argument(
    "--time",
    type=float,
    help="Recording time in seconds (default: record until stopped)",
)
parser.add_argument(
    "--output",
    type=str,
    help="Output file for transcription (default: print to stdout)",
)
parser.add_argument(
    "--config",
    type=str,
    default=DEFAULT_CONFIG_PATH,
    help=f"Path to config file (default: {DEFAULT_CONFIG_PATH})",
)
parser.add_argument(
    "--env-file", type=str, default=".env", help="Path to .env file (default: .env)"
)
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument(
    "--silent",
    action="store_true",
    help="Output only the transcribed text (no logging)",
)
parser.add_argument("--no-vad", action="store_true", help="Disable voice activity detection")
parser.add_argument(
    "--silence-threshold",
    type=float,
    default=0.1,
    help="Threshold for silence detection (0.0-1.0, default: 0.1)",
)
parser.add_argument(
    "--silence-duration",
    type=float,
    default=5.0,
    help="Duration of silence before stopping (seconds, default: 5.0)",
)
parser.add_argument(
    "--min-recording-time",
    type=float,
    default=3.0,
    help="Minimum recording time before VAD kicks in (seconds, default: 3.0)",
)

# Parse arguments
args = parser.parse_args()

# Set up logging
log_level = logging.DEBUG if args.debug else logging.INFO
if args.silent:
    log_level = logging.ERROR  # Suppress most logs in silent mode

logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Suppress all logs except for critical errors if silent mode is enabled
if args.silent:
    logging.disable(logging.CRITICAL)

logger = logging.getLogger(__name__)


class AudioLevelBar(Gtk.DrawingArea):
    """A custom widget to display audio levels."""

    def __init__(self):
        """Initialize the audio level bar."""
        super().__init__()

        self.level = 0.0  # Current audio level (0.0 to 1.0)
        self.peak = 0.0  # Peak level
        self.set_content_width(300)
        self.set_content_height(30)
        self.set_draw_func(self._draw)

    def set_level(self, level):
        """Set the current audio level and queue a redraw."""
        self.level = min(max(level, 0.0), 1.0)
        self.peak = max(self.peak * 0.95, self.level)  # Decay peak slowly
        self.queue_draw()

    def _draw(self, area, cr, width, height, *args):
        """Draw the audio level bar."""
        # Draw background
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Draw level bar
        level_width = int(width * self.level)
        if level_width > 0:
            # Gradient from green to red
            if self.level < 0.5:
                # Green to yellow
                r = self.level * 2
                g = 1.0
                b = 0.0
            else:
                # Yellow to red
                r = 1.0
                g = 1.0 - (self.level - 0.5) * 2
                b = 0.0

            cr.set_source_rgb(r, g, b)
            cr.rectangle(0, 0, level_width, height)
            cr.fill()

        # Draw peak indicator
        peak_x = int(width * self.peak)
        if peak_x > 0:
            cr.set_source_rgb(1.0, 1.0, 1.0)
            cr.rectangle(peak_x - 2, 0, 2, height)
            cr.fill()

        # Draw threshold line for silence detection
        threshold_x = int(width * 0.1)  # 10% threshold
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.set_dash([5, 5], 0)
        cr.move_to(threshold_x, 0)
        cr.line_to(threshold_x, height)
        cr.stroke()


class RecordingWindow(Gtk.Window):
    """Window for recording audio with visual feedback."""

    def __init__(self, on_stop_callback=None, title="S2T Recording"):
        """Initialize the recording window."""
        super().__init__(title=title)

        self.on_stop_callback = on_stop_callback
        self.recording_time = 0
        self.timer_running = False
        self.timer_thread = None

        # Set window properties
        self.set_default_size(400, 250)
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

        # Audio level meter
        level_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        level_label = Gtk.Label(label="Audio Level")
        level_label.set_halign(Gtk.Align.START)
        level_box.append(level_label)

        self.level_bar = AudioLevelBar()
        level_box.append(self.level_bar)

        main_box.append(level_box)

        # Voice activity status
        self.vad_status = Gtk.Label()
        self.vad_status.set_markup("<span>Waiting for speech...</span>")
        self.vad_status.set_halign(Gtk.Align.CENTER)
        main_box.append(self.vad_status)

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
                self.recording_indicator.set_markup(
                    "<span size='x-large' foreground='red'>●</span>"
                )
            else:
                self.recording_indicator.set_markup(
                    "<span size='x-large' foreground='white'>●</span>"
                )

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

    def update_audio_level(self, level):
        """Update the audio level meter."""
        GLib.idle_add(self.level_bar.set_level, level)

    def update_vad_status(self, is_speech, silence_duration=None):
        """Update the voice activity detection status."""
        if is_speech:
            GLib.idle_add(self._set_vad_status, "<span foreground='green'>Speech detected</span>")
        else:
            if silence_duration is not None:
                GLib.idle_add(
                    self._set_vad_status,
                    f"<span foreground='orange'>Silence detected ({silence_duration:.1f}s)</span>",
                )
            else:
                GLib.idle_add(self._set_vad_status, "<span>Waiting for speech...</span>")

    def _set_vad_status(self, markup):
        """Set the VAD status label markup."""
        self.vad_status.set_markup(markup)
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


class PopupRecorder:
    """Records audio with a popup window showing recording status."""

    def __init__(self, config):
        """Initialize the recorder with the given configuration."""
        self.config = config
        self.backend = get_backend(config)
        self.audio_recorder = AudioRecorder(config)
        self.window = None
        self.is_recording = False
        self.audio_file = None
        self.result_text = None
        self.stop_event = threading.Event()
        self.main_loop = None

        # Set up VAD configuration
        self.vad_enabled = config.get("popup_recorder", {}).get("vad_enabled", True)
        self.silence_threshold = config.get("popup_recorder", {}).get("silence_threshold", 0.1)
        self.silence_duration = config.get("popup_recorder", {}).get("silence_duration", 5.0)
        self.min_recording_time = config.get("popup_recorder", {}).get("min_recording_time", 3.0)

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def start_recording(self, audio_callback=None):
        """Start recording audio and show the popup window."""
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False

        if not self.backend.is_available():
            logger.error("Speech-to-text backend is not available")
            logger.error(f"API key set: {bool(self.config['backends']['whisper_api']['api_key'])}")
            return False

        # Define a callback to process audio frames for VAD
        def process_audio(in_data):
            if not self.is_recording:
                return None

            # Convert audio data to numpy array
            audio_data = np.frombuffer(in_data, dtype=np.int16)

            # Calculate audio level (RMS)
            if len(audio_data) > 0:
                rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32) / 32768.0)))
                level = min(rms * 5.0, 1.0)  # Scale for better visualization

                # Update the level meter
                if self.window:
                    self.window.update_audio_level(level)

                # Voice activity detection
                if self.vad_enabled and self.recording_start_time is not None:
                    current_time = time.time()
                    recording_duration = current_time - self.recording_start_time

                    # Only start VAD after minimum recording time
                    if recording_duration >= self.min_recording_time:
                        is_speech_now = level > self.silence_threshold

                        if is_speech_now:
                            # Speech detected
                            self.is_speech = True
                            self.silence_start_time = None
                            if self.window:
                                self.window.update_vad_status(True)
                        else:
                            # Silence detected
                            if self.is_speech:
                                # Transition from speech to silence
                                self.is_speech = False
                                self.silence_start_time = current_time
                                if self.window:
                                    self.window.update_vad_status(False)
                            elif self.silence_start_time is not None:
                                # Continued silence
                                silence_duration = current_time - self.silence_start_time
                                if self.window:
                                    self.window.update_vad_status(False, silence_duration)

                                # Stop recording if silence duration exceeds threshold
                                if silence_duration >= self.silence_duration:
                                    logger.info(
                                        f"Stopping recording after {silence_duration:.1f}s of silence"
                                    )
                                    GLib.idle_add(self._stop_recording_from_thread)

            # Call the original callback if provided
            if audio_callback:
                audio_callback(in_data)

            return None

        success = self.audio_recorder.start_recording(callback=process_audio)
        if success:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.is_speech = False
            self.silence_start_time = None
            logger.info("Started recording")

            # Show the popup window
            self._show_window()

            return True
        else:
            logger.error("Failed to start recording")
            return False

    def stop_recording(self):
        """Stop recording audio."""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None

        self.is_recording = False

        # Stop recording and get the audio file
        audio_file = self.audio_recorder.stop_recording()
        self.audio_file = audio_file

        if audio_file:
            logger.info(f"Stopped recording, saved to {audio_file}")
            return audio_file
        else:
            logger.error("Failed to save recording")
            return None

    def transcribe(self, audio_file):
        """Transcribe the given audio file to text."""
        if not audio_file or not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None

        try:
            logger.info(f"Transcribing audio file: {audio_file}")
            result = self.backend.transcribe(audio_file)
            text = result.get("text", "")

            if not text:
                logger.error("No transcription result")
                return None

            logger.info(f"Transcription successful: {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    def record_and_transcribe(self, duration=None):
        """Record audio and transcribe it.

        Args:
            duration: Recording duration in seconds. If None, record until stopped.

        Returns:
            The transcribed text, or None if transcription failed.
        """
        # Start recording
        if not self.start_recording():
            logger.error("Failed to start recording")
            return None

        try:
            # If duration is specified, set a timer to stop recording
            if duration and not self.vad_enabled:

                def stop_after_duration():
                    logger.info(f"Recording for {duration} seconds...")
                    time.sleep(duration)
                    if self.is_recording:
                        logger.info("Stopping recording after duration...")
                        GLib.idle_add(self._stop_recording_from_thread)

                timer_thread = threading.Thread(target=stop_after_duration)
                timer_thread.daemon = True
                timer_thread.start()

            # Start the GTK main loop
            self.main_loop = GLib.MainLoop()
            self.main_loop.run()

            # At this point, recording has been stopped by user or timer

            # Check if we have an audio file
            if not self.audio_file:
                logger.error("No audio file was created")
                return None

            # Transcribe the audio
            self.result_text = self.transcribe(self.audio_file)
            return self.result_text

        except Exception as e:
            logger.error(f"Error in record_and_transcribe: {e}")
            if self.is_recording:
                self.stop_recording()
            return None

    def _show_window(self):
        """Show the recording window."""
        self.window = RecordingWindow(on_stop_callback=self._on_window_stop)
        self.window.connect("close-request", self._on_window_close)
        self.window.present()

    def _on_window_stop(self):
        """Handle window stop button click."""
        logger.info("Stop button clicked")
        self._stop_recording()

    def _on_window_close(self, window):
        """Handle window close."""
        logger.info("Window closed")
        self._stop_recording()
        return False

    def _stop_recording(self):
        """Stop recording and quit the GTK main loop."""
        # Only stop recording if we're actually recording
        if self.is_recording:
            self.stop_recording()

        # Signal that we're done
        self.stop_event.set()

        # Quit the main loop if it's running
        if self.main_loop and self.main_loop.is_running():
            self.main_loop.quit()

    def _stop_recording_from_thread(self):
        """Stop recording from a thread (via GLib.idle_add)."""
        self._stop_recording()
        return False

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signals."""
        logger.info("Received interrupt signal, stopping recording...")
        if self.is_recording:
            GLib.idle_add(self._stop_recording_from_thread)
        sys.exit(0)


def check_system_dependencies():
    """Check if required system dependencies are installed."""
    missing_deps = []
    
    # Check for libgirepository (for GUI mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gobject-introspection-1.0"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgirepository1.0-dev")
    
    # Check for GTK4 (for popup mode)
    try:
        subprocess.run(["pkg-config", "--exists", "gtk4"], 
                      check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        missing_deps.append("libgtk-4-dev")
    
    return missing_deps

def print_dependency_warning(missing_deps):
    """Print a warning about missing dependencies."""
    print("\n⚠️  Missing system dependencies detected! ⚠️")
    print("The following system packages are required but not found:")
    for dep in missing_deps:
        print(f"  - {dep}")
    print("\nOn Ubuntu/Debian, install them with:")
    print(f"  sudo apt-get install {' '.join(missing_deps)}")
    print("\nCannot continue without these dependencies.\n")

def main():
    """Command-line entry point."""
    # Check system dependencies
    missing_deps = check_system_dependencies()
    if missing_deps:
        print_dependency_warning(missing_deps)
        sys.exit(1)
        
    # Parse arguments
    args = parser.parse_args()

    # Check for environment variables
    logger.info(f"Using env file: {args.env_file} (parsed automatically)")

    # Load configuration
    config = load_config(args.config)

    # Check if API key is set in environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        # Set the API key in the config
        config["backends"]["whisper_api"]["api_key"] = api_key
        logger.info("Using OpenAI API key from environment variables")

    # Check if API key is set in config
    if not config["backends"]["whisper_api"]["api_key"]:
        logger.warning("No OpenAI API key found in config or environment variables")
        logger.warning("Transcription may fail. Set OPENAI_API_KEY in .env file or config.")

    # Set up VAD configuration
    if "popup_recorder" not in config:
        config["popup_recorder"] = {}

    config["popup_recorder"]["vad_enabled"] = not args.no_vad and args.time is None
    config["popup_recorder"]["silence_threshold"] = args.silence_threshold
    config["popup_recorder"]["silence_duration"] = args.silence_duration
    config["popup_recorder"]["min_recording_time"] = args.min_recording_time

    # Create recorder
    recorder = PopupRecorder(config)

    # Record and transcribe
    text = recorder.record_and_transcribe(duration=args.time)

    if text:
        # Output the transcription
        if args.output:
            with open(args.output, "w") as f:
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
    # Parse arguments
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    if args.silent:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    sys.exit(main())
