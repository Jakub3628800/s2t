# S2T API Reference

This document provides detailed information about the public API of S2T.

## Table of Contents

1. [Main Module](#main-module)
2. [Audio Module](#audio-module)
3. [Backends Module](#backends-module)
4. [Configuration Module](#configuration-module)
5. [Popup Recorder Module](#popup-recorder-module)
6. [Immediate Popup Module](#immediate-popup-module)
7. [Truly Silent Module](#truly-silent-module)

## Main Module

The main module serves as the primary entry point for the application.

### Command-Line Interface

```
python -m s2t.main [options]
```

#### Options

- `--silent`: Use silent mode (no GUI window, only notifications)
- `--newline`: Add a newline character after the transcription
- `--threshold N`: Set silence threshold (0.0-1.0, default: 0.05)
- `--duration N`: Set silence duration in seconds (default: 2.0)
- `--debug`: Enable debug output
- `--config PATH`: Path to configuration file (default: ~/.config/s2t/config.yaml)

### Functions

#### `main`

```python
from s2t.main import main
```

```python
main()
```

The main function that processes command-line arguments and controls the application flow.

#### `check_system_dependencies`

```python
from s2t.main import check_system_dependencies
```

```python
check_system_dependencies()
```

Checks if required system dependencies are installed.

- Returns: A list of missing dependencies, or an empty list if all dependencies are met.

#### `setup_logging`

```python
from s2t.main import setup_logging
```

```python
setup_logging(debug=False)
```

Configures the logging system based on the debug flag.

- `debug`: Whether to enable debug logging.

## Audio Module

The audio module provides functionality for recording audio from the microphone.

### `AudioRecorder`

```python
from s2t.audio import AudioRecorder
```

#### Constructor

```python
AudioRecorder(config)
```

- `config`: Configuration object or dictionary with audio recording settings.

#### Methods

##### `start_recording`

```python
start_recording(callback=None)
```

Starts recording audio from the microphone.

- `callback`: Optional callback function that will be called with each audio frame.
- Returns: `True` if recording started successfully, `False` otherwise.

##### `stop_recording`

```python
stop_recording()
```

Stops recording audio and saves it to a temporary file.

- Returns: Path to the temporary audio file, or `None` if recording failed.

##### `get_audio_level`

```python
get_audio_level(audio_data)
```

Calculates the audio level from raw audio data.

- `audio_data`: Raw audio data as bytes.
- Returns: Audio level as a float between 0.0 and 1.0.

## Backends Module

The backends module provides interfaces for speech-to-text services.

### `get_backend`

```python
from s2t.backends import get_backend
```

```python
get_backend(config)
```

Gets the appropriate speech-to-text backend based on the configuration.

- `config`: Configuration object with backend settings.
- Returns: An instance of a class implementing the `STTBackend` interface.

### `STTBackend`

```python
from s2t.backends.base import STTBackend
```

Abstract base class for speech-to-text backends.

#### Methods

##### `is_available`

```python
is_available()
```

Checks if the backend is available for use.

- Returns: `True` if the backend is available, `False` otherwise.

##### `transcribe`

```python
transcribe(audio_file)
```

Transcribes the given audio file to text.

- `audio_file`: Path to the audio file to transcribe.
- Returns: A dictionary containing the transcription result, with at least a 'text' key.

### `WhisperAPIBackend`

```python
from s2t.backends.whisper_api import WhisperAPIBackend
```

Backend implementation using OpenAI's Whisper API.

#### Constructor

```python
WhisperAPIBackend(config)
```

- `config`: Configuration object with Whisper API settings.

#### Methods

Implements all methods from the `STTBackend` interface.

## Configuration Module

The configuration module provides functionality for loading and managing configuration.

### `load_config`

```python
from s2t.config import load_config
```

```python
load_config(config_path=None)
```

Loads the configuration from the specified path or the default location.

- `config_path`: Optional path to the configuration file. If not provided, the default location will be used.
- Returns: A `S2TConfig` object containing the configuration.

### `DEFAULT_CONFIG_PATH`

```python
from s2t.config import DEFAULT_CONFIG_PATH
```

The default path to the configuration file (`~/.config/s2t/config.yaml`).

### `S2TConfig`

```python
from s2t.config import S2TConfig
```

Pydantic model for configuration validation.

#### Properties

- `backends`: Backend configuration settings
- `popup_recorder`: Popup recorder settings
- `audio`: Audio recording settings

## Popup Recorder Module

The popup recorder module provides a graphical interface for recording audio and converting it to text.

### `PopupRecorder`

```python
from s2t.popup_recorder import PopupRecorder
```

#### Constructor

```python
PopupRecorder(config)
```

- `config`: Configuration object with recorder settings.

#### Methods

##### `start_recording`

```python
start_recording(audio_callback=None)
```

Starts recording audio from the microphone and shows the popup window.

- `audio_callback`: Optional callback function that will be called with each audio frame.
- Returns: `True` if recording started successfully, `False` otherwise.

##### `stop_recording`

```python
stop_recording()
```

Stops recording audio.

- Returns: Path to the audio file, or `None` if recording failed.

##### `transcribe`

```python
transcribe(audio_file)
```

Transcribes the given audio file to text.

- `audio_file`: Path to the audio file to transcribe.
- Returns: The transcribed text, or `None` if transcription failed.

##### `record_and_transcribe`

```python
record_and_transcribe(duration=None)
```

Records audio and transcribes it.

- `duration`: Optional recording duration in seconds. If not provided, recording will continue until stopped or silence is detected.
- Returns: The transcribed text, or `None` if recording or transcription failed.

### `RecordingWindow`

```python
from s2t.popup_recorder import RecordingWindow
```

GTK window for recording audio with visual feedback.

#### Constructor

```python
RecordingWindow(on_stop_callback=None, title="S2T Recording")
```

- `on_stop_callback`: Optional callback function that will be called when the window is closed.
- `title`: Window title.

#### Methods

##### `update_audio_level`

```python
update_audio_level(level)
```

Updates the audio level meter with the given level.

- `level`: Audio level as a float between 0.0 and 1.0.

##### `update_vad_status`

```python
update_vad_status(is_speech, silence_duration=None)
```

Updates the voice activity detection status.

- `is_speech`: Whether speech is currently detected.
- `silence_duration`: Duration of silence in seconds, if applicable.

##### `stop_recording`

```python
stop_recording()
```

Stops recording and closes the window.

## Immediate Popup Module

The immediate popup module provides a popup recorder that starts recording immediately when launched.

### `ImmediatePopupRecorder`

```python
from s2t.immediate_popup import ImmediatePopupRecorder
```

#### Constructor

```python
ImmediatePopupRecorder(config)
```

- `config`: Configuration object with recorder settings.

#### Methods

Inherits all methods from `PopupRecorder`.

### `ImmediateRecordingWindow`

```python
from s2t.immediate_popup import ImmediateRecordingWindow
```

Recording window that starts recording immediately.

#### Constructor

```python
ImmediateRecordingWindow(on_stop_callback=None, title="S2T Recording")
```

- `on_stop_callback`: Optional callback function that will be called when the window is closed.
- `title`: Window title.

## Truly Silent Module

The truly silent module provides a recorder that runs without any GUI or notifications.

### `TrulySilentRecorder`

```python
from s2t.truly_silent import TrulySilentRecorder
```

#### Constructor

```python
TrulySilentRecorder(config)
```

- `config`: Configuration object with recorder settings.

#### Methods

##### `start_recording`

```python
start_recording()
```

Starts recording audio from the microphone.

- Returns: `True` if recording started successfully, `False` otherwise.

##### `stop_recording`

```python
stop_recording()
```

Stops recording audio.

- Returns: Path to the audio file, or `None` if recording failed.

##### `transcribe`

```python
transcribe(audio_file)
```

Transcribes the given audio file to text.

- `audio_file`: Path to the audio file to transcribe.
- Returns: The transcribed text, or `None` if transcription failed.

##### `record_and_transcribe`

```python
record_and_transcribe(duration=None)
```

Records audio for the specified duration and transcribes it.

- `duration`: Optional recording duration in seconds. If not provided, recording will continue until interrupted.
- Returns: The transcribed text, or `None` if recording or transcription failed.
