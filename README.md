# DesktopSTT

[![Tests](https://github.com/username/desktopstt/actions/workflows/tests.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml)
[![Release](https://github.com/username/desktopstt/actions/workflows/release.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/release.yml)

A desktop application for Linux that records speech and converts it to text using OpenAI's Whisper API. It provides both GUI and headless modes for flexible usage.

## Features

- **Popup Recorder**: A graphical popup window for recording with visual feedback
  - Voice activity detection (VAD) for automatic recording stop
  - Audio level visualization
  - Customizable silence detection settings
  - Immediate recording mode (starts recording as soon as the window opens)
  - Silent mode for clean output

- **Headless Mode**: A terminal-based version without any GUI
  - Perfect for scripts and automation
  - Minimal dependencies
  - Clean output for piping to other commands

- **Convenience Scripts**:
  - `desktopstt-popup-silent.sh`: Optimized popup recorder that starts recording immediately
  - `desktopstt-silent.sh`: Headless recorder for terminal usage

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

- [Quick Start Guide](docs/quick_start.md): Get up and running quickly
- [User Guide](docs/user_guide.md): Detailed instructions for using DesktopSTT
- [API Reference](docs/api_reference.md): Detailed information about the public API
- [Developer Guide](docs/developer_guide.md): Information for developers who want to contribute

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

### Dependencies

- Python 3.12 or higher
- GTK 4 (for popup mode)
- PyAudio
- OpenAI API key
- `wtype` (for automatic typing of transcribed text)

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

The repository includes two convenience scripts that can be used directly or installed to your PATH:

#### Optimized Popup Script (`desktopstt-popup-silent.sh`)

This script provides an optimized popup recorder that:
- Starts recording immediately when the window opens (no waiting for speech)
- Shows "Recording in progress" status right away
- Automatically stops after 3 seconds of silence
- Types the transcribed text at your cursor position using `wtype`

#### Silent Script (`desktopstt-silent.sh`)

This script provides a headless recorder that:
- Records audio without showing a GUI
- Automatically stops after detecting silence
- Types the transcribed text at your cursor position using `wtype`

#### Installation

```bash
# Copy the scripts to your bin directory
cp desktopstt-popup-silent.sh ~/bin/desktopstt-popup-silent
cp desktopstt-silent.sh ~/bin/desktopstt-silent
chmod +x ~/bin/desktopstt-popup-silent ~/bin/desktopstt-silent

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

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

## Configuration Options

### Silence Detection

You can customize the silence detection parameters:

- `silence_threshold`: Threshold for silence detection (0.0-1.0, default: 0.1)
- `silence_duration`: Duration of silence before stopping (seconds, default: 5.0)

Example:
```bash
desktopstt-popup --silence-threshold 0.05 --silence-duration 3.0
```

Or in the convenience script:
```bash
./desktopstt-popup-silent.sh  # Uses 0.05 threshold and 3.0 seconds by default
```

## Project Structure

- `desktopstt/`: Main package directory
  - `popup_recorder.py`: GUI recorder implementation
  - `truly_silent.py`: Headless recorder implementation
  - `config.py`: Configuration management
  - `utils.py`: Utility functions
  - `audio/`: Audio recording and processing
  - `backends/`: Speech-to-text backend implementations

- `desktopstt-popup-silent.sh`: Optimized popup recorder script
- `desktopstt-silent.sh`: Headless recorder script

## License

[MIT License](LICENSE)
