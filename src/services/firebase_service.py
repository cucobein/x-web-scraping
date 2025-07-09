"""
Firebase Service for remote configuration only
"""

import os
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import credentials, remote_config

from src.services.environment_service import EnvironmentService


class FirebaseService:
    """Firebase service for remote configuration only"""

    def __init__(self, env_service: Optional[EnvironmentService] = None):
        """
        Initialize Firebase service

        Args:
            env_service: Optional EnvironmentService for environment info
        """
        self.env_service = env_service
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        self._initialized = False
        self._remote_config_client = None

    def initialize(self) -> bool:
        """
        Initialize Firebase Admin SDK if not already done

        Returns:
            True if successful, False otherwise
        """
        if self._initialized:
            return True

        if not self.project_id or not self.service_account_path:
            return False

        try:
            # Apply nest_asyncio to handle event loop issues
            import nest_asyncio

            nest_asyncio.apply()

            # Initialize Firebase app if not already done
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.service_account_path)
                firebase_admin.initialize_app(cred, {"projectId": self.project_id})

            # Initialize remote config client
            self._remote_config_client = remote_config

            self._initialized = True
            return True

        except Exception:
            return False

    def is_initialized(self) -> bool:
        """Check if Firebase is initialized"""
        return self._initialized

    def _get_environment(self) -> str:
        """Get environment value with fallback"""
        if self.env_service:
            return self.env_service.get_environment()
        return EnvironmentService.get_default_environment()

    # ===== CONFIG METHODS =====

    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from Firebase Remote Config (synchronously).
        Returns:
            Configuration dictionary
        """
        if not self.is_initialized():
            raise Exception("Firebase not initialized")

        import asyncio

        async def _load_config_async():
            template = await self._remote_config_client.get_server_template()
            server_config = template.evaluate()
            # Extract all config values as a plain dict
            return {key: val.value for key, val in server_config._config_values.items()}

        try:
            # Apply nest_asyncio to handle event loop issues
            import nest_asyncio

            nest_asyncio.apply()

            # Create a new event loop if none exists
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run the async function
            return loop.run_until_complete(_load_config_async())

        except Exception as e:
            raise Exception(f"Failed to load config from Firebase: {str(e)}")

    def get_config_value(self, key: str, config: Dict[str, Any]) -> Any:
        """
        Get a configuration value for the current environment

        Args:
            key: Configuration key (without _dev/_prod suffix)
            config: Configuration dictionary

        Returns:
            Configuration value for current environment
        """
        env = self._get_environment()
        env_key = f"{key}_{env}"

        if env_key in config:
            return config[env_key]

        # Fallback to base key if environment-specific key not found
        if key in config:
            return config[key]

        raise KeyError(f"Configuration key '{key}' not found for environment '{env}'")

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get hardcoded fallback configuration"""
        # type: ignore[attr-defined]
        return {
            "monitoring_check_interval_dev": "30",
            "monitoring_check_interval_prod": "60",
            "monitoring_headless_dev": "true",
            "monitoring_headless_prod": "true",
            "monitoring_page_timeout_dev": "10000",
            "monitoring_page_timeout_prod": "10000",
            "telegram_endpoint_dev": "https://api-com-notifications-test.mobzilla.com/core/api/Telegram/SendMessage",
            "telegram_endpoint_prod": "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            "telegram_api_key_dev": "47827973-e134-4ec1-9b11-458d3cc72962",
            "telegram_api_key_prod": "47827973-e134-4ec1-9b11-458d3cc72962",
            "twitter_accounts_dev": '["olaphone", "cucobein", "FreddyTameJr", "CDMXConsejeria", "ContraloriaCDMX", "FiscaliaCDMX", "ClaraBrugadaM", "Finanzas_CDMX", "SEBIEN_cdmx", "CulturaCiudadMx", "SedecoCDMX", "Vivienda_CDMX", "SECTEI_CDMX", "sgirpc_cdmx", "GobCDMX", "semujerescdmx", "SEDEMA_CDMX", "LaSEMOVI", "SOBSECDMX", "metropoliscdmx", "sepicdmx", "SSaludCdMx", "SSC_CDMX", "TrabajoCDMX", "turismocdmx", "C5_CDMX", "MetrobusCDMX", "Bomberos_CDMX", "SEGIAGUA", "UCS_GCDMX", "LaAgenciaCDMX", "DGRCivilCDMX", "DiversidadCDMX", "locatel_mx", "SCPPyBG", "SAPCI_CDMX", "icat_cdmx", "CedaGeneral", "PDI_FGJCDMX", "CFilmaCDMX", "MetroCDMX", "STECDMX", "micablebuscdmx", "RTP_CiudadDeMex", "InjuveCDMX"]',
            "twitter_accounts_prod": '["olaphone", "cucobein", "FreddyTameJr", "CDMXConsejeria", "ContraloriaCDMX", "FiscaliaCDMX", "ClaraBrugadaM", "Finanzas_CDMX", "SEBIEN_cdmx", "CulturaCiudadMx", "SedecoCDMX", "Vivienda_CDMX", "SECTEI_CDMX", "sgirpc_cdmx", "GobCDMX", "semujerescdmx", "SEDEMA_CDMX", "LaSEMOVI", "SOBSECDMX", "metropoliscdmx", "sepicdmx", "SSaludCdMx", "SSC_CDMX", "TrabajoCDMX", "turismocdmx", "C5_CDMX", "MetrobusCDMX", "Bomberos_CDMX", "SEGIAGUA", "UCS_GCDMX", "LaAgenciaCDMX", "DGRCivilCDMX", "DiversidadCDMX", "locatel_mx", "SCPPyBG", "SAPCI_CDMX", "icat_cdmx", "CedaGeneral", "PDI_FGJCDMX", "CFilmaCDMX", "MetroCDMX", "STECDMX", "micablebuscdmx", "RTP_CiudadDeMex", "InjuveCDMX"]',
        }
