#!/bin/bash

# Ensure we have a proper environment when launched from Dmenu/Rofi
# Source user profile to get environment variables
if [ -f "$HOME/.profile" ]; then
    . "$HOME/.profile"
fi

# Ensure XDG_RUNTIME_DIR is set (needed for Wayland)
if [ -z "$XDG_RUNTIME_DIR" ]; then
    export XDG_RUNTIME_DIR=/run/user/$(id -u)
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
if [ -d "$DESKTOPSTT_PATH/.venv" ] && [ ! -n "$VIRTUAL_ENV" ]; then
    . "$DESKTOPSTT_PATH/.venv/bin/activate"
fi

# Load OpenAI API key from .env file
if [ -f "$DESKTOPSTT_PATH/.env" ]; then
    # Export environment variables from .env file
    export $(grep -v '^#' "$DESKTOPSTT_PATH/.env" | xargs)
    echo "Loaded API key from .env file"
else
    echo "Error: .env file not found at $DESKTOPSTT_PATH/.env"
    notify-send -u critical "DesktopSTT Error" "API key not found. Please create a .env file with your OpenAI API key."
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
    notify-send -u critical "DesktopSTT Error" "API key not found in .env file. Please add OPENAI_API_KEY or OPEN_API_KEY."
    exit 1
fi

# Create a temporary file for the transcription
TEMP_OUTPUT=$(mktemp)

# Create a temporary file for signaling recording stopped
SIGNAL_FILE=$(mktemp)

# Create a log file for debugging
LOG_FILE="$HOME/desktopstt_dmenu.log"
echo "Starting desktopstt-silent.sh at $(date)" > "$LOG_FILE"
echo "Environment: WAYLAND_DISPLAY=$WAYLAND_DISPLAY, XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR" >> "$LOG_FILE"
echo "Working directory: $(pwd)" >> "$LOG_FILE"
echo "API key loaded: ${API_KEY:0:5}..." >> "$LOG_FILE"
echo "API key variable: ${OPEN_API_KEY:+OPEN_API_KEY}${OPENAI_API_KEY:+OPENAI_API_KEY}" >> "$LOG_FILE"

# Function to show notifications in a compatible way
show_notification() {
    local title="$1"
    local message="$2"
    local icon="$3"
    local timeout="$4"
    
    # Try different notification methods
    if command -v dunstify >/dev/null 2>&1; then
        # Use dunstify if available (more features)
        dunstify -t "$timeout" -i "$icon" "$title" "$message"
    elif command -v notify-send >/dev/null 2>&1; then
        # Fallback to notify-send with basic options
        notify-send -t "$timeout" "$title" "$message"
    else
        # No notification system available, just print to stderr
        echo "$title: $message" >&2
    fi
    
    # Log notification for debugging
    echo "Notification: $title - $message" >> "$LOG_FILE"
}

# Show notification that recording is starting
show_notification "🔴 Recording" "Speak now. Will stop after 3s of silence." "microphone-sensitivity-high" 2000

# Create a temporary Python script that uses popup_recorder but disables the GUI
cat > /tmp/silent_recorder.py << 'EOF'
#!/usr/bin/env python3
"""
Silent recorder that uses popup_recorder functionality but disables the GUI.
"""

import os
import sys
import time
import numpy as np
import threading
from desktopstt.backends import get_backend
from desktopstt.audio import AudioRecorder
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv

# Silence detection parameters
SILENCE_THRESHOLD = 0.1
SILENCE_DURATION = 3.0
MIN_RECORDING_TIME = 1.0

def main():
    # Get output file and signal file from command line
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    signal_file = sys.argv[2] if len(sys.argv) > 2 else None
    log_file = sys.argv[3] if len(sys.argv) > 3 else None
    api_key = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Log function for debugging
    def log(message):
        if log_file:
            with open(log_file, 'a') as f:
                f.write(f"{message}\n")
    
    log(f"Python script started with args: {len(sys.argv)} arguments")
    log(f"Environment: WAYLAND_DISPLAY={os.environ.get('WAYLAND_DISPLAY')}, XDG_RUNTIME_DIR={os.environ.get('XDG_RUNTIME_DIR')}")
    
    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)
    log(f"Loaded config from {DEFAULT_CONFIG_PATH}")
    
    # Check if API key is provided as argument
    if api_key:
        config["backends"]["whisper_api"]["api_key"] = api_key
        log(f"API key provided as argument: {api_key[:5]}...")
    else:
        # Check if API key is set in environment variables (try both possible names)
        env_api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
        if env_api_key:
            # Set the API key in the config
            config["backends"]["whisper_api"]["api_key"] = env_api_key
            log(f"API key found in environment variables: {env_api_key[:5]}...")
        else:
            log("WARNING: No API key found in environment variables or arguments")
    
    # Create backend and recorder
    try:
        backend = get_backend(config)
        log(f"Using backend: {backend.__class__.__name__}")
    except Exception as e:
        log(f"Error creating backend: {e}")
        return 1
    
    try:
        recorder = AudioRecorder(config)
        log("Created audio recorder")
    except Exception as e:
        log(f"Error creating audio recorder: {e}")
        return 1
    
    # Variables for silence detection
    is_recording = False
    is_speech = False
    silence_start_time = None
    recording_start_time = None
    stop_event = threading.Event()
    audio_file = None
    
    # Define a callback to process audio frames for VAD
    def process_audio(in_data):
        nonlocal is_speech, silence_start_time
        
        if not is_recording:
            return None
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Calculate audio level (RMS)
        if len(audio_data) > 0:
            rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32) / 32768.0)))
            level = min(rms * 5.0, 1.0)  # Scale for better visualization
            
            # Voice activity detection
            if recording_start_time is not None:
                current_time = time.time()
                recording_duration = current_time - recording_start_time
                
                # Only start VAD after minimum recording time
                if recording_duration >= MIN_RECORDING_TIME:
                    is_speech_now = level > SILENCE_THRESHOLD
                    
                    if is_speech_now:
                        # Speech detected
                        is_speech = True
                        silence_start_time = None
                    else:
                        # Silence detected
                        if is_speech:
                            # Transition from speech to silence
                            is_speech = False
                            silence_start_time = current_time
                            log(f"Silence started at {current_time}")
                        elif silence_start_time is not None:
                            # Continued silence
                            silence_duration = current_time - silence_start_time
                            
                            # Stop recording if silence duration exceeds threshold
                            if silence_duration >= SILENCE_DURATION:
                                log(f"Stopping after {silence_duration:.1f}s of silence")
                                # Signal that recording is stopping by touching the signal file
                                if signal_file:
                                    with open(signal_file, 'w') as f:
                                        f.write("stopped")
                                stop_event.set()
        
        return None
    
    # Start recording
    if not backend.is_available():
        log("Speech-to-text backend is not available")
        log(f"API key set: {bool(config['backends']['whisper_api']['api_key'])}")
        return 1
    
    try:
        success = recorder.start_recording(callback=process_audio)
        if success:
            is_recording = True
            recording_start_time = time.time()
            is_speech = False
            silence_start_time = None
            log(f"Started recording at {recording_start_time}")
        else:
            log("Failed to start recording")
            return 1
    except Exception as e:
        log(f"Error starting recording: {e}")
        return 1
    
    # Wait for the stop event or user interrupt
    try:
        log("Waiting for stop event")
        stop_event.wait()
        log("Stop event received")
    except KeyboardInterrupt:
        log("Keyboard interrupt received")
        pass
    except Exception as e:
        log(f"Error while waiting: {e}")
    
    # Stop recording
    try:
        if is_recording:
            log("Stopping recording")
            audio_file = recorder.stop_recording()
            is_recording = False
            if audio_file:
                log(f"Recording saved to {audio_file}")
            else:
                log("Failed to save recording")
    except Exception as e:
        log(f"Error stopping recording: {e}")
    
    # Transcribe the audio
    if audio_file:
        try:
            log("Transcribing audio")
            result = backend.transcribe(audio_file)
            text = result.get('text', '')
            
            if text:
                log(f"Transcription: {text}")
                # Write to output file if specified
                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(text + "\n")  # Add newline at the end
                    log(f"Wrote transcription to {output_file}")
                    return 0
                else:
                    # Print to stdout
                    print(text, flush=True)
                    log("Printed transcription to stdout")
                    return 0
            else:
                log("Empty transcription result")
        except Exception as e:
            log(f"Error transcribing audio: {e}")
    else:
        log("No audio file to transcribe")
    
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Get output file and log file from command line
        log_file = sys.argv[3] if len(sys.argv) > 3 else None
        if log_file:
            with open(log_file, 'a') as f:
                f.write(f"Unhandled exception: {e}\n")
        sys.exit(1)
EOF

# Run the custom script with the temporary output file
echo "Running Python script..." >> "$LOG_FILE"
PYTHONWARNINGS=ignore .venv/bin/python /tmp/silent_recorder.py "$TEMP_OUTPUT" "$SIGNAL_FILE" "$LOG_FILE" "$API_KEY" 2>>"$LOG_FILE" &
PID=$!

# Monitor the signal file to show notification when recording stops
echo "Monitoring signal file..." >> "$LOG_FILE"
while kill -0 $PID 2>/dev/null; do
    if [ -s "$SIGNAL_FILE" ]; then
        # Show notification that recording is stopping
        show_notification "Recording Stopped" "Transcribing audio..." "microphone-sensitivity-muted" 2000
        break
    fi
    sleep 0.1
done

# Wait for the process to complete
echo "Waiting for process to complete..." >> "$LOG_FILE"
wait $PID
EXIT_CODE=$?
echo "Process completed with exit code: $EXIT_CODE" >> "$LOG_FILE"

# Check if the transcription was successful
if [ -s "$TEMP_OUTPUT" ]; then
    # Show notification that transcription is complete
    show_notification "Transcription Complete" "Text has been typed" "document-edit" 2000
    
    # Log the transcription
    echo "Transcription content:" >> "$LOG_FILE"
    cat "$TEMP_OUTPUT" >> "$LOG_FILE"
    
    # Output the transcription using wtype
    echo "Running wtype..." >> "$LOG_FILE"
    # Add a newline character after the transcription
    (cat "$TEMP_OUTPUT"; echo -n "\n") | wtype -
    WTYPE_EXIT=$?
    echo "wtype exit code: $WTYPE_EXIT" >> "$LOG_FILE"
else
    # Show error notification
    show_notification "Transcription Failed" "No text was produced" "dialog-error" 3000
    echo "Transcription failed: empty output file" >> "$LOG_FILE"
fi

# Clean up temporary files
rm -f "$TEMP_OUTPUT" "$SIGNAL_FILE"
echo "Script completed at $(date)" >> "$LOG_FILE" 