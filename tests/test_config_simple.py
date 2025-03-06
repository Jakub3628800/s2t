#!/usr/bin/env python3
"""
Simple test for the configuration module.
"""

import os
import sys
import tempfile
import json

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktopstt.config import load_config

def test_default_config():
    """Test that the default configuration is loaded correctly."""
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('{}')  # Empty config
        config_path = f.name

    try:
        # Load the config
        config = load_config(config_path)

        # Check that the default values are set
        assert 'backends' in config, "backends not in config"
        assert 'whisper_api' in config['backends'], "whisper_api not in backends"
        assert 'api_key' in config['backends']['whisper_api'], "api_key not in whisper_api"

        # Check audio settings
        assert 'audio' in config, "audio not in config"

        # The actual structure has sample_rate directly in the audio config
        assert 'sample_rate' in config['audio'], "sample_rate not in audio"
        assert config['audio']['sample_rate'] == 16000, f"sample_rate is {config['audio']['sample_rate']}, expected 16000"

        # Check other audio settings
        assert 'channels' in config['audio'], "channels not in audio"
        assert config['audio']['channels'] == 1, f"channels is {config['audio']['channels']}, expected 1"

        assert 'chunk_size' in config['audio'], "chunk_size not in audio"
        assert config['audio']['chunk_size'] == 1024, f"chunk_size is {config['audio']['chunk_size']}, expected 1024"

        print("test_default_config: PASSED")
    except AssertionError as e:
        print(f"test_default_config: FAILED - {e}")
    finally:
        # Clean up
        os.unlink(config_path)

def test_merge_config():
    """Test that user configuration is merged with defaults."""
    # Create a temporary config file with custom settings
    custom_config = {
        'audio': {
            'recorder': {
                'sample_rate': 44100
            }
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        json.dump(custom_config, f)
        config_path = f.name

    try:
        # Load the config
        config = load_config(config_path)

        # Check that the custom value is used
        assert config['audio']['recorder']['sample_rate'] == 44100, f"sample_rate is {config['audio']['recorder']['sample_rate']}, expected 44100"

        # Check that default values for other settings are still present
        assert 'backends' in config, "backends not in config"
        assert 'whisper_api' in config['backends'], "whisper_api not in backends"

        print("test_merge_config: PASSED")
    except AssertionError as e:
        print(f"test_merge_config: FAILED - {e}")
    finally:
        # Clean up
        os.unlink(config_path)

if __name__ == "__main__":
    print("Running configuration tests...")
    test_default_config()
    test_merge_config()
    print("All tests completed.")
