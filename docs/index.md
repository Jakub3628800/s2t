# DesktopSTT Documentation

Welcome to the DesktopSTT documentation! DesktopSTT is a desktop application for Linux that records speech and converts it to text using various speech recognition backends.

## Documentation Sections

- [Quick Start Guide](quick_start.md): Get up and running quickly
- [User Guide](user_guide.md): Detailed instructions for using DesktopSTT
- [API Reference](api_reference.md): Detailed information about the public API
- [Developer Guide](developer_guide.md): Information for developers who want to contribute

## Features

- **Popup Recorder**: A graphical window for recording with visual feedback
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

## Basic Usage

### Popup Recorder

```bash
desktopstt-popup
```

### Headless Mode

```bash
desktopstt-silent
```

## License

DesktopSTT is released under the [MIT License](../LICENSE). 