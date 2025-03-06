#!/bin/bash
# Example script that uses the simple CLI for speech recognition to execute commands
# Usage: ./simple_speech_to_command.sh

# Ensure the directory exists
mkdir -p $(dirname "$0")

echo "Speak a command to execute (e.g., 'echo hello world', 'ls -la', etc.)"
echo "Recording for 5 seconds..."

# Record speech and convert to text using the simple CLI
COMMAND=$(python3 -m desktopstt.simple_cli --time 5)

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
