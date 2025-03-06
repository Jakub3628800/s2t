#!/bin/bash

# Simple installation script for DesktopSTT convenience scripts

# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Copy scripts to bin directory
cp desktopstt-popup-silent.sh ~/bin/desktopstt-popup-silent
cp desktopstt-silent.sh ~/bin/desktopstt-silent

# Make scripts executable
chmod +x ~/bin/desktopstt-popup-silent ~/bin/desktopstt-silent

# Check if ~/bin is in PATH
if ! echo $PATH | grep -q "$HOME/bin"; then
    # Add ~/bin to PATH in the appropriate shell configuration file
    if [ -f ~/.zshrc ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
        echo "Added ~/bin to PATH in ~/.zshrc"
        echo "Please run 'source ~/.zshrc' to apply changes"
    elif [ -f ~/.bashrc ]; then
        echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
        echo "Added ~/bin to PATH in ~/.bashrc"
        echo "Please run 'source ~/.bashrc' to apply changes"
    else
        echo "Could not find .zshrc or .bashrc"
        echo "Please add the following line to your shell configuration file:"
        echo 'export PATH="$HOME/bin:$PATH"'
    fi
else
    echo "~/bin is already in PATH"
fi

echo "Installation complete!"
echo "You can now use the following commands from anywhere:"
echo "  desktopstt-popup-silent - Popup recorder with silent mode"
echo "  desktopstt-silent - Headless terminal-based version" 