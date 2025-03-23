"""
Configuration management for S2T using Pydantic for validation.
"""

import json
import logging
import os

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


class S2TConfig(BaseModel):
    """Root configuration model for S2T."""

    audio: AudioConfig = Field(default_factory=AudioConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    backends: BackendsConfig = Field(default_factory=BackendsConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    popup_recorder: PopupRecorderConfig = Field(default_factory=PopupRecorderConfig)


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


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def create_default_config(config_path=DEFAULT_CONFIG_PATH):
    """Create a default configuration file if it doesn't exist."""
    ensure_config_dir()
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
        return create_default_config(config_path)

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


def save_config(config: S2TConfig, config_path=DEFAULT_CONFIG_PATH) -> bool:
    """
    Save configuration to file.

    Args:
        config: Configuration object to save
        config_path: Path to save the configuration to

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_config_dir()
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
