"""
Audio recording functionality for S2T.
"""

import logging
import os
import tempfile
import threading
import wave
from datetime import datetime

import pyaudio

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Class to handle audio recording from microphone."""

    def __init__(self, config):
        """Initialize the audio recorder with the given configuration."""
        self.config = config
        self.audio_config = config["audio"]
        self.sample_rate = self.audio_config["sample_rate"]
        self.channels = self.audio_config["channels"]
        self.chunk_size = self.audio_config["chunk_size"]
        self.format = pyaudio.paInt16  # 16-bit audio
        self.device_index = self.audio_config["device_index"]

        self.pyaudio = None
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
        self.temp_file = None

    def start_recording(self, callback=None):
        """Start recording audio from the microphone."""
        if self.is_recording:
            logger.warning("Recording is already in progress")
            return False

        try:
            self.pyaudio = pyaudio.PyAudio()
            self.stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
            )

            self.frames = []
            self.is_recording = True

            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_thread, args=(callback,))
            self.recording_thread.daemon = True
            self.recording_thread.start()

            logger.info("Started audio recording")
            return True

        except Exception as e:
            logger.error(f"Error starting audio recording: {e}")
            self._cleanup()
            return False

    def stop_recording(self):
        """Stop recording audio and return the path to the recorded file."""
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None

        self.is_recording = False

        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)

        # Save the recorded audio to a temporary file
        temp_file = self._save_to_temp_file()

        # Clean up resources
        self._cleanup()

        return temp_file

    def _record_thread(self, callback=None):
        """Thread function for recording audio."""
        try:
            while self.is_recording:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)

                # Call the callback function if provided
                if callback:
                    callback(data)

        except Exception as e:
            logger.error(f"Error in recording thread: {e}")
            self.is_recording = False

    def _save_to_temp_file(self):
        """Save recorded audio to a temporary file and return the path."""
        if not self.frames:
            logger.warning("No audio data to save")
            return None

        try:
            # Create a temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"s2t_recording_{timestamp}.wav")

            # Save the audio data to the temporary file
            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b"".join(self.frames))

            logger.info(f"Saved recording to {temp_path}")
            return temp_path

        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")
            return None

    def _cleanup(self):
        """Clean up resources."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.debug(f"Error closing audio stream: {e}")
            self.stream = None

        if self.pyaudio:
            try:
                self.pyaudio.terminate()
            except Exception as e:
                logger.debug(f"Error terminating PyAudio: {e}")
            self.pyaudio = None

        self.frames = []
        self.is_recording = False
