# S2T API Reference

This document provides detailed information about the public API of S2T.

## Table of Contents

1. [Audio Module](#audio-module)
2. [Backends Module](#backends-module)
3. [Configuration Module](#configuration-module)
4. [Popup Recorder Module](#popup-recorder-module)
5. [Truly Silent Module](#truly-silent-module)

## Audio Module

The audio module provides functionality for recording audio from the microphone.

### `AudioRecorder`

```python
from s2t.audio import AudioRecorder
```

#### Constructor

```python
AudioRecorder(config=None)
```

- `config`: Optional configuration dictionary. If not provided, the default configuration will be used.

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
get_backend(config=None)
```

Gets the appropriate speech-to-text backend based on the configuration.

- `config`: Optional configuration dictionary. If not provided, the default configuration will be used.
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
WhisperAPIBackend(config=None)
```

- `config`: Optional configuration dictionary. If not provided, the default configuration will be used.

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
- Returns: Configuration dictionary.

### `DEFAULT_CONFIG_PATH`

```python
from s2t.config import DEFAULT_CONFIG_PATH
```

The default path to the configuration file.

## Popup Recorder Module

The popup recorder module provides a graphical interface for recording audio and converting it to text.

### Command-Line Interface

```
python -m s2t.popup_recorder [options]
```

#### Options

- `--time SECONDS`: Recording time in seconds (default: record until stopped)
- `--output FILE`: Output file for transcription (default: print to stdout)
- `--config FILE`: Path to config file (default: ~/.config/s2t/config.yaml)
- `--env-file FILE`: Path to .env file (default: .env)
- `--debug`: Enable debug logging
- `--silent`: Output only the transcribed text (no logging)
- `--no-vad`: Disable voice activity detection
- `--silence-threshold THRESHOLD`: Threshold for silence detection (0.0-1.0, default: 0.1)
- `--silence-duration SECONDS`: Duration of silence before stopping (seconds, default: 5.0)
- `--min-recording-time SECONDS`: Minimum recording time before VAD kicks in (seconds, default: 3.0)

### `PopupRecorder`

```python
from s2t.popup_recorder import PopupRecorder
```

#### Constructor

```python
PopupRecorder(config=None)
```

- `config`: Optional configuration dictionary. If not provided, the default configuration will be used.

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

- `duration`: Optional recording duration in seconds. If not provided, recording will continue until stopped.
- Returns: The transcribed text, or `None` if recording or transcription failed.

## Truly Silent Module

The truly silent module provides a terminal-based interface without any GUI.

### Command-Line Interface

```
python -m s2t.truly_silent [options]
```

#### Options

- `--time SECONDS`: Recording time in seconds (default: 5.0)
- `--output FILE`: Output file for transcription (default: print to stdout)
- `--config FILE`: Path to config file (default: ~/.config/s2t/config.yaml)
- `--env-file FILE`: Path to .env file (default: .env)

### `TrulySilentRecorder`

```python
from s2t.truly_silent import TrulySilentRecorder
```

#### Constructor

```python
TrulySilentRecorder(config=None)
```

- `config`: Optional configuration dictionary. If not provided, the default configuration will be used.

#### Methods

##### `record_and_transcribe`

```python
record_and_transcribe(duration=5.0)
```

Records audio and transcribes it.

- `duration`: Recording duration in seconds (default: 5.0).
- Returns: The transcribed text, or `None` if recording or transcription failed.
