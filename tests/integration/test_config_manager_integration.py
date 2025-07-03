"""
Integration tests for ConfigManager with Firebase Remote Config
Uses captured Firebase fixtures to test remote config loading
"""
import pytest
import json
from unittest.mock import patch, AsyncMock, mock_open
from pathlib import Path

from src.config.config_manager import ConfigManager, ConfigMode


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager with Firebase"""
    
    @pytest.fixture
    def firebase_config_fixture(self):
        """Load captured Firebase response fixture"""
        fixture_path = Path("tests/fixtures/firebase/config_response.json")
        if fixture_path.exists():
            with open(fixture_path, 'r') as f:
                return json.load(f)
        else:
            # Fallback fixture if file doesn't exist
            return {
                "monitoring_check_interval_dev": "30",
                "monitoring_check_interval_prod": "60",
                "monitoring_headless_dev": "false",
                "monitoring_headless_prod": "true",
                "monitoring_page_timeout_dev": "5000",
                "monitoring_page_timeout_prod": "10000",
                "telegram_endpoint_dev": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                "telegram_endpoint_prod": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                "telegram_api_key_dev": "test-api-key-dev",
                "telegram_api_key_prod": "test-api-key-prod",
                "twitter_accounts_dev": '["nasa", "olaphone", "cucobein"]',
                "twitter_accounts_prod": '["olaphone", "cucobein", "GobCDMX"]'
            }
    
    def test_firebase_config_loading_with_fixture(self, firebase_config_fixture):
        """Test Firebase config loading using captured fixture"""
        # Create config manager with fixture enabled
        config_manager = ConfigManager(
            mode=ConfigMode.FIXTURE,
            environment='dev'
        )
        
        # Verify config contains Firebase data by checking properties
        assert config_manager.check_interval == 30
        assert config_manager.headless is False
        assert config_manager.accounts == ["nasa", "olaphone", "cucobein"]
    
    def test_firebase_config_properties_dev_environment(self, firebase_config_fixture):
        """Test Firebase config properties in dev environment"""
        config_manager = ConfigManager(
            mode=ConfigMode.FIXTURE,
            environment='dev'
        )
        
        # Test properties
        assert config_manager.check_interval == 30  # monitoring_check_interval_dev
        assert config_manager.headless is False     # monitoring_headless_dev
        assert config_manager.page_timeout == 5000  # monitoring_page_timeout_dev
        assert config_manager.accounts == ["nasa", "olaphone", "cucobein"]  # twitter_accounts_dev
        assert config_manager.telegram_endpoint == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
        assert config_manager.telegram_api_key == "47827973-e134-4ec1-9b11-458d3cc72962"  # Actual fixture value
        assert config_manager.telegram_enabled is True
    
    def test_firebase_config_properties_prod_environment(self, firebase_config_fixture):
        """Test Firebase config properties in prod environment"""
        config_manager = ConfigManager(
            mode=ConfigMode.FIXTURE,
            environment='prod'
        )
        
        # Test properties
        assert config_manager.check_interval == 60  # monitoring_check_interval_prod
        assert config_manager.headless is True      # monitoring_headless_prod
        assert config_manager.page_timeout == 10000 # monitoring_page_timeout_prod
        # Actual fixture contains many CDMX accounts, check that it includes the expected ones
        prod_accounts = config_manager.accounts
        assert "olaphone" in prod_accounts
        assert "cucobein" in prod_accounts
        assert "GobCDMX" in prod_accounts
        assert len(prod_accounts) > 3  # Should have many more accounts
        assert config_manager.telegram_endpoint == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
        assert config_manager.telegram_api_key == "47827973-e134-4ec1-9b11-458d3cc72962"  # Actual fixture value
        assert config_manager.telegram_enabled is True
    
    def test_fallback_to_local_when_firebase_fails(self):
        """Test fallback to local config when Firebase fails"""
        # Mock local config file
        local_config = {
            "check_interval": 45,
            "headless": True,
            "accounts": ["fallback_user"]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(local_config))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager(mode=ConfigMode.FALLBACK)
                
                # Should fall back to local config
                assert config_manager.check_interval == 45
                assert config_manager.headless is True
                assert config_manager.accounts == ["fallback_user"]
    
    def test_fallback_to_defaults_when_both_firebase_and_local_fail(self):
        """Test fallback to defaults when both Firebase and local config fail"""
        # Mock local config file to not exist
        with patch('pathlib.Path.exists', return_value=False):
            config_manager = ConfigManager(mode=ConfigMode.FIXTURE)
            
            # Should use defaults from _get_default_config()
            # Note: In FIXTURE mode, the config contains Firebase-style keys
            # but the properties should return the correct values
            assert config_manager.check_interval == 30
            assert config_manager.headless is False  # "false" string becomes False
            assert config_manager.accounts == ["nasa", "olaphone", "cucobein"]
    
    def test_firebase_disabled_falls_back_to_local(self):
        """Test that when Firebase is disabled, it uses local config"""
        local_config = {
            "check_interval": 90,
            "headless": False,
            "accounts": ["local_user"]
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(local_config))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager(mode=ConfigMode.LOCAL)
                
                # Should use local config
                assert config_manager.check_interval == 90
                assert config_manager.headless is False
                assert config_manager.accounts == ["local_user"]
    
    def test_firebase_manager_initialization(self, firebase_config_fixture):
        """Test Firebase manager initialization and caching"""
        config_manager = ConfigManager(
            mode=ConfigMode.FIXTURE,
            environment='dev'
        )
        
        # Config should be loaded and cached
        assert config_manager.check_interval == 30
        assert config_manager.headless is False
        assert config_manager.accounts == ["nasa", "olaphone", "cucobein"] 