#!/bin/bash

# Ensure we have a proper environment when launched from Dmenu/Rofi
# Source user profile to get environment variables
if [ -f "$HOME/.profile" ]; then
    . "$HOME/.profile"
fi

# Ensure XDG_RUNTIME_DIR is set (needed for Wayland)
if [ -z "$XDG_RUNTIME_DIR" ]; then
    XDG_RUNTIME_DIR="/run/user/$(id -u)"
    export XDG_RUNTIME_DIR
fi

# Ensure WAYLAND_DISPLAY is set if running on Wayland
if [ -z "$WAYLAND_DISPLAY" ] && [ -n "$SWAYSOCK" ]; then
    export WAYLAND_DISPLAY=wayland-0
fi

# Check for wtype availability
if ! command -v wtype >/dev/null 2>&1; then
    echo "Error: wtype is not installed or not in PATH. Please install wtype."
    notify-send -u critical "DesktopSTT Error" "wtype is not installed or not in PATH. Please install wtype."
    exit 1
fi

# Path to the desktopstt repository
DESKTOPSTT_PATH="$HOME/repos/desktopstt"

# Change to the desktopstt directory
cd "$DESKTOPSTT_PATH" || {
    echo "Error: Could not find desktopstt repository at $DESKTOPSTT_PATH"
    notify-send -u critical "DesktopSTT Error" "Could not find desktopstt repository at $DESKTOPSTT_PATH"
    exit 1
}

# Ensure Python virtual environment is activated
if [ -d "$DESKTOPSTT_PATH/.venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    . "$DESKTOPSTT_PATH/.venv/bin/activate"
fi

# Load OpenAI API key from .env file
if [ -f "$DESKTOPSTT_PATH/.env" ]; then
    # Export environment variables from .env file
    export "$(grep -v '^#' "$DESKTOPSTT_PATH/.env" | xargs)"
    echo "Loaded API key from .env file"
else
    echo "Error: .env file not found at $DESKTOPSTT_PATH/.env"
    notify-send -u critical "DesktopSTT Error" ".env file not found at $DESKTOPSTT_PATH/.env"
    exit 1
fi

# Verify that we have an API key (check both possible variable names)
API_KEY=""
if [ -n "$OPENAI_API_KEY" ]; then
    API_KEY="$OPENAI_API_KEY"
elif [ -n "$OPEN_API_KEY" ]; then
    API_KEY="$OPEN_API_KEY"
    # Also set OPENAI_API_KEY for compatibility
    export OPENAI_API_KEY="$OPEN_API_KEY"
fi

if [ -z "$API_KEY" ]; then
    echo "Error: Neither OPENAI_API_KEY nor OPEN_API_KEY found in .env file"
    notify-send -u critical "DesktopSTT Error" "Neither OPENAI_API_KEY nor OPEN_API_KEY found in .env file"
    exit 1
fi

# Create temporary files
TEMP_OUTPUT=$(mktemp)
SIGNAL_FILE=$(mktemp)
LOG_FILE=$(mktemp)

# Log environment information
{
    echo "Starting DesktopSTT Silent Recorder"
    echo "Date: $(date)"
    echo "Environment: WAYLAND_DISPLAY=$WAYLAND_DISPLAY, XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR"
    echo "API Key: ${API_KEY:0:5}..."
} >> "$LOG_FILE"

# Create a temporary Python script for silent recording
cat > /tmp/silent_recorder.py << 'EOF'
#!/usr/bin/env python3
"""
Silent recorder for DesktopSTT.
Records audio without a GUI and transcribes it.
"""

import os
import sys
import time
import signal
import logging
import numpy as np
from desktopstt.audio import AudioRecorder
from desktopstt.backends import get_backend
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=sys.argv[3] if len(sys.argv) > 3 else None
)
logger = logging.getLogger(__name__)

class SilentRecorder:
    """Records audio silently and transcribes it."""

    def __init__(self, config):
        """Initialize the recorder with the given configuration."""
        self.config = config
        self.backend = get_backend(config)
        self.audio_recorder = AudioRecorder(config)
        self.is_recording = False
        self.audio_file = None
        self.result_text = None

        # Set up VAD configuration
        self.vad_enabled = config.get("silent_recorder", {}).get("vad_enabled", True)
        self.silence_threshold = config.get("silent_recorder", {}).get("silence_threshold", 0.1)
        self.silence_duration = config.get("silent_recorder", {}).get("silence_duration", 5.0)
        self.min_recording_time = config.get("silent_recorder", {}).get("min_recording_time", 3.0)

        # Initialize VAD state
        self.is_speech = False
        self.silence_start_time = None
        self.recording_start_time = None
        self.should_stop = False

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
                            logger.debug("Speech detected")
                        else:
                            # Silence detected
                            if self.is_speech:
                                # Transition from speech to silence
                                self.is_speech = False
                                self.silence_start_time = current_time
                                logger.debug("Silence started")
                            elif self.silence_start_time is not None:
                                # Continued silence
                                silence_duration = current_time - self.silence_start_time
                                logger.debug(f"Silence duration: {silence_duration:.1f}s")

                                # Stop recording if silence duration exceeds threshold
                                if silence_duration >= self.silence_duration:
                                    logger.info(f"Stopping recording after {silence_duration:.1f}s of silence")
                                    self.should_stop = True

            return None

        success = self.audio_recorder.start_recording(callback=process_audio)
        if success:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.is_speech = False
            self.silence_start_time = None
            self.should_stop = False
            logger.info("Started recording")
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
            text = result.get('text', '')

            if not text:
                logger.error("No transcription result")
                return None

            logger.info(f"Transcription successful: {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

    def wait_for_silence(self):
        """Wait for silence to be detected."""
        logger.info("Waiting for silence...")

        while self.is_recording and not self.should_stop:
            time.sleep(0.1)

            # Check if we should stop due to an external signal
            if os.path.exists(sys.argv[2]) and os.path.getsize(sys.argv[2]) > 0:
                logger.info("Received stop signal from external file")
                return True

        return True

    def record_and_transcribe(self):
        """Record audio and transcribe it."""
        # Start recording
        if not self.start_recording():
            logger.error("Failed to start recording")
            return None

        try:
            # Wait for silence to be detected
            self.wait_for_silence()

            # Stop recording
            audio_file = self.stop_recording()

            # Check if we have an audio file
            if not audio_file:
                logger.error("No audio file was created")
                return None

            # Transcribe the audio
            self.result_text = self.transcribe(audio_file)
            return self.result_text

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


def main():
    """Command-line entry point."""
    # Check if we have enough arguments
    if len(sys.argv) < 2:
        print("Usage: silent_recorder.py <output_file> <signal_file> <log_file> [api_key]")
        return 1

    # Get the output file path
    output_file = sys.argv[1]

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Check if API key is provided as an argument
    if len(sys.argv) > 4:
        api_key = sys.argv[4]
        config["backends"]["whisper_api"]["api_key"] = api_key

    # Set up silent recorder configuration
    if "silent_recorder" not in config:
        config["silent_recorder"] = {}

    config["silent_recorder"]["vad_enabled"] = True
    config["silent_recorder"]["silence_threshold"] = 0.05
    config["silent_recorder"]["silence_duration"] = 3.0
    config["silent_recorder"]["min_recording_time"] = 1.0

    # Create recorder
    recorder = SilentRecorder(config)

    # Record and transcribe
    text = recorder.record_and_transcribe()

    if text:
        # Output the transcription
        with open(output_file, 'w') as f:
            f.write(text)
        logger.info(f"Transcription saved to {output_file}")
        return 0
    else:
        logger.error("Failed to transcribe audio")
        return 1


if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the silent recorder in the background
PYTHONWARNINGS=ignore .venv/bin/python /tmp/silent_recorder.py "$TEMP_OUTPUT" "$SIGNAL_FILE" "$LOG_FILE" "$API_KEY" &
PID=$!

# Show notification
notify-send -u low "DesktopSTT" "Recording started. Speak now..."

# Wait for the process to finish
wait $PID
EXIT_CODE=$?

# Check if the transcription was successful
if [ -s "$TEMP_OUTPUT" ]; then
    # Show notification
    notify-send -u low "DesktopSTT" "Transcription successful"

    # Log success
    {
        echo "Transcription successful"
        echo "Transcription content:"
        cat "$TEMP_OUTPUT"
    } >> "$LOG_FILE"

    # Output the transcription using wtype
    (cat "$TEMP_OUTPUT"; printf "\n") | wtype -
else
    # Show error notification
    notify-send -u critical "DesktopSTT Error" "Failed to transcribe audio"

    # Log error
    echo "Transcription failed with exit code $EXIT_CODE" >> "$LOG_FILE"
fi

# Clean up temporary files
rm -f "$TEMP_OUTPUT" "$SIGNAL_FILE"
# Keep the log file for debugging
echo "Log file: $LOG_FILE"
