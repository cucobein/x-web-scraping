"""
Unit tests for ConfigManager
"""

import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.config.config_manager import ConfigManager, ConfigMode
from src.services.logger_service import LoggerService


class TestConfigManager:
    """Test cases for ConfigManager"""

    def test_load_valid_config_file(self):
        """Test loading a valid config file"""
        logger = LoggerService()  # Simple logger for tests
        config_data = {
            "check_interval": 60,
            "headless": False,
            "accounts": ["user1", "user2", "user3"],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager(ConfigMode.LOCAL, logger=logger)

                # Test that config was loaded correctly
                assert config_manager.check_interval == 60
                assert config_manager.headless is False
                assert config_manager.accounts == ["user1", "user2", "user3"]

    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in config file"""
        logger = LoggerService()  # Simple logger for tests
        with patch("builtins.open", mock_open(read_data="invalid json content")):
            with patch("pathlib.Path.exists", return_value=True):
                with pytest.raises(json.JSONDecodeError):
                    ConfigManager(ConfigMode.LOCAL, logger=logger)

    def test_config_properties(self):
        """Test that config properties work correctly"""
        logger = LoggerService()  # Simple logger for tests
        config_data = {
            "check_interval": 45,
            "headless": True,
            "accounts": ["test_user"],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager(ConfigMode.LOCAL, logger=logger)

                assert config_manager.check_interval == 45
                assert config_manager.headless is True
                assert config_manager.accounts == ["test_user"]

    def test_config_caching(self):
        """Test that config is cached after first load"""
        logger = LoggerService()  # Simple logger for tests
        config_data = {"check_interval": 100}

        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager(ConfigMode.LOCAL, logger=logger)

                # Config should be loaded and cached
                assert config_manager.check_interval == 100
                assert config_manager.check_interval == 100  # Should use cached value

    def test_real_config_file_integration(self):
        """Test with actual config file from the project"""
        logger = LoggerService()  # Simple logger for tests
        config_path = Path("config/config.json")

        if config_path.exists():
            config_manager = ConfigManager(ConfigMode.LOCAL, logger=logger)

            # Test that config was loaded from real file
            assert config_manager.check_interval > 0
            assert isinstance(config_manager.headless, bool)
            assert isinstance(config_manager.accounts, list)
