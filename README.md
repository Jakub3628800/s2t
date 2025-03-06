# DesktopSTT

[![Tests](https://github.com/username/desktopstt/actions/workflows/tests.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/pre-commit.yml)
[![Release](https://github.com/username/desktopstt/actions/workflows/release.yml/badge.svg)](https://github.com/username/desktopstt/actions/workflows/release.yml)

A desktop application for Linux that records speech and converts it to text using various speech recognition backends.

## CursorRules

This project follows [CursorRules](https://github.com/cursor-rules/cursor-rules) for development. CursorRules is a set of guidelines and best practices for developing applications with Cursor, an AI-powered code editor.

Key principles we follow:
- Use modern Python packaging with `pyproject.toml` and `uv` for dependency management
- Maintain clean, well-documented code with type hints
- Follow a modular architecture for extensibility
- Prioritize user experience and accessibility

## Project Specification

### Overview
DesktopSTT is a lightweight desktop application that allows users to record audio from their microphone and convert it to text in real-time or from saved recordings. The application is designed to work on Linux systems, with specific optimizations for Wayland/Sway environments.

### Features
- **Audio Recording**: Capture audio from the system's microphone
- **Speech-to-Text Conversion**: Convert recorded audio to text
- **Multiple Backend Support**:
  - Initial implementation with OpenAI's Whisper API
  - Extensible architecture to support additional STT backends in the future
- **User Interface**:
  - Simple, intuitive GUI for recording and displaying transcribed text
  - System tray integration for quick access
  - Keyboard shortcuts for hands-free operation
  - Popup recording window for visual feedback
  - Voice activity detection for automatic recording stop
  - Audio level visualization
- **Output Options**:
  - Copy text to clipboard
  - Save transcriptions to file
  - Export in various formats (TXT, JSON, etc.)
- **Command-Line Interface**:
  - Record and transcribe from the terminal
  - Output to stdout for piping to other commands
  - Optional minimal UI during recording
  - Simple CLI version for Wayland/Sway compatibility
  - Silent mode for clean output in scripts

### Technical Architecture
- **Frontend**: Python-based GUI using GTK for Linux compatibility
- **Audio Handling**: Use PulseAudio/PipeWire for audio capture
- **Backend Interface**: Modular design to support multiple STT services
  - Whisper API integration (initial implementation)
  - Placeholder for future backends (local Whisper, Mozilla DeepSpeech, etc.)
- **Configuration**: User-configurable settings stored in config files

### Dependencies
- Python 3.12+
- GTK 4 for GUI
- PulseAudio/PipeWire for audio capture
- OpenAI API key (for Whisper API backend)
- NumPy for audio processing and voice activity detection
- Various Python packages (see requirements.txt)

### Limitations
- Initially designed for Linux only, with focus on Wayland/Sway environments
- Internet connection required for cloud-based backends (like Whisper API)
- Audio quality dependent on microphone and system audio settings

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver that we use for this project.

```bash
# Clone the repository
git clone https://github.com/yourusername/desktopstt.git
cd desktopstt

# Create a virtual environment with uv
uv venv

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
# .venv\Scripts\activate  # On Windows

# Install dependencies with uv
uv sync

# If you need to add a new dependency
# Edit pyproject.toml to add the dependency, then run:
uv sync
```

### Using pip (Alternative)

```bash
# Clone the repository
git clone https://github.com/yourusername/desktopstt.git
cd desktopstt

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

### Using Makefile

```bash
# Clone the repository
git clone https://github.com/yourusername/desktopstt.git
cd desktopstt

# Create a virtual environment and install
make install-venv
source .venv/bin/activate

# Or install directly
make install
```

### Package Management

This project uses `pyproject.toml` for dependency management, not `requirements.txt`. The `requirements.txt` file is provided only for compatibility with older tools.

When adding new dependencies:
1. Add them to the `dependencies` list in `pyproject.toml`
2. Run `