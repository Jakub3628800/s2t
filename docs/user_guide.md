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
2. **Headless Mode**: A command-line interface without any GUI, suitable for scripts and automation.

Both modes use OpenAI's Whisper API for speech-to-text conversion, providing high-quality transcriptions.

## Installation

### Prerequisites

- Python 3.12 or higher
- GTK 4 (for popup mode)
- PyAudio
- OpenAI API key
- `wtype` (optional, for automatic typing of transcribed text)

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
s2t-popup
```

This will open a window with a "Recording" indicator and a "Stop Recording" button. Speak into your microphone, and the audio level meter will show your voice level. When you're done speaking, either:

- Click the "Stop Recording" button
- Close the window
- Wait for the voice activity detection to detect silence (default: 5 seconds)

The transcribed text will be printed to the terminal.

### Silent Mode

For a cleaner output with only the transcribed text:

```bash
s2t-popup --silent --silence-duration 3.0
```

### Fixed Duration Recording

To record for a fixed duration instead of using voice activity detection:

```bash
s2t-popup --time 10 --no-vad
```

### Disable Voice Activity Detection

To disable voice activity detection completely:

```bash
s2t-popup --no-vad
```

### Headless Mode

The headless mode provides a terminal-based interface without any GUI.

```bash
s2t-silent
```

This will record audio from your microphone for 5 seconds (by default) and then transcribe it. The transcribed text will be printed to the terminal.

### Piping Output

You can pipe the output of the headless mode to other commands:

```bash
s2t-silent | grep "important"
```

### Capturing Output

You can capture the output in a variable:

```bash
SPEECH=$(s2t-silent)
echo "You said: $SPEECH"
```

## Convenience Scripts

The repository includes two convenience scripts that make it easier to use S2T from anywhere on your system.

### Installation

```bash
# Copy the scripts to your bin directory
cp s2t-popup-silent.sh ~/bin/s2t-popup-silent
cp s2t-silent.sh ~/bin/s2t-silent
chmod +x ~/bin/s2t-popup-silent ~/bin/s2t-silent

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

### Popup Script

```bash
s2t-popup-silent
```

This script will open a popup window that starts recording immediately. When you stop speaking, it will automatically type the transcribed text at your cursor position.

### Silent Script

```bash
s2t-silent
```

This script will record audio without showing a GUI and then type the transcribed text at your cursor position.

## Troubleshooting

### No Audio Input

If S2T is not detecting any audio input:

1. Check that your microphone is connected and working
2. Check that your microphone is not muted
3. Try selecting a different audio input device:
   ```bash
   s2t-popup --list-devices
   s2t-popup --device-index 1  # Use the index from the list
   ```

### API Key Issues

If you're having issues with the API key:

1. Check that your API key is correct
2. Check that your API key has access to the Whisper API
3. Check your internet connection

### Debug Mode

To enable debug logging:

```bash
export S2T_DEBUG=1
```

## FAQ

### Q: Does S2T work offline?

A: Currently, S2T requires an internet connection as it uses OpenAI's Whisper API for speech-to-text conversion. Support for offline models may be added in the future.

### Q: Can I use S2T on Windows or macOS?

A: S2T is designed for Linux systems. While it may work on macOS with some modifications, Windows support is not currently available.

### Q: How accurate is the transcription?

A: S2T uses OpenAI's Whisper API, which is one of the most accurate speech recognition systems available. However, accuracy can vary depending on factors such as audio quality, background noise, accent, and language.

### Q: Can I customize keyboard shortcuts?

A: Currently, S2T does not support customizable keyboard shortcuts. This feature may be added in future versions.
