# DesktopSTT Developer Guide

This guide provides information for developers who want to contribute to DesktopSTT or understand its internal architecture.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Development Setup](#development-setup)
5. [Testing](#testing)
6. [Contributing](#contributing)
7. [Code Style](#code-style)

## Project Structure

The DesktopSTT project is organized as follows:

```
desktopstt/
├── desktopstt/               # Main package
│   ├── __init__.py           # Package initialization
│   ├── audio/                # Audio recording functionality
│   │   ├── __init__.py
│   │   └── recorder.py       # Audio recorder implementation
│   ├── backends/             # Speech-to-text backends
│   │   ├── __init__.py
│   │   ├── base.py           # Base backend interface
│   │   └── whisper_api.py    # OpenAI Whisper API implementation
│   ├── config.py             # Configuration handling
│   ├── popup_recorder.py     # Popup recorder implementation
│   ├── truly_silent.py       # Headless mode implementation
│   ├── ui/                   # UI components
│   │   └── __init__.py
│   └── utils.py              # Utility functions
├── tests/                    # Test suite
├── .github/                  # GitHub configuration
│   └── workflows/            # GitHub Actions workflows
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── desktopstt-popup-silent.sh # Convenience script for popup recorder
├── desktopstt-silent.sh      # Convenience script for headless mode
├── install_scripts.sh        # Installation script for convenience scripts
├── Makefile                  # Build and run targets
├── pyproject.toml            # Project metadata and dependencies
└── README.md                 # Project overview
```

## Architecture

DesktopSTT follows a modular architecture with clear separation of concerns:

1. **Audio Recording**: Handles capturing audio from the microphone
2. **Speech-to-Text Backend**: Converts audio to text using external services
3. **User Interface**: Provides visual feedback and controls
4. **Configuration**: Manages user settings and API keys

The application has two main entry points:
- `popup_recorder.py`: Graphical interface with visual feedback
- `truly_silent.py`: Headless mode for terminal use

## Core Components

### Audio Recorder

The `AudioRecorder` class in `audio/recorder.py` handles audio capture using PyAudio. It provides methods for starting and stopping recording, and can save the recorded audio to a temporary file.

Key features:
- Real-time audio level calculation
- Callback mechanism for processing audio frames
- Temporary file management

### Speech-to-Text Backends

The backends module provides a pluggable interface for different speech-to-text services. Currently, only the OpenAI Whisper API is implemented.

The backend interface is defined in `backends/base.py`, and specific implementations should inherit from the `STTBackend` class and implement the required methods.

### Popup Recorder

The `popup_recorder.py` module provides a graphical interface using GTK 4. It includes:

- A custom window with recording controls
- Audio level visualization
- Voice activity detection
- Timer display

### Headless Mode

The `truly_silent.py` module provides a terminal-based interface without any GUI. It's designed to be used in scripts and automation, with minimal output.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- GTK 4 development libraries
- PulseAudio or PipeWire development libraries

### Setting Up the Development Environment

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

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install pytest pytest-cov pre-commit
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Testing

DesktopSTT uses pytest for testing. The test suite is located in the `tests/` directory.

### Running Tests

Run the entire test suite:
```bash
make test
```

Or using pytest directly:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=desktopstt --cov-report=term
```

### Writing Tests

When adding new features, please include tests that cover the new functionality. Tests should be placed in the `tests/` directory with a name that matches the module being tested.

Example test structure:
```python
def test_feature():
    # Arrange
    # Set up the test environment
    
    # Act
    # Call the function or method being tested
    
    # Assert
    # Verify the expected outcome
```

## Contributing

We welcome contributions to DesktopSTT! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run the tests to ensure everything works
5. Run pre-commit hooks to ensure code quality
6. Submit a pull request

### Pull Request Process

1. Ensure your code passes all tests and pre-commit checks
2. Update the documentation if necessary
3. Add a clear description of your changes
4. Reference any related issues

## Code Style

DesktopSTT follows the PEP 8 style guide with some modifications. We use ruff for linting and formatting.

### Linting

Run the pre-commit hooks to lint your code:
```bash
pre-commit run --all-files
```

### Type Hints

We use type hints throughout the codebase. Please include type hints in your contributions.

Example:
```python
def process_audio(data: bytes) -> str:
    """Process audio data and return the transcription."""
    # Implementation
    return transcription
```

### Documentation

Please document your code using docstrings. We follow the Google style for docstrings.

Example:
```python
def process_audio(data: bytes) -> str:
    """Process audio data and return the transcription.
    
    Args:
        data: The audio data as bytes.
        
    Returns:
        The transcribed text.
    """
    # Implementation
    return transcription
``` 