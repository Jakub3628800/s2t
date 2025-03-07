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

# Run the headless recorder with wtype output
PYTHONWARNINGS=ignore python -m desktopstt.headless_recorder --silence-threshold 0.05 --silence-duration 3.0 --wtype --silent 2>/dev/null
