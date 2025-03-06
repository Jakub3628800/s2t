#!/bin/bash
# Quick transcription script using DesktopSTT
# Usage: ./quick_transcribe.sh [duration_in_seconds] [silent]

# Default duration is 5 seconds
DURATION=${1:-5}

# Path to Python in the virtual environment
PYTHON_PATH="../.venv/bin/python"

# Check if silent mode is requested
if [ "$2" = "silent" ]; then
    SILENT="--silent"
    echo "Silent mode enabled. Recording for $DURATION seconds..."
else
    SILENT=""
    echo "Recording for $DURATION seconds..."
    echo "Please speak now..."
fi

# Record and transcribe
TRANSCRIPTION=$($PYTHON_PATH -m desktopstt.simple_cli --time $DURATION $SILENT)

# If not in silent mode, print formatted output
if [ -z "$SILENT" ]; then
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
else
    # In silent mode, just output the transcription
    echo "$TRANSCRIPTION"
fi
