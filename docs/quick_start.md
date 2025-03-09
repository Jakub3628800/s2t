# Quick Start Guide

This guide will help you get started with S2T quickly.

## Installation

### Prerequisites

- Python 3.12 or higher
- GTK 4 (for popup mode)
- PyAudio
- OpenAI API key
- `wtype` (for automatic typing of transcribed text)

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

### Option 1: Edit the config file
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

### Option 2: Set environment variable
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Option 3: Create a .env file
Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

## Basic Usage

### Popup Recorder

The popup recorder provides a graphical interface for recording audio and converting it to text.

```bash
# Standard popup recorder with voice activity detection
s2t-popup

# Immediate popup recorder (starts recording immediately)
s2t-immediate
```

### Headless Recorder

The headless recorder runs without a GUI, making it suitable for scripts and automation.

```bash
# Headless recorder with notifications
s2t-headless

# Truly silent recorder (no GUI, no notifications)
s2t-silent
```

### Convenience Scripts

The repository includes two convenience scripts that can be used directly or installed to your PATH:

```bash
# Copy the scripts to your bin directory
cp s2t-popup-silent.sh ~/bin/s2t-popup-silent
cp s2t-silent.sh ~/bin/s2t-silent
chmod +x ~/bin/s2t-popup-silent ~/bin/s2t-silent

# Add ~/bin to your PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc  # or ~/.zshrc
source ~/.bashrc  # or ~/.zshrc
```

## Configuration Options

### Silence Detection

You can customize the silence detection parameters:

- `silence_threshold`: Threshold for silence detection (0.0-1.0, default: 0.1)
- `silence_duration`: Duration of silence before stopping (seconds, default: 5.0)

Example:
```bash
s2t-popup --silence-threshold 0.05 --silence-duration 3.0
```

Or in the convenience script:
```bash
./s2t-popup-silent.sh  # Uses 0.05 threshold and 3.0 seconds by default
```

## Next Steps

For more detailed information, see the [User Guide](user_guide.md) and [API Reference](api_reference.md).
