"""
Tests for the utils module.
"""

import os
import tempfile
import unittest

from s2t.utils import load_dotenv


class TestUtils(unittest.TestCase):
    """Tests for the utils module."""

    def test_load_dotenv_file_exists(self):
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
            self.assertTrue(result)

            # Check that the environment variables were set
            self.assertEqual(os.environ.get("TEST_VAR"), "test_value")
            self.assertEqual(os.environ.get("ANOTHER_VAR"), "quoted value")
        finally:
            # Clean up
            os.unlink(env_path)

            # Clean up environment variables
            if "TEST_VAR" in os.environ:
                del os.environ["TEST_VAR"]
            if "ANOTHER_VAR" in os.environ:
                del os.environ["ANOTHER_VAR"]

    def test_load_dotenv_file_not_exists(self):
        """Test loading environment variables from a .env file that doesn't exist."""
        # Use a non-existent file path
        env_path = "/tmp/non_existent_env_file_for_testing"

        # Make sure the file doesn't exist
        if os.path.exists(env_path):
            os.unlink(env_path)

        # Load the .env file
        result = load_dotenv(env_path)

        # Check that the function returned False
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
