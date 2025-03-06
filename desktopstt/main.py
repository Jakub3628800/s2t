#!/usr/bin/env python3
"""
Main entry point for the DesktopSTT application.
"""

import sys
import logging
import argparse
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from desktopstt.ui.app_window import AppWindow
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Desktop Speech-to-Text Application')
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
        '--cli',
        action='store_true',
        help='Run in command-line mode (no GUI, output to stdout)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout in CLI mode)'
    )
    parser.add_argument(
        '--record-time',
        type=float,
        help='Record for specified number of seconds and then stop (CLI mode only)'
    )
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Load configuration
    config = load_config(args.config)

    # Check if we're running in CLI mode
    if args.cli:
        return run_cli_mode(args, config)
    else:
        return run_gui_mode(args, config)

def run_cli_mode(args, config):
    """Run the application in command-line mode."""
    logger.info("Running in CLI mode")

    # Initialize components
    recorder = AudioRecorder(config)
    backend = get_backend(config)

    if not backend.is_available():
        logger.error("Speech-to-text backend is not available")
        return 1

    # Start recording
    logger.info("Starting recording...")
    if not recorder.start_recording():
        logger.error("Failed to start recording")
        return 1

    # If record time is specified, wait for that duration
    if args.record_time:
        import time
        logger.info(f"Recording for {args.record_time} seconds...")
        time.sleep(args.record_time)
    else:
        # Otherwise, wait for user to press Enter
        logger.info("Recording... Press Enter to stop")
        try:
            input()
        except KeyboardInterrupt:
            pass

    # Stop recording
    logger.info("Stopping recording...")
    audio_file = recorder.stop_recording()

    if not audio_file:
        logger.error("Failed to save recording")
        return 1

    logger.info(f"Saved recording to {audio_file}")

    # Transcribe the audio
    logger.info("Transcribing audio...")
    try:
        result = backend.transcribe(audio_file)
        text = result.get('text', '')

        if not text:
            logger.error("No transcription result")
            return 1

        # Output the transcription
        if args.output:
            with open(args.output, 'w') as f:
                f.write(text)
            logger.info(f"Transcription saved to {args.output}")
        else:
            # Output to stdout
            print(text)

        return 0

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return 1

def run_gui_mode(args, config):
    """Run the application in GUI mode."""
    logger.info("Running in GUI mode")

    # Create and run the application
    app = Gtk.Application(application_id='com.github.desktopstt')
    app.connect('activate', on_activate, config)

    return app.run(sys.argv)

def on_activate(app, config):
    """Callback for application activation."""
    win = AppWindow(app, config)
    win.present()

if __name__ == "__main__":
    sys.exit(main())
