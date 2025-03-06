#!/bin/bash
# Example script demonstrating the popup recorder
# Usage: ./popup_transcribe.sh [duration_in_seconds] [--no-vad]

# Default duration is 10 seconds (only used if --no-vad is specified)
DURATION=${1:-10}

# Path to Python in the virtual environment
PYTHON_PATH=".venv/bin/python"

echo "DesktopSTT Popup Recorder Example"
echo "--------------------------------"
echo "A window will appear showing the recording in progress."

# Check if --no-vad flag is provided
if [ "$2" = "--no-vad" ]; then
    echo "You can either wait for the timer (${DURATION}s) or click 'Stop Recording'."
    VAD_FLAG="--no-vad --time $DURATION"
    VAD_MSG="Recording for fixed duration of ${DURATION}s (VAD disabled)"
else
    echo "Recording will automatically stop after detecting silence."
    echo "The audio level meter shows your voice activity."
    VAD_FLAG=""
    VAD_MSG="Recording with voice activity detection (will stop after silence)"
fi

echo ""
echo "Starting recording in 3 seconds..."
sleep 3

echo "$VAD_MSG"

# Record and transcribe with popup window
TRANSCRIPTION=$($PYTHON_PATH -m desktopstt.popup_recorder $VAD_FLAG)

echo ""
echo "Transcription:"
echo "--------------"
echo "$TRANSCRIPTION"
echo "--------------"

# Copy to clipboard if xclip is available
if command -v xclip &> /dev/null; then
    echo "$TRANSCRIPTION" | xclip -selection clipboard
    echo "Transcription copied to clipboard!"
fi
