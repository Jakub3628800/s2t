"""
Configuration management for S2T using Pydantic for validation.
"""

import argparse
import json
import logging
import os
import shutil
import subprocess

import openai
import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Default configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/s2t")
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")


class AudioConfig(BaseModel):
    """Audio configuration settings."""

    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    file_format: str = "wav"
    device_index: int | None = None


class UIConfig(BaseModel):
    """User interface configuration settings."""

    theme: str = "system"
    window_width: int = 800
    window_height: int = 600
    show_in_tray: bool = True


class WhisperAPIConfig(BaseModel):
    """Configuration for OpenAI Whisper API."""

    api_key: str = ""
    model: str = "whisper-1"
    language: str = "en"
    temperature: float = 0
    response_format: str = "json"


class BackendsConfig(BaseModel):
    """Speech recognition backends configuration."""

    default: str = "whisper_api"
    whisper_api: WhisperAPIConfig = Field(default_factory=WhisperAPIConfig)


class OutputConfig(BaseModel):
    """Output formatting and saving configuration."""

    output_format: str = "text"
    save_audio: bool = False
    transcriptions_dir: str = Field(default=os.path.expanduser("~/Documents/S2T"))


class PopupRecorderConfig(BaseModel):
    """Popup recorder configuration settings."""

    vad_enabled: bool = True
    silence_threshold: float = 0.1
    silence_duration: float = 5.0
    min_recording_time: float = 3.0


class CLIConfig(BaseModel):
    """Command-line interface configuration."""

    silent: bool = False
    newline: bool = False
    debug: bool = False
    config_path: str = DEFAULT_CONFIG_PATH


class S2TConfig(BaseModel):
    """Root configuration model for S2T."""

    audio: AudioConfig = Field(default_factory=AudioConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    backends: BackendsConfig = Field(default_factory=BackendsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    popup_recorder: PopupRecorderConfig = Field(default_factory=PopupRecorderConfig)
    cli: CLIConfig = Field(default_factory=CLIConfig)


# Create a DEFAULT_CONFIG dictionary for backward compatibility with tests
# This converts the default Pydantic model to a dictionary
DEFAULT_CONFIG = S2TConfig().model_dump()


def _deep_update(target, source):
    """
    Deep update target dict with source.

    For each k,v in source: if k exists in target and v is a dict, deep update.
    If v is a list, extend target[k] with v, otherwise replace target[k] with v.

    Args:
        target (dict): Target dictionary to update
        source (dict): Source dictionary with new values

    Returns:
        dict: Updated target dictionary
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        elif key in target and isinstance(target[key], list) and isinstance(value, list):
            target[key].extend(value)
        else:
            target[key] = value
    return target


def _ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _create_default_config(config_path=DEFAULT_CONFIG_PATH):
    """Create a default configuration file if it doesn't exist."""
    _ensure_config_dir()
    config = S2TConfig()

    if not os.path.exists(config_path):
        # Determine file format based on extension
        if config_path.endswith((".yaml", ".yml")):
            with open(config_path, "w") as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False)
        elif config_path.endswith(".json"):
            with open(config_path, "w") as f:
                json.dump(config.model_dump(), f, indent=2)
        else:
            # Default to YAML if extension is unknown
            with open(config_path, "w") as f:
                yaml.dump(config.model_dump(), f, default_flow_style=False)

        logger.info(f"Created default configuration at {config_path}")

    return config


def load_config(config_path=DEFAULT_CONFIG_PATH) -> S2TConfig:
    """
    Load configuration from file, creating default if needed.

    Args:
        config_path: Path to the configuration file (YAML or JSON)

    Returns:
        S2TConfig: The loaded and validated configuration
    """
    if not os.path.exists(config_path):
        return _create_default_config(config_path)

    try:
        # Determine file format based on extension
        if config_path.endswith((".yaml", ".yml")):
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
        elif config_path.endswith(".json"):
            with open(config_path) as f:
                config_data = json.load(f)
        else:
            # Try YAML by default
            with open(config_path) as f:
                config_data = yaml.safe_load(f)

        logger.info(f"Loaded configuration from {config_path}")

        # Create and validate Pydantic model
        config = S2TConfig(**config_data)
        return config

    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Return default config on error
        return S2TConfig()


def _save_config(config: S2TConfig, config_path=DEFAULT_CONFIG_PATH) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration object to save
        config_path: Path to save the configuration to

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        _ensure_config_dir()
        config_dict = config.model_dump()

        # Determine file format based on extension
        if config_path.endswith((".yaml", ".yml")):
            with open(config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        elif config_path.endswith(".json"):
            with open(config_path, "w") as f:
                json.dump(config_dict, f, indent=2)
        else:
            # Default to YAML if extension is unknown
            with open(config_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False)

        logger.info(f"Saved configuration to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False


def send_notification(title, message, urgency="normal"):
    """
    Send a desktop notification using notify-send.

    Args:
        title: The notification title
        message: The notification message
        urgency: The urgency level ('low', 'normal', or 'critical')

    Returns:
        bool: True if the notification was sent successfully, False otherwise
    """
    # Use full path for notify-send to ensure it works in all environments
    notify_send_path = shutil.which("notify-send")
    if notify_send_path:
        try:
            # We're explicitly using a full path from shutil.which and not injecting user input,
            # so this is safe. We need to disable the S603 warning.
            subprocess.run(  # noqa: S603 - Using full path from shutil.which, not user input
                [
                    notify_send_path,
                    "-u",
                    urgency,
                    title,
                    message,
                ],
                check=False,
                capture_output=True,
                shell=False,  # Explicitly set shell=False for security
            )
            logger.debug(f"Sent notification: {title} - {message}")
            return True
        except Exception as e:
            logger.warning(f"Failed to send notification: {e}")
            return False
    else:
        logger.debug("notify-send not found, notification not sent")
        return False


def setup_logging(debug=False):
    """Configure the logging system based on debug flag."""
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure s2t logger
    logger.setLevel(log_level)

    # Add console handler if not already present
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


def _test_openai_api_key(api_key: str) -> bool:
    """
    Test if the OpenAI API key is valid by making a minimal test request.

    Args:
        api_key: OpenAI API key to test

    Returns:
        bool: True if the API key is valid, False otherwise
    """
    if not api_key:
        logger.warning("No API key provided to test")
        return False

    try:
        # Create a minimal client to test the API key
        client = openai.OpenAI(api_key=api_key)

        # Make a minimal models list request to check if the key is valid
        # This is more efficient than making an actual transcription request
        client.models.list(limit=1)

        logger.info("OpenAI API key is valid")
        return True
    except Exception as e:
        logger.error(f"OpenAI API key validation failed: {e}")
        return False


def _parse_arguments(args=None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Command-line arguments to parse. If None, sys.argv is used.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="S2T (Speech to Text) - A command-line tool for speech recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--silent", action="store_true", help="Use silent mode (no GUI window)")
    parser.add_argument(
        "--newline", action="store_true", help="Add a newline character after the transcription"
    )
    parser.add_argument(
        "--threshold", type=float, default=None, help="Silence threshold (0.0-1.0, default: 0.05)"
    )
    parser.add_argument(
        "--duration", type=float, default=None, help="Silence duration in seconds (default: 2.0)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument(
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to configuration file (YAML or JSON, default: {DEFAULT_CONFIG_PATH})",
    )

    return parser.parse_args(args)


def get_validated_config(args=None) -> S2TConfig:
    """
    Process command-line arguments and return a validated configuration.
    This function handles all the logic of loading the configuration, applying
    command-line overrides, and validating the final configuration.

    Args:
        args: Command-line arguments to parse. If None, sys.argv is used.

    Returns:
        S2TConfig: The validated configuration
    """
    # Parse command-line arguments
    parsed_args = _parse_arguments(args)

    # Setup logging based on debug flag
    setup_logging(parsed_args.debug)

    # Validate the config file extension
    if parsed_args.config:
        if not os.path.exists(parsed_args.config):
            # This will create a default config at the specified path
            logger.info(
                f"Config file not found, will create a default config at: " f"{parsed_args.config}"
            )
        # Ensure the config file has a valid extension
        elif not parsed_args.config.endswith((".yaml", ".yml", ".json")):
            logger.warning(
                f"Config file should have .yaml, .yml, or .json extension. "
                f"Found: {parsed_args.config}"
            )
            logger.warning("Will attempt to load it anyway, assuming YAML format.")

    # Load configuration from specified path
    config = load_config(parsed_args.config)

    # Update CLI config with parsed arguments
    config.cli.silent = parsed_args.silent
    config.cli.newline = parsed_args.newline
    config.cli.debug = parsed_args.debug
    config.cli.config_path = parsed_args.config

    # Override specific configuration settings from command line if provided
    if parsed_args.threshold is not None:
        config.popup_recorder.silence_threshold = parsed_args.threshold

    if parsed_args.duration is not None:
        config.popup_recorder.silence_duration = parsed_args.duration

    # Enable VAD by default
    config.popup_recorder.vad_enabled = True

    # Check for OpenAI API key in environment variables if not in config
    api_key = config.backends.whisper_api.api_key
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        # Set the API key in the config if found in environment
        if api_key:
            config.backends.whisper_api.api_key = api_key

    return config
