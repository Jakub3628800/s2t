#!/bin/bash
# Silent popup recorder example that suppresses ALSA warnings
# Usage: ./silent_popup.sh [duration_in_seconds]

# Default duration is 5 seconds (only used if --no-vad is specified)
DURATION=${1:-5}

# Path to Python in the virtual environment
PYTHON_PATH="../.venv/bin/python"

# Suppress ALSA warnings
export PYTHONWARNINGS="ignore"

echo "DesktopSTT Silent Popup Recorder"
echo "-------------------------------"
echo "A window will appear showing the recording in progress."
echo "The recording will automatically stop after detecting silence."
echo ""
echo "Starting recording in 3 seconds..."
sleep 3

# Check if --no-vad flag is provided
if [ "$2" = "--no-vad" ]; then
    # Record and transcribe with popup window, suppressing stderr, with fixed duration
    TRANSCRIPTION=$($PYTHON_PATH -m desktopstt.popup_recorder --time $DURATION --silent --no-vad 2>/dev/null)
    echo "Recording for fixed duration of ${DURATION}s (VAD disabled)"
else
    # Record and transcribe with popup window, suppressing stderr, with VAD
    TRANSCRIPTION=$($PYTHON_PATH -m desktopstt.popup_recorder --silent 2>/dev/null)
    echo "Recording with voice activity detection (will stop after silence)"
fi

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
