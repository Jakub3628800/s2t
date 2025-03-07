#!/bin/bash

# Enable debug output
set -x

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
    exit 1
fi

# Path to the desktopstt repository
DESKTOPSTT_PATH="$HOME/repos/desktopstt"

# Change to the desktopstt directory
cd "$DESKTOPSTT_PATH" || { echo "Error: Could not find desktopstt repository at $DESKTOPSTT_PATH"; exit 1; }

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
    exit 1
fi

# Create a log file for debugging
LOG_FILE="/tmp/desktopstt-popup-debug.log"
echo "Starting desktopstt-popup-silent.sh at $(date)" > "$LOG_FILE"
echo "Working directory: $(pwd)" >> "$LOG_FILE"
echo "Python path: $("$DESKTOPSTT_PATH/.venv/bin/python" -c 'import sys; print(sys.path)')" >> "$LOG_FILE"
echo "API key loaded: ${OPENAI_API_KEY:0:5}..." >> "$LOG_FILE"

# Create a temporary file to capture the output
OUTPUT_FILE=$(mktemp)

# Run the immediate popup recorder and capture its output
PYTHONWARNINGS=ignore "$DESKTOPSTT_PATH/.venv/bin/python" -m desktopstt.immediate_popup --silence-threshold 0.05 --silence-duration 3.0 --debug > "$OUTPUT_FILE" 2>> "$LOG_FILE"
PYTHON_EXIT_CODE=$?

# Check if the Python script exited successfully
if [ $PYTHON_EXIT_CODE -ne 0 ]; then
    echo "Error: Python script exited with code $PYTHON_EXIT_CODE" >> "$LOG_FILE"
    notify-send -u critical "DesktopSTT Error" "Failed to transcribe audio. Check the log at $LOG_FILE"
    rm "$OUTPUT_FILE"
    exit $PYTHON_EXIT_CODE
fi

# Extract the transcription using the markers
if [ -s "$OUTPUT_FILE" ]; then
    # Look for the special markers in the output
    TRANSCRIPTION=$(grep -o "TRANSCRIPTION_START:.*:TRANSCRIPTION_END" "$OUTPUT_FILE" | sed 's/TRANSCRIPTION_START:\(.*\):TRANSCRIPTION_END/\1/')
    
    if [ -n "$TRANSCRIPTION" ]; then
        echo "Found transcription with markers: $TRANSCRIPTION" >> "$LOG_FILE"
    else
        # If no markers found, try to use the entire output
        TRANSCRIPTION=$(cat "$OUTPUT_FILE")
        echo "No markers found, using entire output: $TRANSCRIPTION" >> "$LOG_FILE"
    fi
else
    # If no output, try to extract from the log file
    TRANSCRIPTION_LINE=$(grep -o "TRANSCRIPTION_START:.*:TRANSCRIPTION_END" "$LOG_FILE" | sed 's/TRANSCRIPTION_START:\(.*\):TRANSCRIPTION_END/\1/')
    
    if [ -n "$TRANSCRIPTION_LINE" ]; then
        TRANSCRIPTION="$TRANSCRIPTION_LINE"
        echo "Extracted transcription from log: $TRANSCRIPTION" >> "$LOG_FILE"
    else
        # Try another approach - look for the text between "text" and "language" in the JSON response
        TRANSCRIPTION_LINE=$(grep -o '"text": "[^"]*"' "$LOG_FILE" | head -n 1 | sed 's/"text": "\(.*\)"/\1/')
        
        if [ -n "$TRANSCRIPTION_LINE" ]; then
            TRANSCRIPTION="$TRANSCRIPTION_LINE"
            echo "Extracted transcription from JSON in log: $TRANSCRIPTION" >> "$LOG_FILE"
        else
            TRANSCRIPTION=""
            echo "No transcription found in log" >> "$LOG_FILE"
        fi
    fi
fi

# Clean up the temporary file
rm "$OUTPUT_FILE"

# Check if we have a transcription
if [ -n "$TRANSCRIPTION" ] && [ "$TRANSCRIPTION" != "0 characters" ]; then
    echo "Typing transcription: $TRANSCRIPTION" >> "$LOG_FILE"
    echo "$TRANSCRIPTION" | wtype -
else
    echo "No transcription found or empty transcription" >> "$LOG_FILE"
    notify-send "DesktopSTT" "No speech detected or transcription was empty"
fi

# Check the exit code
EXIT_CODE=$?
echo "Exit code: $EXIT_CODE" >> "$LOG_FILE"
echo "Log file: $LOG_FILE"
