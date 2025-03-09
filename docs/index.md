# S2T Documentation

Welcome to the S2T documentation. This documentation provides information about using and developing with S2T.

## What is S2T?

S2T is a desktop application for Linux that records speech and converts it to text using OpenAI's Whisper API. It provides both GUI and headless modes for flexible usage.

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
  - Immediate recording mode (starts recording as soon as the window opens)
  - Silent mode for clean output

- **Headless Mode**: A terminal-based version without any GUI
  - Perfect for scripts and automation
  - Minimal dependencies
  - Clean output for piping to other commands
  - Desktop notifications support

- **Convenience Scripts**:
  - `s2t-popup-silent.sh`: Optimized popup recorder that starts recording immediately
  - `s2t-silent.sh`: Headless recorder for terminal usage

## Installation

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

### Popup Recorder

```bash
s2t-popup
```

### Headless Mode

```bash
s2t-silent
```

## License

S2T is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
