# DesktopSTT User Guide

This guide provides detailed instructions on how to install, configure, and use DesktopSTT, a desktop application for Linux that converts speech to text.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Using the Popup Recorder](#using-the-popup-recorder)
5. [Using the Headless Mode](#using-the-headless-mode)
6. [Convenience Scripts](#convenience-scripts)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

DesktopSTT is a lightweight desktop application that allows you to record audio from your microphone and convert it to text. It offers two main modes of operation:

- **Popup Recorder**: A graphical window that provides visual feedback during recording
- **Headless Mode**: A terminal-based version without any GUI, perfect for scripts and automation

Both modes use the same speech-to-text backend (currently OpenAI's Whisper API) to provide accurate transcriptions.

## Installation

### Prerequisites

- Linux operating system
- Python 3.12 or higher
- PulseAudio or PipeWire for audio capture
- GTK 4 for the popup recorder (not needed for headless mode)
- `wtype` for the convenience scripts (optional)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/desktopstt.git
   cd desktopstt
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

4. (Optional) Install the convenience scripts:
   ```bash
   ./install_scripts.sh
   ```

## Configuration

DesktopSTT requires an OpenAI API key to use the Whisper API for speech-to-text conversion. You can provide this key in one of three ways:

### Option 1: Config File

1. Create the default config if it doesn't exist:
   ```bash
   python -m desktopstt.config
   ```

2. Edit the config file:
   ```bash
   nano ~/.config/desktopstt/config.yaml
   ```

3. Set your API key:
   ```yaml
   backends:
     whisper_api:
       api_key: 'your-api-key-here'
   ```

### Option 2: Environment Variable

Set the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Option 3: .env File

Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

## Using the Popup Recorder

The popup recorder provides a graphical interface for recording audio and converting it to text.

### Basic Usage

Run the popup recorder:
```bash
desktopstt-popup
```

Or using make:
```bash
make run-popup
```

### Features

- **Recording Indicator**: A pulsing red circle indicates that recording is in progress
- **Timer**: Shows the elapsed recording time
- **Audio Level Meter**: Visualizes your voice level in real-time
- **Voice Activity Detection (VAD)**: Automatically stops recording after detecting silence
- **Stop Button**: Manually stop recording at any time

### Command-Line Options

- `--silent`: Output only the transcribed text (no logging)
- `--time SECONDS`: Record for a specific duration (disables VAD)
- `--no-vad`: Disable voice activity detection
- `--silence-threshold THRESHOLD`: Set the threshold for silence detection (0.0-1.0, default: 0.1)
- `--silence-duration SECONDS`: Set the duration of silence before stopping (default: 5.0)
- `--min-recording-time SECONDS`: Set the minimum recording time before VAD kicks in (default: 3.0)
- `--output FILE`: Save the transcription to a file

### Examples

Silent mode with 3 seconds silence duration:
```bash
desktopstt-popup --silent --silence-duration 3.0
```

Record for 10 seconds without VAD:
```bash
desktopstt-popup --time 10 --no-vad
```

Start recording immediately without waiting for speech:
```bash
desktopstt-popup --no-vad
```

## Using the Headless Mode

The headless mode provides a terminal-based interface without any GUI, perfect for scripts and automation.

### Basic Usage

Run the headless mode:
```bash
desktopstt-silent
```

Or using make:
```bash
make run-silent
```

### Features

- **Minimal Dependencies**: No GUI dependencies required
- **Clean Output**: Only outputs the transcribed text
- **Script-Friendly**: Perfect for use in shell scripts and automation

### Examples

Pipe the output to another command:
```bash
desktopstt-silent | grep "important"
```

Use in a shell script:
```bash
SPEECH=$(desktopstt-silent)
echo "You said: $SPEECH"
```

## Convenience Scripts

The repository includes two convenience scripts that make it easier to use DesktopSTT from anywhere on your system.

### Installation

Using the installation script:
```bash
./install_scripts.sh
```

Or manually:
```bash
cp desktopstt-popup-silent.sh ~/bin/desktopstt-popup-silent
cp desktopstt-silent.sh ~/bin/desktopstt-silent
chmod +x ~/bin/desktopstt-popup-silent ~/bin/desktopstt-silent
```

### Usage

Run the popup recorder with silent mode:
```bash
desktopstt-popup-silent
```

Run the headless mode:
```bash
desktopstt-silent
```

These scripts will:
1. Run the appropriate command
2. Suppress warnings and error messages
3. Pipe the output to `wtype` to automatically type the transcribed text at your cursor position

## Troubleshooting

### Common Issues

#### No Audio Input

If DesktopSTT is not detecting any audio input:

1. Check if your microphone is working with other applications
2. Make sure your microphone is not muted in your system settings
3. Try running `pavucontrol` to check your PulseAudio settings

#### API Key Issues

If you're having issues with the OpenAI API key:

1. Make sure your API key is correct and has not expired
2. Check that you have sufficient credits in your OpenAI account
3. Verify that the API key is set correctly in one of the three supported methods

#### GTK Errors

If you're seeing GTK-related errors when using the popup recorder:

1. Make sure GTK 4 is installed on your system
2. Try installing the required dependencies:
   ```bash
   sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-4.0
   ```

### Debugging

To enable debug logging:
```bash
export DESKTOPSTT_DEBUG=1
```

## FAQ

### Q: Does DesktopSTT work offline?

A: Currently, DesktopSTT requires an internet connection as it uses OpenAI's Whisper API for speech-to-text conversion. Support for offline models may be added in the future.

### Q: Can I use DesktopSTT on Windows or macOS?

A: DesktopSTT is designed for Linux systems. While it may work on macOS with some modifications, Windows support is not currently available.

### Q: How accurate is the speech recognition?

A: DesktopSTT uses OpenAI's Whisper API, which is one of the most accurate speech recognition systems available. However, accuracy can vary depending on factors such as audio quality, background noise, and accent.

### Q: Is there a limit to how long I can record?

A: There is no built-in limit to recording duration, but longer recordings will take more time to transcribe and may incur higher API costs. The Whisper API has its own limitations on file size and duration.

### Q: Can I customize the keyboard shortcuts?

A: Currently, DesktopSTT does not support customizable keyboard shortcuts. This feature may be added in future versions. 