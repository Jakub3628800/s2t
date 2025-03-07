"""
Utility functions for DesktopSTT.
"""

import logging
import os

logger = logging.getLogger(__name__)


def load_dotenv(dotenv_path=".env"):
    """
    Load environment variables from a .env file.

    Args:
        dotenv_path: Path to the .env file

    Returns:
        bool: True if the .env file was loaded successfully, False otherwise
    """
    try:
        if not os.path.exists(dotenv_path):
            logger.warning(f".env file not found at {dotenv_path}")
            return False

        logger.info(f"Loading environment variables from {dotenv_path}")
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                os.environ[key] = value
                logger.debug(f"Set environment variable: {key}")

        return True

    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
        return False
