"""
Configuration management for X Feed Monitor with Firebase Remote Config support
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from enum import Enum

from src.config.firebase_config_manager import FirebaseConfigManager
from src.utils.env_helper import get_environment
from src.services.logger_service import LoggerService


class ConfigMode(Enum):
    """Configuration loading modes"""
    LOCAL = "local"      # Load from local config.json
    FIREBASE = "firebase"  # Load from Firebase Remote Config
    FIXTURE = "fixture"    # Load from test fixture file
    FALLBACK = "fallback"  # Load from invalid fixture to test fallback


class ConfigManager:
    """Manages application configuration with Firebase Remote Config support"""
    
    def __init__(self, mode: ConfigMode, environment: str = None, logger: Optional[LoggerService] = None):
        self.mode = mode
        self.environment = environment or get_environment()
        self._config = None
        self._firebase_manager = None
        self.logger = logger or LoggerService()
        
        # Firebase configuration
        self.project_id = "web-scraper-e14ff"
        self.service_account_path = "config/web-scraper-e14ff-firebase-adminsdk-fbsvc-2f32bfbd7b.json"
        
        # Load configuration immediately
        self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration based on mode"""
        if self._config is None:
            if self.mode == ConfigMode.LOCAL:
                self._config = self._load_from_file()
            elif self.mode == ConfigMode.FIREBASE:
                self._config = self._load_from_firebase_with_fallback()
            elif self.mode == ConfigMode.FIXTURE:
                self._config = self._load_from_fixture()
            elif self.mode == ConfigMode.FALLBACK:
                self._config = self._load_from_invalid_fixture_with_fallback()
        return self._config
    
    def refresh(self):
        """Refresh configuration (only for FIREBASE mode)"""
        if self.mode != ConfigMode.FIREBASE:
            return  # Do nothing for LOCAL/FIXTURE modes
        
        try:
            new_config = self._load_from_firebase_with_fallback()
            self._config = new_config  # Update with new values
            self.logger.info("Configuration refreshed from Firebase")
        except Exception as e:
            # Keep existing cached values - don't fall back to local JSON
            self.logger.warning("Firebase refresh failed, keeping existing config", {"error": str(e)})
    
    def _load_from_firebase_with_fallback(self) -> Dict[str, Any]:
        """Load from Firebase with fallback to local JSON"""
        try:
            return asyncio.run(self._load_from_firebase())
        except Exception as e:
            self.logger.warning("Firebase config failed, falling back to local config", {"error": str(e)})
            return self._load_from_file()
    
    async def _load_from_firebase(self) -> Dict[str, Any]:
        """Async Firebase loading"""
        await self._ensure_firebase_manager()
        return await self._firebase_manager.load_config()
    
    def _load_from_fixture(self) -> Dict[str, Any]:
        """Load configuration from fixture file"""
        fixture_path = "tests/fixtures/firebase/config_response.json"
        try:
            with open(fixture_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Config loaded from fixture: {fixture_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"Fixture file {fixture_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing fixture file", {"error": str(e)})
            raise
    
    def _load_from_invalid_fixture_with_fallback(self) -> Dict[str, Any]:
        """Load configuration from invalid fixture to test fallback"""
        fixture_path = "tests/fixtures/firebase/invalid_config.json"
        try:
            with open(fixture_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Config loaded from fallback fixture: {fixture_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"Fallback fixture file {fixture_path} not found, falling back to local config")
            return self._load_from_file()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing fallback fixture file, falling back to local config", {"error": str(e)})
            return self._load_from_file()
    
    async def _ensure_firebase_manager(self):
        """Ensure Firebase manager is initialized"""
        if self._firebase_manager is None:
            self._firebase_manager = FirebaseConfigManager(self.project_id, self.service_account_path)
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        config_path = "config/config.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Config loaded from {config_path}")
            return config
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing config file", {"error": str(e)})
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
        
        if self.mode == ConfigMode.FIREBASE and self._firebase_manager:
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
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            value = self._get_value("monitoring_check_interval", "60")
            return int(value)
        else:
            return self._load().get("check_interval", 60)
    
    @property
    def headless(self) -> bool:
        """Get headless mode setting"""
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            value = self._get_value("monitoring_headless", "true")
            return value.lower() == "true"
        else:
            return self._load().get("headless", True)
    
    @property
    def page_timeout(self) -> int:
        """Get page timeout in milliseconds"""
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            value = self._get_value("monitoring_page_timeout", "5000")
            return int(value)
        else:
            return self._load().get("page_timeout", 5000)
    
    @property
    def accounts(self) -> List[str]:
        """Get list of accounts to monitor"""
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            value = self._get_value("twitter_accounts", '["nasa"]')
            return self._parse_json_string(value)
        else:
            return self._load().get("accounts", [])
    
    @property
    def telegram_endpoint(self) -> str:
        """Get Telegram endpoint URL"""
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            return self._get_value("telegram_endpoint", "")
        else:
            telegram_config = self._load().get("telegram", {})
            return telegram_config.get("endpoint", "")
    
    @property
    def telegram_api_key(self) -> str:
        """Get Telegram API key"""
        if self.mode in [ConfigMode.FIREBASE, ConfigMode.FIXTURE]:
            return self._get_value("telegram_api_key", "")
        else:
            telegram_config = self._load().get("telegram", {})
            return telegram_config.get("api_key", "")
    
    @property
    def telegram_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        endpoint = self.telegram_endpoint
        api_key = self.telegram_api_key
        return bool(endpoint and api_key) 