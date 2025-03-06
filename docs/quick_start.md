# DesktopSTT Quick Start Guide

This guide will help you get started with DesktopSTT quickly.

## Installation

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

3. Install the package:
   ```bash
   pip install -e .
   ```

4. Set up your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

## Using the Popup Recorder

The popup recorder provides a graphical interface for recording audio and converting it to text.

### Basic Usage

1. Run the popup recorder:
   ```bash
   desktopstt-popup
   ```

2. A window will appear with a "Recording" indicator and a "Stop Recording" button.

3. Speak into your microphone. The audio level meter will show your voice level.

4. When you're done speaking, either:
   - Click the "Stop Recording" button
   - Close the window
   - Wait for the voice activity detection to detect silence (default: 5 seconds)

5. The transcribed text will be printed to the terminal.

### Silent Mode

For a cleaner output with only the transcribed text:

```bash
desktopstt-popup --silent
```

### Custom Silence Duration

To change how long the recorder waits for silence before stopping:

```bash
desktopstt-popup --silence-duration 3.0
```

### Disable Voice Activity Detection

To record for a fixed duration instead of using voice activity detection:

```bash
desktopstt-popup --time 10 --no-vad
```

## Using the Headless Mode

The headless mode provides a terminal-based interface without any GUI.

### Basic Usage

1. Run the headless mode:
   ```bash
   desktopstt-silent
   ```

2. Speak into your microphone. The recording will stop after 5 seconds by default.

3. The transcribed text will be printed to the terminal.

### Custom Duration

To change the recording duration:

```bash
desktopstt-silent --time 10
```

### Save to File

To save the transcription to a file:

```bash
desktopstt-silent --output transcription.txt
```

## Using the Convenience Scripts

The repository includes two convenience scripts that make it easier to use DesktopSTT from anywhere on your system.

### Installation

```bash
./install_scripts.sh
```

### Usage

1. Position your cursor where you want the text to be inserted.

2. Run one of the convenience scripts:
   ```bash
   desktopstt-popup-silent
   ```
   or
   ```bash
   desktopstt-silent
   ```

3. Speak into your microphone.

4. The transcribed text will be automatically typed at your cursor position.

## Next Steps

- Read the [User Guide](user_guide.md) for more detailed information
- Check out the [API Reference](api_reference.md) if you want to use DesktopSTT programmatically
- See the [Developer Guide](developer_guide.md) if you want to contribute to the project 