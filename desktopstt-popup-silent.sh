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
    exit 1
fi

# Create a temporary file for the transcription
TEMP_OUTPUT=$(mktemp)

# Create a temporary Python script that uses popup_recorder with immediate recording
cat > /tmp/popup_recorder_immediate.py << 'EOF'
#!/usr/bin/env python3
"""
Modified popup recorder that starts recording immediately and automatically closes after transcription.
"""

import os
import sys
import time
import threading
import subprocess
import argparse
from desktopstt.popup_recorder import PopupRecorder, RecordingWindow
from desktopstt.config import load_config, DEFAULT_CONFIG_PATH
from desktopstt.utils import load_dotenv
from gi.repository import GLib

class ImmediateRecordingWindow(RecordingWindow):
    """Modified recording window that shows 'Recording in progress' instead of 'Waiting for speech'."""

    def __init__(self, on_stop_callback=None, title="DesktopSTT Recording"):
        super().__init__(on_stop_callback, title)
        # Set the VAD status to show recording in progress immediately
        self.update_vad_status(True)

class ImmediatePopupRecorder(PopupRecorder):
    """Modified popup recorder that starts recording immediately without waiting for speech."""

    def _show_window(self):
        """Show the recording window with immediate recording status."""
        self.window = ImmediateRecordingWindow(on_stop_callback=self._on_window_stop)
        self.window.connect("close-request", self._on_window_close)
        self.window.present()
        # Set speech detection to true immediately
        self.is_speech = True

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Immediate recording popup recorder')
    parser.add_argument('--output', type=str, help='Output file for transcription')
    parser.add_argument('--silence-threshold', type=float, default=0.05, help='Threshold for silence detection (0.0-1.0)')
    parser.add_argument('--silence-duration', type=float, default=3.0, help='Duration of silence before stopping (seconds)')
    args = parser.parse_args()

    # Load configuration
    config = load_config(DEFAULT_CONFIG_PATH)

    # Check if API key is set in environment variables
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPEN_API_KEY")
    if api_key:
        # Set the API key in the config
        config["backends"]["whisper_api"]["api_key"] = api_key

    # Set popup recorder configuration
    config["popup_recorder"] = config.get("popup_recorder", {})
    config["popup_recorder"]["silence_threshold"] = args.silence_threshold
    config["popup_recorder"]["silence_duration"] = args.silence_duration
    config["popup_recorder"]["vad_enabled"] = True
    config["popup_recorder"]["min_recording_time"] = 0.0  # Start VAD immediately

    # Create recorder
    recorder = ImmediatePopupRecorder(config)

    # Record and transcribe
    text = recorder.record_and_transcribe()

    # Write to output file if specified
    if text:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(text + "\n")  # Add newline at the end
        else:
            print(text, flush=True)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Run the custom script with the temporary output file
PYTHONWARNINGS=ignore .venv/bin/python /tmp/popup_recorder_immediate.py --output "$TEMP_OUTPUT" --silence-threshold 0.05 --silence-duration 3.0 2>/dev/null

# Check if the transcription was successful
if [ -s "$TEMP_OUTPUT" ]; then
    # Output the transcription using wtype
    (cat "$TEMP_OUTPUT"; printf "\n") | wtype -
fi

# Clean up temporary files
rm -f "$TEMP_OUTPUT"
