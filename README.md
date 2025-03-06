# DesktopSTT

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
2. Run `uv sync` to install the new dependencies
3. Optionally update `requirements.txt` with `uv pip freeze > requirements.txt`

## API Key Setup

To use the Whisper API backend, you need to set your OpenAI API key:

### Option 1: Edit the config file
```bash
# Create the default config if it doesn't exist
python -m desktopstt.config

# Edit the config file
nano ~/.config/desktopstt/config.yaml
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

## Usage

### GUI Mode

```bash
# Run the application in GUI mode
desktopstt

# Or using make
make run-gui
```

### CLI Mode

```bash
# Basic CLI usage (outputs to stdout)
desktopstt-cli

# Record for a specific duration (in seconds)
desktopstt-cli --time 10

# Save output to a file
desktopstt-cli --output transcription.txt

# Show a minimal UI during recording
desktopstt-cli --ui

# Enable debug logging
desktopstt-cli --debug
```

### Simple CLI Mode (Wayland/Sway Compatible)

```bash
# Basic simple CLI usage (outputs to stdout)
desktopstt-simple

# Record for a specific duration (in seconds)
desktopstt-simple --time 10

# Save output to a file
desktopstt-simple --output transcription.txt

# Enable debug logging
desktopstt-simple --debug

# Silent mode (outputs only the transcribed text)
desktopstt-simple --silent

# Using make
make transcribe
make transcribe-silent
make transcribe-time
```

### Popup Recorder Mode

```bash
# Basic popup recorder usage with voice activity detection (VAD)
# Automatically stops recording after detecting silence
desktopstt-popup

# Record for a specific duration (in seconds) without VAD
desktopstt-popup --time 10 --no-vad

# Customize VAD settings
desktopstt-popup --silence-threshold 0.15 --silence-duration 3.0 --min-recording-time 2.0

# Save output to a file
desktopstt-popup --output transcription.txt

# Silent mode (outputs only the transcribed text)
desktopstt-popup --silent

# Using make
make record-popup            # With VAD
make record-popup-time       # Fixed duration (5 seconds)
make record-popup-vad        # Explicit VAD
make record-popup-silent     # Silent mode with VAD
```

### Terminal Integration

DesktopSTT can be integrated into terminal workflows using pipes:

```bash
# Transcribe speech and pipe to another command (suppress warnings)
desktopstt-simple --silent 2>/dev/null | grep "important"

# Transcribe speech and use in a shell script (suppress warnings)
SPEECH=$(desktopstt-simple --silent --time 5 2>/dev/null)
echo "You said: $SPEECH"

# Suppress ALSA warnings using environment variable
PYTHONWARNINGS="ignore" desktopstt-simple --silent
```

## Example Scripts

The repository includes several example scripts that use the Python interpreter from the virtual environment created with uv:

```bash
# First, create and activate the virtual environment
uv venv
source .venv/bin/activate

# Quick transcription with formatted output
./examples/quick_transcribe.sh

# Quick transcription with silent output
./examples/quick_transcribe.sh 5 silent

# Speech to command execution
./examples/pipe_example.sh

# Silent speech to command execution (no ALSA warnings)
./examples/silent_pipe.sh

# Popup window for recording with visual feedback and VAD
./examples/popup_transcribe.sh

# Popup window with fixed duration (no VAD)
./examples/popup_transcribe.sh 10 --no-vad

# Silent popup window with VAD
./examples/silent_popup.sh
```

Note: All example scripts assume they are run from the project root directory and that a virtual environment has been created at `.venv` using `uv venv`.

## Voice Activity Detection (VAD)

The popup recorder includes voice activity detection that automatically stops recording after detecting silence:

- **Audio Level Visualization**: See your voice level in real-time
- **Automatic Stop**: Recording stops after a period of silence
- **Customizable Settings**:
  - `--silence-threshold`: Level below which audio is considered silence (0.0-1.0, default: 0.1)
  - `--silence-duration`: How long silence must persist before stopping (seconds, default: 2.0)
  - `--min-recording-time`: Minimum recording time before VAD activates (seconds, default: 3.0)
  - `--no-vad`: Disable VAD and use fixed duration instead

## Desktop Integration

The repository includes a desktop entry file for launching the popup recorder from your desktop environment:

```bash
# Copy the desktop entry to your applications directory
cp examples/desktopstt-popup.desktop ~/.local/share/applications/

# Make it executable
chmod +x ~/.local/share/applications/desktopstt-popup.desktop
```

## Testing

The repository includes simple test scripts:

```bash
# Test audio recording only
python test_record.py

# Test audio recording and transcription
OPENAI_API_KEY='your-api-key-here' python test_transcribe.py

# Test with .env file
python test_with_dotenv.py
```

## Configuration

Configuration file is located at `~/.config/desktopstt/config.yaml`.

## License

[MIT License](LICENSE)
