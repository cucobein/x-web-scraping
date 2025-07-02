"""
Unit tests for ConfigManager
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager"""
    
    def test_load_valid_config_file(self):
        """Test loading a valid config file"""
        config_data = {
            "check_interval": 60,
            "headless": False,
            "accounts": ["user1", "user2", "user3"]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager("test_config.json")
                config = config_manager.load()
                
                assert config["check_interval"] == 60
                assert config["headless"] is False
                assert config["accounts"] == ["user1", "user2", "user3"]
    
    def test_fallback_to_defaults_when_file_missing(self):
        """Test fallback to defaults when config file doesn't exist"""
        with patch("pathlib.Path.exists", return_value=False):
            config_manager = ConfigManager("nonexistent.json")
            config = config_manager.load()
            
            # Should use defaults
            assert config["check_interval"] == 30
            assert config["headless"] is True
            assert config["accounts"] == ["nasa"]
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON in config file"""
        with patch("builtins.open", mock_open(read_data="invalid json content")):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager("invalid_config.json")
                
                with pytest.raises(Exception):
                    config_manager.load()
    
    def test_config_properties(self):
        """Test config property accessors"""
        config_data = {
            "check_interval": 45,
            "headless": True,
            "accounts": ["test1", "test2"]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager("test_config.json")
                
                assert config_manager.check_interval == 45
                assert config_manager.headless is True
                assert config_manager.accounts == ["test1", "test2"]
    
    def test_config_properties_with_defaults(self):
        """Test config properties when using default values"""
        with patch("pathlib.Path.exists", return_value=False):
            config_manager = ConfigManager("nonexistent.json")
            
            assert config_manager.check_interval == 30
            assert config_manager.headless is True
            assert config_manager.accounts == ["nasa"]
    
    def test_config_caching(self):
        """Test that config is cached after first load"""
        config_data = {"check_interval": 100}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(config_data))):
            with patch("pathlib.Path.exists", return_value=True):
                config_manager = ConfigManager("test_config.json")
                
                # First load
                config1 = config_manager.load()
                # Second load should use cached version
                config2 = config_manager.load()
                
                assert config1 is config2  # Same object reference
    
    def test_real_config_file_integration(self):
        """Test with actual config file from the project"""
        config_path = Path("config/config.json")
        
        if config_path.exists():
            config_manager = ConfigManager(str(config_path))
            config = config_manager.load()
            
            # Should have required fields
            assert "check_interval" in config
            assert "headless" in config
            assert "accounts" in config
            assert isinstance(config["accounts"], list)
            assert len(config["accounts"]) > 0 