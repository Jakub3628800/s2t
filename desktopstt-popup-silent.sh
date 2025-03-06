#!/bin/bash

# Path to the desktopstt repository
DESKTOPSTT_PATH="$HOME/repos/desktopstt"

# Change to the desktopstt directory
cd "$DESKTOPSTT_PATH" || { echo "Error: Could not find desktopstt repository at $DESKTOPSTT_PATH"; exit 1; }

# Run the popup recorder with silent mode, 3 seconds silence duration, and no voice activity detection
# This will start recording immediately without waiting for speech
PYTHONWARNINGS=ignore .venv/bin/python -m desktopstt.popup_recorder --silent --silence-duration 3.0 --no-vad 2>/dev/null | wtype -
