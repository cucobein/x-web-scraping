"""Unit tests for NotificationService"""

from unittest.mock import PropertyMock, patch

from src.config.config_manager import ConfigManager, ConfigMode
from src.services.notification_service import NotificationService
from src.services.logger_service import LoggerService
from src.services.telegram_notification_service import TelegramNotificationService
from src.services.http_client_service import HttpClientService


class TestNotificationService:
    """Test notification service functionality"""

    def test_notification_service_initialization_with_telegram_enabled(self):
        """Test notification service initialization with Telegram enabled"""
        # Test with Telegram enabled (use local mode for unit tests)
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        config_with_telegram = ConfigManager(ConfigMode.LOCAL, logger=logger)
        http_client = HttpClientService(timeout=5)
        telegram_service = TelegramNotificationService(
            endpoint="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            api_key="47827973-e134-4ec1-9b11-458d3cc72962",
            http_client=http_client,
            logger=logger
        )
        service_with_telegram = NotificationService(
            config_manager=config_with_telegram,
            telegram_service=telegram_service,
            logger=logger
        )
        assert service_with_telegram.telegram_service is not None
        assert (
            service_with_telegram.telegram_service.endpoint
            == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
        )
        assert (
            service_with_telegram.telegram_service.api_key
            == "47827973-e134-4ec1-9b11-458d3cc72962"
        )

    def test_notification_service_initialization_with_telegram_disabled(self):
        """Test notification service initialization with Telegram disabled"""
        # Test with Telegram disabled
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        config_without_telegram = ConfigManager(ConfigMode.LOCAL, logger=logger)
        service_without_telegram = NotificationService(
            config_manager=config_without_telegram,
            telegram_service=None,
            logger=logger
        )
        assert service_without_telegram.telegram_service is None

    def test_notification_service_initialization_with_disabled_config(self):
        """Test notification service initialization when config has Telegram disabled"""
        # Create a config where Telegram is disabled
        with patch.object(
            ConfigManager, "telegram_enabled", new_callable=PropertyMock
        ) as mock_enabled:
            mock_enabled.return_value = False
            logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
            config_disabled = ConfigManager(ConfigMode.LOCAL, logger=logger)
            service_disabled = NotificationService(
                config_manager=config_disabled,
                telegram_service=None,
                logger=logger
            )
            assert service_disabled.telegram_service is None
