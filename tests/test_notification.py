#!/usr/bin/env python3
"""
Tests for the notification functionality in the config module.
"""

import unittest
from unittest.mock import MagicMock, patch

from s2t.config import get_validated_config, send_notification


class TestNotification(unittest.TestCase):
    """Tests for the notification functionality."""

    @patch("s2t.config.shutil.which")
    @patch("s2t.config.subprocess.run")
    @patch("s2t.config.logger")
    def test_send_notification_success(self, mock_logger, mock_run, mock_which):
        """Test that send_notification works correctly when notify-send is available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/notify-send"
        mock_run.return_value = MagicMock(returncode=0)

        # Call the function
        result = send_notification("Test Title", "Test Message", "normal")

        # Check results
        self.assertTrue(result)
        mock_which.assert_called_once_with("notify-send")
        mock_run.assert_called_once()
        mock_logger.debug.assert_called_once()

        # Verify subprocess.run was called with correct arguments
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "/usr/bin/notify-send")
        self.assertEqual(args[0][1], "-u")
        self.assertEqual(args[0][2], "normal")
        self.assertEqual(args[0][3], "Test Title")
        self.assertEqual(args[0][4], "Test Message")
        self.assertFalse(kwargs["check"])
        self.assertTrue(kwargs["capture_output"])
        self.assertFalse(kwargs["shell"])

    @patch("s2t.config.shutil.which")
    @patch("s2t.config.logger")
    def test_send_notification_missing_notify_send(self, mock_logger, mock_which):
        """Test that send_notification handles missing notify-send gracefully."""
        # Setup mocks
        mock_which.return_value = None

        # Call the function
        result = send_notification("Test Title", "Test Message", "normal")

        # Check results
        self.assertFalse(result)
        mock_which.assert_called_once_with("notify-send")
        mock_logger.debug.assert_called_once_with("notify-send not found, notification not sent")

    @patch("s2t.config.shutil.which")
    @patch("s2t.config.subprocess.run")
    @patch("s2t.config.logger")
    def test_send_notification_error(self, mock_logger, mock_run, mock_which):
        """Test that send_notification handles errors gracefully."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/notify-send"
        mock_run.side_effect = Exception("Test error")

        # Call the function
        result = send_notification("Test Title", "Test Message", "normal")

        # Check results
        self.assertFalse(result)
        mock_which.assert_called_once_with("notify-send")
        mock_run.assert_called_once()
        mock_logger.warning.assert_called_once()

    @patch("s2t.config.os.environ.get")
    def test_get_validated_config_api_key_from_env(self, mock_environ_get):
        """Test that get_validated_config correctly retrieves API key from environment.

        Ensures the API key is set from environment variables without validation.
        """
        # Setup mock
        test_api_key = "test_api_key_from_env"
        mock_environ_get.return_value = test_api_key

        # Setup arguments
        mock_args = ["--debug"]

        # Call the function
        config = get_validated_config(mock_args)

        # Verify the API key was set from the environment
        self.assertEqual(config.backends.whisper_api.api_key, test_api_key)
        mock_environ_get.assert_called_with("OPENAI_API_KEY", "")


if __name__ == "__main__":
    unittest.main()
