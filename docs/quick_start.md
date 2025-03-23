# Quick Start Guide

This guide will help you get started with S2T quickly.

## Installation

### Prerequisites

- Python 3.12 or higher
- GTK 4 (required for popup mode)
- PyAudio
- OpenAI API key
- `wtype` (for automatic typing of transcribed text)

### Install System Dependencies

For Ubuntu/Debian systems:

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

## API Key Setup

To use the Whisper API backend, you need to set your OpenAI API key:

### Option 1: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Option 2: Edit the Config File
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

### Option 3: Create a .env File
Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

## Basic Usage

### Standard Mode (Popup)

The default mode provides a graphical interface for recording audio and converting it to text:

```bash
# Using the main command
s2t

# Using make run
make run

# With parameters
s2t --threshold 0.03 --duration 1.5
```

This will open a window with recording controls. After you speak and stop the recording, the transcribed text will be typed at your cursor position.

### Silent Mode

For command-line usage without a GUI:

```bash
s2t --silent
```

### Add Newline

To add a newline character after the transcription:

```bash
s2t --newline
```

### Debug Mode

Enable verbose logging to help troubleshoot issues:

```bash
s2t --debug
```

## Using the Convenience Script

S2T comes with a convenience script that can be used directly or added to your PATH:

```bash
# Run directly
./speaktype.sh

# Or copy to your bin directory and make executable
cp speaktype.sh ~/bin/speaktype
chmod +x ~/bin/speaktype

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

Then you can simply type:

```bash
speaktype
```

## Configuration Options

### Silence Detection

You can customize the silence detection parameters:

- `--threshold`: Threshold for silence detection (0.0-1.0, default: 0.05)
- `--duration`: Duration of silence before stopping (seconds, default: 2.0)

Example:
```bash
s2t --threshold 0.03 --duration 1.5
```

### Custom Configuration File

You can specify a custom configuration file:

```bash
s2t --config /path/to/your/config.yaml
```

## Common Issues and Solutions

### Missing Dependencies

If you encounter errors about missing GTK or other dependencies:

```bash
sudo apt-get install libgirepository1.0-dev libgtk-4-dev wtype
```

### OpenAI API Key

If transcription fails with API errors, check your API key:

```bash
echo $OPENAI_API_KEY
```

### Audio Issues

If you experience audio recording problems, try:

```bash
# Check your audio devices
arecord -l

# Test recording with ALSA directly
arecord -d 5 test.wav
```

## Next Steps

For more detailed information, see the [User Guide](user_guide.md) and [API Reference](api_reference.md).
