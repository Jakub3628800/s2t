# S2T Developer Guide

This guide provides information for developers who want to contribute to S2T or understand its internal architecture.

## Table of Contents

1. [Development Environment](#development-environment)
2. [Project Structure](#project-structure)
3. [Architecture](#architecture)
4. [Testing](#testing)
5. [Contributing](#contributing)
6. [Coding Standards](#coding-standards)

## Development Environment

To set up a development environment for S2T, follow these steps:

1. Clone the repository
2. Install system dependencies
3. Create a virtual environment
4. Install the package in development mode
5. Set up pre-commit hooks

```bash
# Clone the repository
git clone https://github.com/yourusername/s2t.git
cd s2t

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install libgirepository1.0-dev libgtk-4-dev wtype

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package in development mode with development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

## Project Structure

The S2T project is organized as follows:

```
s2t/
├── s2t/               # Main package
│   ├── __init__.py    # Package initialization
│   ├── audio.py       # Audio recording functionality
│   ├── backends/      # Speech-to-text backends
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── whisper_api.py
│   ├── config.py      # Configuration management using Pydantic
│   ├── immediate_popup.py    # Immediate popup recorder
│   ├── main.py        # Main entry point
│   ├── popup_recorder.py     # Popup recorder implementation
│   └── truly_silent.py       # Truly silent recorder
├── tests/             # Test suite
│   ├── test_audio_simple.py
│   ├── test_backends_simple.py
│   ├── test_config.py
│   └── test_main.py
├── docs/              # Documentation
├── speaktype.sh       # Convenience script
├── pyproject.toml     # Project metadata and dependencies
├── Makefile           # Build system
└── README.md          # Project overview
```

## Architecture

S2T follows a modular architecture with clear separation of concerns:

### Main Module

The `main.py` module serves as the primary entry point for the application and includes:

- Command-line argument parsing
- Configuration loading
- Mode selection (popup vs. silent)
- Input validation
- Transcription output handling

### Audio Module

The `audio.py` module is responsible for recording audio from the microphone. It provides the `AudioRecorder` class, which handles:

- Initializing the audio device
- Recording audio in a separate thread
- Calculating audio levels for visualization
- Saving recorded audio to a temporary file

### Backends Module

The `backends` module provides interfaces for speech-to-text services. It includes:

- `STTBackend`: Abstract base class for all backends
- `WhisperAPIBackend`: Implementation using OpenAI's Whisper API
- `get_backend`: Factory function to get the appropriate backend based on configuration

### Configuration Module

The `config.py` module handles loading and managing configuration. It uses Pydantic for type validation and provides:

- `load_config`: Function to load configuration from a file or the default location
- `S2TConfig`: Pydantic model for configuration validation
- `DEFAULT_CONFIG_PATH`: Default path to the configuration file

### Recorder Implementations

S2T provides several recorder implementations:

- `PopupRecorder`: Graphical recorder with a popup window using GTK 4
- `ImmediatePopupRecorder`: Popup recorder that starts recording immediately
- `TrulySilentRecorder`: Recorder without any GUI or notifications

## GUI Implementation

The GUI is implemented using GTK 4 and includes:

- `RecordingWindow`: Window class for recording with visual feedback
- `AudioLevelBar`: Custom GTK widget for displaying audio levels
- Event handling for user interactions (button clicks, window close)
- Voice activity detection visualization

## Testing

S2T uses pytest for testing. The test suite is located in the `tests/` directory.

### Running Tests

To run the tests:

```bash
# Run all tests
make test

# Or directly with pytest
pytest

# Run tests with coverage report
pytest --cov=s2t --cov-report=term

# Run a specific test file
pytest tests/test_config.py

# Run a specific test
pytest tests/test_config.py::test_load_config
```

### Writing Tests

When writing tests, follow these guidelines:

- Use pytest fixtures for common setup
- Mock external dependencies (especially GTK and audio recording)
- Test both success and failure cases
- Use descriptive test names
- Ensure tests are deterministic and don't depend on external services

## Pre-commit Checks

The project uses pre-commit to ensure code quality. The pre-commit hooks include:

- ruff for linting and formatting
- mypy for type checking
- codespell for spell checking
- shellcheck for shell script checking

To run pre-commit checks manually:

```bash
pre-commit run --all-files
```

## Contributing

We welcome contributions to S2T! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Add tests for your changes
5. Run the tests and pre-commit checks to make sure they pass
6. Submit a pull request

### Pull Request Process

1. Ensure your code passes all tests and pre-commit checks
2. Update the documentation if necessary
3. Add a description of your changes to the pull request
4. Wait for a maintainer to review your pull request

## Debugging

### GTK Debugging

When working with the GTK interface, you may encounter issues with the main loop or widget hierarchy. To debug these issues:

- Use `--debug` flag to enable debug logging
- Check for GTK warnings in the console
- Test with minimal GTK applications to isolate issues
- Use the GTK Inspector (if available)

### Audio Debugging

For audio-related issues:

- Check ALSA configuration and permissions
- Verify microphone access
- Use tools like `arecord` to test audio recording outside of S2T
- Increase debug logging to see audio device details

### API Debugging

When troubleshooting API issues:

- Verify API key validity
- Check network connectivity
- Inspect request/response details with debug logging
- Use a tool like curl to test API endpoints directly

## Coding Standards

S2T follows the PEP 8 style guide with some modifications. We use ruff for linting and formatting.

### Linting

To lint your code:

```bash
ruff check .
```

### Formatting

To format your code:

```bash
ruff format .
```

### Pre-commit Hooks

We recommend using pre-commit hooks to ensure your code meets our standards:

```bash
pip install pre-commit
pre-commit install
```
