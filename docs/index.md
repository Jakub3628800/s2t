# S2T Documentation

Welcome to the S2T documentation. This documentation provides information about using and developing with S2T.

## What is S2T?

S2T is a desktop application for Linux that records speech and converts it to text using OpenAI's Whisper API. It provides both GUI and command-line modes for flexible usage.

## Documentation Sections

- [Quick Start Guide](quick_start.md): Get up and running quickly
- [User Guide](user_guide.md): Detailed instructions for using S2T
- [API Reference](api_reference.md): Detailed information about the public API
- [Developer Guide](developer_guide.md): Information for developers who want to contribute

## Features

- **Popup Recorder**: A graphical popup window for recording with visual feedback
  - Voice activity detection (VAD) for automatic recording stop
  - Audio level visualization
  - Customizable silence detection settings
  - Immediate recording mode
  - GTK 4 based interface

- **Silent Mode**: A command-line version without any GUI
  - Perfect for scripts and automation
  - Minimal dependencies
  - Clean output for piping to other commands
  - Desktop notification support

- **Convenience Script**:
  - `speaktype.sh`: One-click recording and typing

## Installation

### Prerequisites

- Python 3.12 or higher
- GTK 4
- PyAudio
- OpenAI API key
- `wtype` (for automatic typing of transcribed text)

### Install System Dependencies

```bash
# For Ubuntu/Debian
sudo apt-get install libgirepository1.0-dev libgtk-4-dev wtype
```

### Install S2T

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

## Basic Usage

### Popup Mode (Default)

```bash
s2t
```

### Silent Mode

```bash
s2t --silent
```

### Using make

```bash
make run
```

## License

S2T is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
