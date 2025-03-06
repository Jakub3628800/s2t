#!/bin/bash
# Example script that uses speech recognition to take notes
# Usage: ./speech_to_notes.sh [notes_file]

# Default notes file
NOTES_FILE=${1:-"$HOME/speech_notes.txt"}

# Ensure the directory exists
mkdir -p $(dirname "$NOTES_FILE")

echo "Speech Notes Taker"
echo "Press Ctrl+C to stop recording"
echo "Notes will be saved to: $NOTES_FILE"
echo ""
echo "Start speaking..."

# Add timestamp
echo "--- Notes from $(date) ---" >> "$NOTES_FILE"

# Record speech and append to notes file
desktopstt-cli --ui >> "$NOTES_FILE"

# Add a newline
echo "" >> "$NOTES_FILE"

echo "Notes saved to $NOTES_FILE"
echo "Content:"
echo "-------------------"
tail -n 10 "$NOTES_FILE"
echo "-------------------"
