#!/bin/bash

# Path to the desktopstt repository
DESKTOPSTT_PATH="$HOME/repos/desktopstt"

# Change to the desktopstt directory
cd "$DESKTOPSTT_PATH" || { echo "Error: Could not find desktopstt repository at $DESKTOPSTT_PATH"; exit 1; }

# Run the headless version
# This will record audio and transcribe it without any GUI
PYTHONWARNINGS=ignore .venv/bin/python -m desktopstt.truly_silent 2>/dev/null | wtype - 