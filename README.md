# s2t - Speech-to-Text Tool

A lightweight background dictation tool for Wayland desktops using [Whisper.cpp](https://github.com/ggerganov/whisper.cpp). Record speech via global keyboard shortcut and have it transcribed directly at your cursor.

## Features

- **Background dictation**: Runs silently in the background, triggered by keyboard shortcuts
- **Wayland native**: Types text at cursor using `wtype` (works in any application)
- **Multiple modes**: Push-to-talk (default) or Enter-key activation
- **Output options**: Print to stdout, send to tmux, or type at cursor
- **Model fallback**: Automatically tries 'small' model, falls back to 'tiny' if unavailable
- **Clean error handling**: Comprehensive logging for debugging

## Installation

### Quick Install (Recommended)

```bash
uv tool install git+https://github.com/Jakub3628800/s2t.git
```

This installs `s2t` globally and makes it available system-wide.

### From Source

```bash
git clone https://github.com/Jakub3628800/s2t.git
cd s2t
uv pip install -e .
```

### System Dependencies

PyAudio requires PortAudio libraries. Install them via your distribution's package manager:
- Look for packages named `portaudio` or `portaudio19-dev`
- Check PyAudio documentation for your specific distribution

You'll also need `wtype` for typing functionality:
```bash
# Install wtype from your package manager
# Package name is typically "wtype"
```

## Usage

### Sway Integration (Recommended)

Add to your `~/.config/sway/config`:

#### Option 1: Hold-to-Record (Walkie-Talkie Style)

```
# Hold Super+Space to record, release to transcribe and type
bindsym $mod+Space exec pkill -9 s2t; s2t --type
bindsym --release $mod+Space exec pkill -SIGINT s2t
```

**How it works:**
1. Hold Super+Space
2. Speak into your microphone
3. Release Super+Space
4. Text appears at your cursor

#### Option 2: Toggle Mode (Press to Start/Stop)

```
# Press once to start, press again to stop
bindsym $mod+Space exec "pgrep s2t && pkill -SIGINT s2t || s2t --type"
```

#### Option 3: Separate Keys

```
# Super+Space to start recording
bindsym $mod+Space exec s2t --type

# Super+Shift+Space to stop and transcribe
bindsym $mod+Shift+Space exec pkill -SIGINT s2t
```

After adding the configuration, reload Sway:
```bash
swaymsg reload
```

### Standalone Usage

#### Push-to-Talk Mode
```bash
s2t --type
```
Press Ctrl+C to stop recording and transcribe.

#### Enter-Key Mode
```bash
s2t --enter --type
```
Press Enter to start/stop recording.

#### Send to Tmux Session
```bash
s2t --tmux SESSION_NAME
```
Transcription will be sent as command input to the specified tmux session.

#### Print to Stdout Only
```bash
s2t
```
Records audio and prints transcription (no typing).

## Options

- `--enter`: Use Enter key for start/stop (instead of push-to-talk)
- `--tmux SESSION, -t SESSION`: Send transcription to tmux session
- `--type`: Type transcription at cursor using wtype

## First Run

On first use, Whisper will download model files:
- **tiny model**: ~75 MB (faster, less accurate)
- **small model**: ~500 MB (slower, more accurate)

The tool tries 'small' first, falls back to 'tiny' if unavailable. Models are cached for subsequent runs.

## Troubleshooting

### Audio Input Issues
- Verify your microphone works: `arecord -d 5 test.wav`
- Check PyAudio can access your microphone
- Ensure PortAudio libraries are installed

### Typing Not Working
- Install `wtype`: Check your distribution's package manager
- Verify wtype works: `wtype "test"`
- Only works on Wayland (not X11)

### Model Download Errors
- Requires internet connection on first run
- Models cached at `~/.cache/whisper` or similar
- If 'small' fails to download, 'tiny' will be used automatically

### Sway Shortcut Not Working
- Reload Sway config: `swaymsg reload`
- Check if s2t is in PATH: `which s2t`
- Test manually first: `s2t --type` then Ctrl+C

## Development

Run tests:
```bash
make test
```

## License

MIT
