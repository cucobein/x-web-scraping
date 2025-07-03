"""
Configuration management for X Feed Monitor with Firebase Remote Config support
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.config.firebase_config_manager import FirebaseConfigManager
from src.utils.env_helper import get_environment


class ConfigManager:
    """Manages application configuration with Firebase Remote Config support"""
    
    def __init__(self, config_path: str = "config/config.json", use_firebase: bool = True, environment: str = None, fixture_path: str = None):
        self.config_path = Path(config_path)
        self.use_firebase = use_firebase
        self.environment = environment or get_environment()
        self.fixture_path = fixture_path
        self._config = None
        self._firebase_manager = None
        
        # Firebase configuration
        self.project_id = "web-scraper-e14ff"
        self.service_account_path = "config/web-scraper-e14ff-firebase-adminsdk-fbsvc-2f32bfbd7b.json"
    
    def load(self) -> Dict[str, Any]:
        """Load configuration - Firebase if enabled, otherwise local JSON"""
        if self._config is None:
            if self.fixture_path:
                self._config = self._load_from_fixture()
            elif self.use_firebase:
                self._config = self._load_from_firebase_with_fallback()
            else:
                self._config = self._load_from_file()
        return self._config
    
    def _load_from_firebase_with_fallback(self) -> Dict[str, Any]:
        """Load from Firebase with fallback to local JSON"""
        try:
            return asyncio.run(self._load_from_firebase())
        except Exception as e:
            print(f"⚠️ Firebase config failed: {e}, falling back to local config")
            return self._load_from_file()
    
    async def _load_from_firebase(self) -> Dict[str, Any]:
        """Async Firebase loading"""
        await self._ensure_firebase_manager()
        return await self._firebase_manager.load_config()
    
    def _load_from_fixture(self) -> Dict[str, Any]:
        """Load configuration from fixture file"""
        try:
            with open(self.fixture_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Config loaded from fixture: {self.fixture_path}")
            return config
        except FileNotFoundError:
            print(f"⚠️ Fixture file {self.fixture_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing fixture file: {e}")
            raise
    
    async def _ensure_firebase_manager(self):
        """Ensure Firebase manager is initialized"""
        if self._firebase_manager is None:
            self._firebase_manager = FirebaseConfigManager(self.project_id, self.service_account_path)
    
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
    
    def _get_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value for the current environment"""
        if self._config is None:
            return default
        
        if self.use_firebase and self._firebase_manager:
            try:
                return self._firebase_manager.get_value(key, self._config)
            except KeyError:
                return default
        else:
            # Local JSON mode or fixture mode - try environment-specific key first
            env_key = f"{key}_{self.environment}"
            if env_key in self._config:
                return self._config[env_key]
            # Fallback to base key
            return self._config.get(key, default)
    
    def _parse_json_string(self, value: str) -> Any:
        """Parse JSON string value"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    @property
    def check_interval(self) -> int:
        """Get check interval in seconds"""
        if self.use_firebase:
            value = self._get_value("monitoring_check_interval", "60")
            return int(value)
        else:
            return self.load().get("check_interval", 60)
    
    @property
    def headless(self) -> bool:
        """Get headless mode setting"""
        if self.use_firebase:
            value = self._get_value("monitoring_headless", "true")
            return value.lower() == "true"
        else:
            return self.load().get("headless", True)
    
    @property
    def page_timeout(self) -> int:
        """Get page timeout in milliseconds"""
        if self.use_firebase:
            value = self._get_value("monitoring_page_timeout", "5000")
            return int(value)
        else:
            return self.load().get("page_timeout", 5000)
    
    @property
    def accounts(self) -> List[str]:
        """Get list of accounts to monitor"""
        if self.use_firebase:
            value = self._get_value("twitter_accounts", '["nasa"]')
            return self._parse_json_string(value)
        else:
            return self.load().get("accounts", [])
    
    @property
    def telegram_endpoint(self) -> str:
        """Get Telegram endpoint URL"""
        if self.use_firebase:
            return self._get_value("telegram_endpoint", "")
        else:
            telegram_config = self.load().get("telegram", {})
            return telegram_config.get("endpoint", "")
    
    @property
    def telegram_api_key(self) -> str:
        """Get Telegram API key"""
        if self.use_firebase:
            return self._get_value("telegram_api_key", "")
        else:
            telegram_config = self.load().get("telegram", {})
            return telegram_config.get("api_key", "")
    
    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        endpoint = self.telegram_endpoint
        api_key = self.telegram_api_key
        return bool(endpoint and api_key) 