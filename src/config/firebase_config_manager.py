"""
Firebase Remote Config manager
"""
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, remote_config

from src.utils.env_helper import get_environment


class FirebaseConfigManager:
    """Manages configuration from Firebase Remote Config"""
    
    def __init__(self, project_id: str, service_account_path: str):
        """
        Initialize Firebase Config Manager
        
        Args:
            project_id: Firebase project ID
            service_account_path: Path to service account JSON file
        """
        self.project_id = project_id
        self.service_account_path = service_account_path
        self._config_cache: Optional[Dict[str, Any]] = None
        self._initialized = False
        
    async def _initialize_firebase(self):
        """Initialize Firebase Admin SDK if not already done"""
        if not self._initialized:
            try:
                cred = credentials.Certificate(self.service_account_path)
                firebase_admin.initialize_app(cred, {
                    'projectId': self.project_id
                })
                remote_config.init_server_template()
                self._initialized = True
                print("✅ Firebase initialized successfully")
            except Exception as e:
                print(f"❌ Firebase initialization failed: {e}")
                raise
    
    async def _load_config_from_firebase(self) -> Dict[str, Any]:
        """Load configuration from Firebase Remote Config"""
        await self._initialize_firebase()
        
        try:
            # Get the server template
            template = await remote_config.get_server_template()
            config_data = template.to_json()
            
            # Parse JSON data
            if isinstance(config_data, str):
                config_dict = json.loads(config_data)
            else:
                config_dict = config_data
            
            # Extract parameters
            parameters = config_dict.get('parameters', {})
            
            # Convert to simple key-value pairs
            config = {}
            for key, param in parameters.items():
                if 'defaultValue' in param and 'value' in param['defaultValue']:
                    config[key] = param['defaultValue']['value']
            
            return config
            
        except Exception as e:
            print(f"❌ Failed to load config from Firebase: {e}")
            raise
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get hardcoded fallback configuration"""
        return {
            "monitoring_check_interval_dev": "30",
            "monitoring_check_interval_prod": "60",
            "monitoring_headless_dev": "false",
            "monitoring_headless_prod": "true",
            "monitoring_page_timeout_dev": "5000",
            "monitoring_page_timeout_prod": "10000",
            "telegram_endpoint_dev": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            "telegram_endpoint_prod": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            "telegram_api_key_dev": "47827973-e134-4ec1-9b11-458d3cc72962",
            "telegram_api_key_prod": "47827973-e134-4ec1-9b11-458d3cc72962",
            "twitter_accounts_dev": '["nasa", "olaphone", "cucobein"]',
            "twitter_accounts_prod": '["olaphone", "cucobein", "FreddyTameJr", "CDMXConsejeria", "ContraloriaCDMX", "FiscaliaCDMX", "ClaraBrugadaM", "Finanzas_CDMX", "SEBIEN_cdmx", "CulturaCiudadMx", "SedecoCDMX", "Vivienda_CDMX", "SECTEI_CDMX", "sgirpc_cdmx", "GobCDMX", "semujerescdmx", "SEDEMA_CDMX", "LaSEMOVI", "SOBSECDMX", "metropoliscdmx", "sepicdmx", "SSaludCdMx", "SSC_CDMX", "TrabajoCDMX", "turismocdmx", "C5_CDMX", "MetrobusCDMX", "Bomberos_CDMX", "SEGIAGUA", "UCS_GCDMX", "LaAgenciaCDMX", "DGRCivilCDMX", "DiversidadCDMX", "locatel_mx", "SCPPyBG", "SAPCI_CDMX", "icat_cdmx", "CedaGeneral", "PDI_FGJCDMX", "CFilmaCDMX", "MetroCDMX", "STECDMX", "micablebuscdmx", "RTP_CiudadDeMex", "InjuveCDMX"]',
            "twitter_cookies_dev": '[{"name": "auth_token", "value": "47827973-e134-4ec1-9b11-458d3cc72962", "domain": ".x.com", "path": "/", "secure": true, "httpOnly": false, "sameSite": "Lax"}, {"name": "ct0", "value": "47827973-e134-4ec1-9b11-458d3cc72962", "domain": ".x.com", "path": "/", "secure": true, "httpOnly": false, "sameSite": "Lax"}]',
            "twitter_cookies_prod": '[{"name": "auth_token", "value": "47827973-e134-4ec1-9b11-458d3cc72962", "domain": ".x.com", "path": "/", "secure": true, "httpOnly": false, "sameSite": "Lax"}, {"name": "ct0", "value": "47827973-e134-4ec1-9b11-458d3cc72962", "domain": ".x.com", "path": "/", "secure": true, "httpOnly": false, "sameSite": "Lax"}]'
        }
    
    async def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from Firebase with fallback
        
        Returns:
            Configuration dictionary
        """
        try:
            config = await self._load_config_from_firebase()
            print("✅ Configuration loaded from Firebase")
            return config
        except Exception as e:
            print(f"⚠️ Firebase config failed, using fallback: {e}")
            config = self._get_fallback_config()
            print("✅ Using fallback configuration")
            return config
    
    def get_value(self, key: str, config: Dict[str, Any]) -> Any:
        """
        Get a configuration value for the current environment
        
        Args:
            key: Configuration key (without _dev/_prod suffix)
            config: Configuration dictionary
            
        Returns:
            Configuration value for current environment
        """
        env = get_environment()
        env_key = f"{key}_{env}"
        
        if env_key in config:
            return config[env_key]
        
        # Fallback to base key if environment-specific key not found
        if key in config:
            return config[key]
        
        raise KeyError(f"Configuration key '{key}' not found for environment '{env}'") 