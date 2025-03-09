#!/usr/bin/env python3
"""
Simple tests for the utils module.
"""

import os
import sys
import tempfile

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from s2t.utils import load_dotenv


def test_load_dotenv_file_exists():
    """Test loading environment variables from a .env file that exists."""
    # Create a temporary .env file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("TEST_VAR=test_value\n")
        f.write('ANOTHER_VAR="quoted value"\n')
        env_path = f.name

    try:
        # Clear the environment variables if they exist
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]
        if "ANOTHER_VAR" in os.environ:
            del os.environ["ANOTHER_VAR"]

        # Load the .env file
        result = load_dotenv(env_path)

        # Check that the function returned True
        assert result is True, "load_dotenv returned False when file exists"

        # Check that the environment variables were set
        assert (
            os.environ.get("TEST_VAR") == "test_value"
        ), f"TEST_VAR is {os.environ.get('TEST_VAR')}, expected 'test_value'"
        assert (
            os.environ.get("ANOTHER_VAR") == "quoted value"
        ), f"ANOTHER_VAR is {os.environ.get('ANOTHER_VAR')}, expected 'quoted value'"

        print("test_load_dotenv_file_exists: PASSED")
    except AssertionError as e:
        print(f"test_load_dotenv_file_exists: FAILED - {e}")
    finally:
        # Clean up
        os.unlink(env_path)

        # Clean up environment variables
        if "TEST_VAR" in os.environ:
            del os.environ["TEST_VAR"]
        if "ANOTHER_VAR" in os.environ:
            del os.environ["ANOTHER_VAR"]


def test_load_dotenv_file_not_exists():
    """Test loading environment variables from a .env file that doesn't exist."""
    # Use a non-existent file path
    env_path = "/tmp/non_existent_env_file_for_testing"

    # Make sure the file doesn't exist
    if os.path.exists(env_path):
        os.unlink(env_path)

    try:
        # Load the .env file
        result = load_dotenv(env_path)

        # Check that the function returned False
        assert result is False, "load_dotenv returned True when file doesn't exist"

        print("test_load_dotenv_file_not_exists: PASSED")
    except AssertionError as e:
        print(f"test_load_dotenv_file_not_exists: FAILED - {e}")


if __name__ == "__main__":
    print("Running utils tests...")
    test_load_dotenv_file_exists()
    test_load_dotenv_file_not_exists()
    print("All tests completed.")
