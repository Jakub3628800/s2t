# DesktopSTT

[![Tests](https://github.com/username/desktopstt/actions/workflows/tests.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml)
[![Release](https://github.com/username/desktopstt/actions/workflows/release.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/release.yml)

A desktop application for Linux that records speech and converts it to text using various speech recognition backends.

## Features

- **Popup Recorder**: A graphical popup window for recording with visual feedback
  - Voice activity detection (VAD) for automatic recording stop
  - Audio level visualization
  - Customizable silence detection settings
  - Silent mode for clean output

- **Headless Mode**: A terminal-based version without any GUI
  - Perfect for scripts and automation
  - Minimal dependencies
  - Clean output for piping to other commands

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/desktopstt.git
cd desktopstt

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

## Usage

### Popup Recorder

```bash
# Basic usage with voice activity detection
desktopstt-popup

# Silent mode with 3 seconds silence duration
desktopstt-popup --silent --silence-duration 3.0

# Start recording immediately without waiting for speech
desktopstt-popup --no-vad

# Using make
make run-popup
make run-popup-silent
```

### Headless Mode

```bash
# Basic usage
desktopstt-silent

# Using make
make run-silent
```

### Convenience Scripts

The repository includes two convenience scripts that can be installed to your PATH:

#### Option 1: Using the installation script

```bash
# Run the installation script
./install_scripts.sh
```

This script will:
1. Copy the scripts to your ~/bin directory
2. Make them executable
3. Add ~/bin to your PATH if it's not already there

#### Option 2: Manual installation

```bash
# Copy the scripts to your bin directory
cp desktopstt-popup-silent.sh ~/bin/desktopstt-popup-silent
cp desktopstt-silent.sh ~/bin/desktopstt-silent
chmod +x ~/bin/desktopstt-popup-silent ~/bin/desktopstt-silent

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

These scripts will:
1. Run the appropriate command
2. Suppress warnings and error messages
3. Pipe the output to `wtype` to automatically type the transcribed text at your cursor position

## API Key Setup

To use the Whisper API backend, you need to set your OpenAI API key:

### Option 1: Edit the config file
```bash
# Create the default config if it doesn't exist
python -m desktopstt.config

# Edit the config file
nano ~/.config/desktopstt/config.yaml
```

In the config file, set your API key:
```yaml
backends:
  whisper_api:
    api_key: 'your-api-key-here'
```

### Option 2: Set environment variable
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Option 3: Create a .env file
Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

## License

[MIT License](LICENSE)