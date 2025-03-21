"""
Configuration management for S2T.
"""

import logging
import os

import yaml

logger = logging.getLogger(__name__)

# Default configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/s2t")
DEFAULT_CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")

# Default configuration
DEFAULT_CONFIG = {
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024,
        "format": "wav",
        "device_index": None,  # Use default device
    },
    "ui": {
        "theme": "system",
        "window_width": 800,
        "window_height": 600,
        "show_in_tray": True,
    },
    "backends": {
        "default": "whisper_api",
        "whisper_api": {
            "api_key": "",  # Will be loaded from environment variable
            "model": "whisper-1",
            "language": "en",
            "temperature": 0,
            "response_format": "json",
        },
    },
    "output": {
        "format": "text",
        "save_audio": False,
        "transcriptions_dir": os.path.expanduser("~/Documents/S2T"),
    },
    "popup_recorder": {
        "vad_enabled": True,
        "silence_threshold": 0.1,
        "silence_duration": 5.0,
        "min_recording_time": 3.0,
    },
}


def ensure_config_dir():
    """Ensure the configuration directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def create_default_config(config_path=DEFAULT_CONFIG_PATH):
    """Create a default configuration file if it doesn't exist."""
    ensure_config_dir()

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        logger.info(f"Created default configuration at {config_path}")

    return DEFAULT_CONFIG


def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Load configuration from file, creating default if needed."""
    if not os.path.exists(config_path):
        return create_default_config(config_path)

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config_path}")

        # Merge with defaults to ensure all keys exist
        merged_config = DEFAULT_CONFIG.copy()
        _deep_update(merged_config, config)
        return merged_config

    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return DEFAULT_CONFIG


def _deep_update(d, u):
    """Recursively update a dictionary."""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            _deep_update(d[k], v)
        else:
            d[k] = v
