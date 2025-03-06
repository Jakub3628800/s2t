#!/bin/bash
# Silent popup recorder example that suppresses ALSA warnings
# Usage: ./silent_pipe.sh

# Path to Python in the virtual environment
PYTHON_PATH="../.venv/bin/python"

# Suppress ALSA warnings
export PYTHONWARNINGS="ignore"

echo "This example demonstrates using DesktopSTT with silent mode."
echo "Speak a command after the prompt, and it will be executed."
echo ""
echo "Recording for 5 seconds..."

# Record speech and convert to text using silent mode
# Redirect stderr to /dev/null to suppress ALSA warnings
COMMAND=$($PYTHON_PATH -m desktopstt.simple_cli --time 5 --silent 2>/dev/null)

# Trim whitespace
COMMAND=$(echo "$COMMAND" | xargs)

if [ -z "$COMMAND" ]; then
    echo "No command detected. Exiting."
    exit 1
fi

echo "Detected command: '$COMMAND'"
echo "Do you want to execute this command? (y/n)"
read -r CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "Executing command..."
    eval "$COMMAND"
else
    echo "Command execution cancelled."
fi
