#!/bin/bash
# Example script that uses speech recognition to execute commands
# Usage: ./speech_to_command.sh

# Ensure the directory exists
mkdir -p $(dirname "$0")

echo "Speak a command to execute (e.g., 'echo hello world', 'ls -la', etc.)"
echo "Recording for 5 seconds..."

# Record speech and convert to text
COMMAND=$(desktopstt-cli --time 5 --ui)

if [ -z "$COMMAND" ]; then
    echo "No command detected. Exiting."
    exit 1
fi

echo "Detected command: $COMMAND"
echo "Do you want to execute this command? (y/n)"
read -r CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    echo "Executing command..."
    eval "$COMMAND"
else
    echo "Command execution cancelled."
fi
