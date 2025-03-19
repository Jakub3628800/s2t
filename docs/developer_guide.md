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
2. Create a virtual environment
3. Install the package in development mode
4. Install development dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/s2t.git
cd s2t

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package in development mode
pip install -e ".[dev]"
```

## Project Structure

The S2T project is organized as follows:

```
s2t/
├── s2t/               # Main package
│   ├── __init__.py    # Package initialization
│   ├── audio/         # Audio recording functionality
│   │   ├── __init__.py
│   │   └── recorder.py
│   ├── backends/      # Speech-to-text backends
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── whisper_api.py
│   ├── config.py      # Configuration management
│   ├── headless_recorder.py  # Headless recorder implementation
│   ├── immediate_popup.py    # Immediate popup recorder
│   ├── popup_recorder.py     # Popup recorder implementation
│   └── truly_silent.py       # Truly silent recorder
├── tests/             # Test suite
├── docs/              # Documentation
├── s2t-popup-silent.sh # Convenience script for popup recorder
├── s2t-silent.sh      # Convenience script for headless mode
├── pyproject.toml     # Project metadata and dependencies
├── Makefile           # Build system
└── README.md          # Project overview
```

## Architecture

S2T follows a modular architecture with clear separation of concerns:

### Audio Module

The `audio` module is responsible for recording audio from the microphone. It provides the `AudioRecorder` class, which handles:

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

The `config` module handles loading and managing configuration. It provides:

- `load_config`: Function to load configuration from a file or the default location
- `DEFAULT_CONFIG`: Default configuration values
- `DEFAULT_CONFIG_PATH`: Default path to the configuration file

### Recorder Implementations

S2T provides several recorder implementations:

- `PopupRecorder`: Graphical recorder with a popup window
- `ImmediatePopupRecorder`: Popup recorder that starts recording immediately
- `TrulySilentRecorder`: Recorder without any GUI or notifications
- `HeadlessRecorder`: Recorder without GUI but with desktop notifications


## Testing

S2T uses pytest for testing. The test suite is located in the `tests/` directory.

### Running Tests

To run the tests:

```bash
# Run all tests
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
- Mock external dependencies
- Test both success and failure cases
- Use descriptive test names

## Contributing

We welcome contributions to S2T! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Add tests for your changes
5. Run the tests to make sure they pass
6. Submit a pull request

### Pull Request Process

1. Ensure your code passes all tests
2. Update the documentation if necessary
3. Add a description of your changes to the pull request
4. Wait for a maintainer to review your pull request

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
