# S2T User Guide

This guide provides detailed instructions on how to install, configure, and use S2T, a desktop application for Linux that converts speech to text.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [Convenience Scripts](#convenience-scripts)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

S2T is a lightweight desktop application that allows you to record audio from your microphone and convert it to text. It offers two main modes of operation:

1. **Popup Recorder**: A graphical interface with a popup window that shows recording status and audio levels.
2. **Silent Mode**: A command-line interface without any GUI, suitable for scripts and automation.

Both modes use OpenAI's Whisper API for speech-to-text conversion, providing high-quality transcriptions.

## Installation

### Prerequisites

- Python 3.12 or higher
- GTK 4 (required for popup mode)
- PyAudio
- OpenAI API key
- `wtype` (optional, for automatic typing of transcribed text)

### Install Required System Dependencies

For Ubuntu/Debian-based systems:

```bash
sudo apt-get install libgirepository1.0-dev libgtk-4-dev wtype
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/s2t.git
cd s2t

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

## Configuration

### API Key Setup

S2T requires an OpenAI API key to use the Whisper API for speech-to-text conversion. You can provide this key in one of three ways:

#### Option 1: Edit the config file
```bash
# Create the default config if it doesn't exist
python -m s2t.config

# Edit the config file
nano ~/.config/s2t/config.yaml
```

In the config file, set your API key:
```yaml
backends:
  whisper_api:
    api_key: 'your-api-key-here'
```

#### Option 2: Set environment variable
```bash
export OPENAI_API_KEY='your-api-key-here'
```

#### Option 3: Create a .env file
Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

### Customizing Behavior

You can customize various aspects of S2T by editing the config file at `~/.config/s2t/config.yaml`. The following settings are available:

- **Audio Settings**: Sample rate, channels, chunk size, etc.
- **UI Settings**: Window size, theme, etc.
- **Backend Settings**: API key, model, language, etc.
- **Output Settings**: Format, save location, etc.
- **VAD Settings**: Silence threshold, silence duration, etc.

## Basic Usage

### Popup Recorder

The popup recorder provides a graphical interface for recording audio and converting it to text.

```bash
# Using the main command
s2t

# Using the make run target
make run
```

This will open a window with a "Recording" indicator and a "Stop Recording" button. Speak into your microphone, and the audio level meter will show your voice level. When you're done speaking, either:

- Click the "Stop Recording" button
- Close the window
- Wait for the voice activity detection to detect silence (default: 5 seconds)

The transcribed text will be printed to the terminal and typed at your cursor position.

### Silent Mode

To run S2T in silent mode without a GUI:

```bash
s2t --silent
```

### Custom Threshold and Duration

Adjust the silence detection sensitivity:

```bash
s2t --threshold 0.03 --duration 1.5
```

### Add Newline

To add a newline character after the transcription:

```bash
s2t --newline
```

### Debug Mode

To enable debug output:

```bash
s2t --debug
```

## Advanced Usage

### Using a Custom Configuration File

```bash
s2t --config /path/to/your/config.yaml
```

### Transcribe to File

To save the transcription to a file instead of typing it out:

```bash
s2t-popup --output transcript.txt
```

### Fixed Duration Recording

To record for a fixed duration instead of using voice activity detection:

```bash
s2t-popup --time 10 --no-vad
```

### Programmatic Usage

You can use S2T in your Python code:

```python
from s2t.popup_recorder import PopupRecorder
from s2t.config import load_config

# Load configuration
config = load_config()

# Create recorder
recorder = PopupRecorder(config)

# Record and transcribe
text = recorder.record_and_transcribe()

# Use the transcribed text
print(f"Transcription: {text}")
```

## Convenience Scripts

The repository includes a convenience script that makes it easier to use S2T from anywhere on your system.

### Installation

```bash
# Copy the script to your bin directory
cp speaktype.sh ~/bin/speaktype
chmod +x ~/bin/speaktype

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

### Usage

```bash
speaktype
```

This script will automatically record audio and type the transcribed text at your cursor position.

## Troubleshooting

### Missing System Dependencies

If you encounter errors about missing GTK or other dependencies:

```bash
sudo apt-get install libgirepository1.0-dev libgtk-4-dev wtype
```

### GTK Version Errors

The application requires GTK 4. If you encounter errors related to GTK methods:

```bash
# Check your GTK4 installation
pkg-config --modversion gtk4
```

### No Audio Input

If S2T is not detecting any audio input:

1. Check that your microphone is connected and working
2. Check that your microphone is not muted
3. Try running with debug mode to see more information:
   ```bash
   s2t --debug
   ```

### API Key Issues

If you're having issues with the API key:

1. Check that your API key is correct
2. Check that your API key has access to the Whisper API
3. Check your internet connection

### Clean Start

If you're having persistent issues, try removing temporary files:

```bash
rm -rf ~/.config/s2t/tmp_*
```

## FAQ

### Q: Does S2T work offline?

A: Currently, S2T requires an internet connection as it uses OpenAI's Whisper API for speech-to-text conversion. Support for offline models may be added in the future.

### Q: Can I use S2T on Windows or macOS?

A: S2T is designed for Linux systems. While it may work on macOS with some modifications, Windows support is not currently available.

### Q: How accurate is the transcription?

A: S2T uses OpenAI's Whisper API, which is one of the most accurate speech recognition systems available. However, accuracy can vary depending on factors such as audio quality, background noise, accent, and language.

### Q: What's the difference between popup and silent modes?

A: Popup mode provides a graphical interface with visual feedback, while silent mode operates without a GUI and is more suitable for scripting and automation.

### Q: Can I use S2T for languages other than English?

A: Yes, S2T supports multiple languages through the Whisper API. You can specify the language in your configuration file.
