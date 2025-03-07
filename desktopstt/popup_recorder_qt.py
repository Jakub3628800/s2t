#!/usr/bin/env python3
"""
Popup recorder for DesktopSTT using Qt/PySide6 with Wayland support.
Shows a window during recording with a stop button and recording indicator.
"""

import os
import sys
import time
import logging
import argparse
import signal
import threading
import tempfile
from datetime import datetime
import numpy as np

# Import Qt modules
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QWidget, QProgressBar
)
from PySide6.QtGui import QFont, QColor, QPalette

# Import DesktopSTT modules
from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Record audio and transcribe it with a popup window (Qt/Wayland version).')
parser.add_argument(
    '--time',
    type=float,
    default=None,
    help='Maximum recording time in seconds (default: no limit)'
)
parser.add_argument(
    '--silence-duration',
    type=float,
    default=2.0,
    help='Duration of silence to stop recording (default: 2.0 seconds)'
)
parser.add_argument(
    '--silent',
    action='store_true',
    help='Silent mode (no voice activity detection)'
)
parser.add_argument(
    '--output',
    type=str,
    default=None,
    help='Output file for transcription (default: print to stdout)'
)
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

# Signal handler for communication between threads
class SignalHandler(QObject):
    recording_level_changed = Signal(float)
    recording_stopped = Signal(str)
    transcription_complete = Signal(str)

# Main window class
class RecorderWindow(QMainWindow):
    def __init__(self, args, config, signal_handler):
        super().__init__()
        
        self.args = args
        self.config = config
        self.signal_handler = signal_handler
        self.recorder = None
        self.recording = False
        self.recording_thread = None
        self.transcription_thread = None
        self.temp_file = None
        
        # Set up UI
        self.init_ui()
        
        # Connect signals
        self.signal_handler.recording_level_changed.connect(self.update_level)
        self.signal_handler.recording_stopped.connect(self.handle_recording_stopped)
        self.signal_handler.transcription_complete.connect(self.handle_transcription_complete)
        
        # Set up Wayland-specific settings if running on Wayland
        self.setup_wayland()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('DesktopSTT Recording')
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel('Ready to record')
        self.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        self.status_label.setFont(font)
        main_layout.addWidget(self.status_label)
        
        # Level meter
        self.level_meter = QProgressBar()
        self.level_meter.setMinimum(0)
        self.level_meter.setMaximum(100)
        self.level_meter.setValue(0)
        main_layout.addWidget(self.level_meter)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Record/Stop button
        self.record_button = QPushButton('Start Recording')
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        
        main_layout.addLayout(button_layout)
        
        # Transcription result
        self.result_label = QLabel('')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        main_layout.addWidget(self.result_label)
        
        self.setCentralWidget(central_widget)
        
    def setup_wayland(self):
        # Check if running on Wayland
        if os.environ.get('WAYLAND_DISPLAY'):
            logger.info("Running on Wayland")
            # Set Qt platform to Wayland
            os.environ['QT_QPA_PLATFORM'] = 'wayland'
        else:
            logger.info("Not running on Wayland")
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        logger.info("Starting recording")
        self.recording = True
        self.record_button.setText('Stop Recording')
        self.status_label.setText('Recording...')
        
        # Create a temporary file for the recording
        fd, temp_path = tempfile.mkstemp(suffix='.wav', prefix='desktopstt_recording_')
        os.close(fd)
        self.temp_file = temp_path
        
        # Create and start the recorder
        self.recorder = AudioRecorder(
            output_file=self.temp_file,
            vad_enabled=not self.args.silent,
            silence_duration=self.args.silence_duration,
            max_duration=self.args.time
        )
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(
            target=self.recording_worker,
            daemon=True
        )
        self.recording_thread.start()
        
        # Start a timer to update the level meter
        self.level_timer = QTimer()
        self.level_timer.timeout.connect(self.check_recording_level)
        self.level_timer.start(50)  # Update every 50ms
    
    def recording_worker(self):
        try:
            self.recorder.record()
            logger.info(f"Recording saved to {self.temp_file}")
            self.signal_handler.recording_stopped.emit(self.temp_file)
        except Exception as e:
            logger.error(f"Error during recording: {e}")
            self.signal_handler.recording_stopped.emit("")
    
    def check_recording_level(self):
        if self.recorder and self.recording:
            level = self.recorder.get_current_level()
            self.signal_handler.recording_level_changed.emit(level)
    
    def update_level(self, level):
        # Convert level to a percentage (0-100)
        level_percent = min(100, int(level * 100))
        self.level_meter.setValue(level_percent)
        
        # Change color based on level
        palette = QPalette()
        if level_percent < 30:
            color = QColor(0, 255, 0)  # Green
        elif level_percent < 70:
            color = QColor(255, 255, 0)  # Yellow
        else:
            color = QColor(255, 0, 0)  # Red
        
        palette.setColor(QPalette.Highlight, color)
        self.level_meter.setPalette(palette)
    
    def stop_recording(self):
        if self.recorder:
            logger.info("Stopping recording")
            self.recorder.stop()
            self.recording = False
            self.record_button.setText('Start Recording')
            self.status_label.setText('Processing...')
            
            if self.level_timer:
                self.level_timer.stop()
    
    def handle_recording_stopped(self, file_path):
        if not file_path:
            self.status_label.setText('Recording failed')
            return
        
        self.status_label.setText('Transcribing...')
        
        # Start transcription in a separate thread
        self.transcription_thread = threading.Thread(
            target=self.transcription_worker,
            args=(file_path,),
            daemon=True
        )
        self.transcription_thread.start()
    
    def transcription_worker(self, file_path):
        try:
            logger.info(f"Transcribing audio file: {file_path}")
            backend = get_backend(self.config)
            result = backend.transcribe(file_path)
            logger.info(f"Transcription successful: {len(result)} characters")
            self.signal_handler.transcription_complete.emit(result)
            
            # Write to output file if specified
            if self.args.output:
                with open(self.args.output, 'w') as f:
                    f.write(result)
                logger.info(f"Transcription saved to {self.args.output}")
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            self.signal_handler.transcription_complete.emit("")
    
    def handle_transcription_complete(self, text):
        if not text:
            self.status_label.setText('Transcription failed')
            return
        
        self.status_label.setText('Transcription complete')
        self.result_label.setText(text)
        
        # Clean up temporary file
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
                logger.debug(f"Removed temporary file: {self.temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")
    
    def closeEvent(self, event):
        # Stop recording if active
        if self.recording:
            self.stop_recording()
        
        # Clean up temporary file
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
                logger.debug(f"Removed temporary file: {self.temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")
        
        event.accept()

def main():
    # Parse arguments
    args = parser.parse_args()
    
    # Set up logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load environment variables
    load_dotenv()
    logger.info("Loaded environment variables from .env")
    
    # Load configuration
    config = load_config(args.config)
    
    # Check for API key
    if 'OPENAI_API_KEY' in os.environ:
        logger.info("Using OpenAI API key from environment variables")
    else:
        logger.warning("OpenAI API key not found in environment variables")
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Force Wayland backend if available
    if os.environ.get('WAYLAND_DISPLAY'):
        os.environ['QT_QPA_PLATFORM'] = 'wayland'
        logger.info("Setting Qt platform to Wayland")
    
    # Create signal handler
    signal_handler = SignalHandler()
    
    # Create and show the main window
    window = RecorderWindow(args, config, signal_handler)
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 