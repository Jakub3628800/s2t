#!/usr/bin/env python3
"""
Tests for the internal configuration functions (prefixed with underscore).
"""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

from s2t.config import (
    S2TConfig,
    _create_default_config,
    _deep_update,
    _ensure_config_dir,
    _parse_arguments,
    _save_config,
    _test_openai_api_key,
)


class TestConfigInternal(unittest.TestCase):
    """Tests for the internal configuration functions."""

    def test_deep_update(self):
        """Test the _deep_update function correctly merges dictionaries."""
        # Test basic merge
        target = {"a": 1, "b": 2}
        source = {"b": 3, "c": 4}
        result = _deep_update(target, source)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 4})

        # Test nested merge
        target = {"a": {"x": 1, "y": 2}, "b": 2}
        source = {"a": {"y": 3, "z": 4}, "c": 5}
        result = _deep_update(target, source)
        self.assertEqual(result, {"a": {"x": 1, "y": 3, "z": 4}, "b": 2, "c": 5})

        # Test list merge
        target = {"a": [1, 2], "b": 2}
        source = {"a": [3, 4], "c": 5}
        result = _deep_update(target, source)
        self.assertEqual(result, {"a": [1, 2, 3, 4], "b": 2, "c": 5})

    @patch("s2t.config.os.makedirs")
    def test_ensure_config_dir(self, mock_makedirs):
        """Test the _ensure_config_dir function creates the directory."""
        _ensure_config_dir()
        mock_makedirs.assert_called_once()

    @patch("s2t.config._ensure_config_dir")
    @patch("s2t.config.open", new_callable=unittest.mock.mock_open)
    @patch("s2t.config.yaml.dump")
    @patch("s2t.config.os.path.exists")
    def test_create_default_config_yaml(
        self, mock_exists, mock_yaml_dump, mock_open, mock_ensure_config_dir
    ):
        """Test the _create_default_config function with YAML output."""
        # Mock os.path.exists to return False to force file creation
        mock_exists.return_value = False

        with tempfile.NamedTemporaryFile(suffix=".yaml") as temp_file:
            config = _create_default_config(temp_file.name)
            self.assertIsInstance(config, S2TConfig)
            mock_ensure_config_dir.assert_called_once()
            mock_open.assert_called_once()
            mock_yaml_dump.assert_called_once()

    @patch("s2t.config._ensure_config_dir")
    @patch("s2t.config.open", new_callable=unittest.mock.mock_open)
    @patch("s2t.config.json.dump")
    @patch("s2t.config.os.path.exists")
    def test_create_default_config_json(
        self, mock_exists, mock_json_dump, mock_open, mock_ensure_config_dir
    ):
        """Test the _create_default_config function with JSON output."""
        # Mock os.path.exists to return False to force file creation
        mock_exists.return_value = False

        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            config = _create_default_config(temp_file.name)
            self.assertIsInstance(config, S2TConfig)
            mock_ensure_config_dir.assert_called_once()
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()

    @patch("s2t.config._ensure_config_dir")
    @patch("s2t.config.open", new_callable=unittest.mock.mock_open)
    @patch("s2t.config.yaml.dump")
    def test_save_config_yaml(self, mock_yaml_dump, mock_open, mock_ensure_config_dir):
        """Test the _save_config function with YAML output."""
        config = S2TConfig()
        with tempfile.NamedTemporaryFile(suffix=".yaml") as temp_file:
            result = _save_config(config, temp_file.name)
            self.assertTrue(result)
            mock_ensure_config_dir.assert_called_once()
            mock_open.assert_called_once()
            mock_yaml_dump.assert_called_once()

    @patch("s2t.config._ensure_config_dir")
    @patch("s2t.config.open", new_callable=unittest.mock.mock_open)
    @patch("s2t.config.json.dump")
    def test_save_config_json(self, mock_json_dump, mock_open, mock_ensure_config_dir):
        """Test the _save_config function with JSON output."""
        config = S2TConfig()
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            result = _save_config(config, temp_file.name)
            self.assertTrue(result)
            mock_ensure_config_dir.assert_called_once()
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()

    @patch("s2t.config._ensure_config_dir")
    def test_save_config_error(self, mock_ensure_config_dir):
        """Test the _save_config function handles errors gracefully."""
        mock_ensure_config_dir.side_effect = Exception("Test error")
        config = S2TConfig()
        result = _save_config(config)
        self.assertFalse(result)

    @patch("s2t.config.openai.OpenAI")
    def test_test_openai_api_key_valid(self, mock_openai):
        """Test the _test_openai_api_key function with a valid key."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.models.list.return_value = ["model1", "model2"]

        # Test with a valid API key
        result = _test_openai_api_key("valid_key")
        self.assertTrue(result)
        mock_openai.assert_called_once_with(api_key="valid_key")
        mock_client.models.list.assert_called_once()

    @patch("s2t.config.openai.OpenAI")
    def test_test_openai_api_key_invalid(self, mock_openai):
        """Test the _test_openai_api_key function with an invalid key."""
        # Setup mock
        mock_openai.side_effect = Exception("Invalid API key")

        # Test with an invalid API key
        result = _test_openai_api_key("invalid_key")
        self.assertFalse(result)
        mock_openai.assert_called_once_with(api_key="invalid_key")

    def test_test_openai_api_key_empty(self):
        """Test the _test_openai_api_key function with an empty key."""
        result = _test_openai_api_key("")
        self.assertFalse(result)

    def test_parse_arguments_defaults(self):
        """Test the _parse_arguments function with default values."""
        args = _parse_arguments([])
        self.assertFalse(args.silent)
        self.assertFalse(args.newline)
        self.assertIsNone(args.threshold)
        self.assertIsNone(args.duration)
        self.assertFalse(args.debug)

    def test_parse_arguments_custom(self):
        """Test the _parse_arguments function with custom values."""
        args = _parse_arguments(
            ["--silent", "--newline", "--threshold", "0.1", "--duration", "3.0", "--debug"]
        )
        self.assertTrue(args.silent)
        self.assertTrue(args.newline)
        self.assertEqual(args.threshold, 0.1)
        self.assertEqual(args.duration, 3.0)
        self.assertTrue(args.debug)


if __name__ == "__main__":
    unittest.main()
