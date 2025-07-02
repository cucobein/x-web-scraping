"""
Configuration management for X Feed Monitor
"""
import json
from pathlib import Path
from typing import Dict, List, Any


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self._config = None
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self._config is None:
            self._config = self._load_from_file()
        return self._config
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Config loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"⚠️ Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            raise
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "check_interval": 30,
            "headless": True,
            "accounts": ["nasa"]
        }
    
    @property
    def check_interval(self) -> int:
        """Get check interval in seconds"""
        return self.load().get("check_interval", 60)
    

    
    @property
    def headless(self) -> bool:
        """Get headless mode setting"""
        return self.load().get("headless", True)
    
    @property
    def page_timeout(self) -> int:
        """Get page timeout in milliseconds"""
        return self.load().get("page_timeout", 5000)
    
    @property
    def accounts(self) -> List[str]:
        """Get list of accounts to monitor"""
        return self.load().get("accounts", [])
    
    @property
    def telegram_endpoint(self) -> str:
        """Get Telegram endpoint URL"""
        telegram_config = self.load().get("telegram", {})
        return telegram_config.get("endpoint", "")
    
    @property
    def telegram_api_key(self) -> str:
        """Get Telegram API key"""
        telegram_config = self.load().get("telegram", {})
        return telegram_config.get("api_key", "")
    
    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        telegram_config = self.load().get("telegram", {})
        return bool(telegram_config.get("endpoint") and telegram_config.get("api_key")) 