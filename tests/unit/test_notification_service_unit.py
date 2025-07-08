"""Unit tests for NotificationService"""

from unittest.mock import PropertyMock, patch

from src.config.config_manager import ConfigManager, ConfigMode
from src.services.notification_service import NotificationService
from src.services.logger_service import LoggerService
from src.services.telegram_notification_service import TelegramNotificationService


class TestNotificationService:
    """Test notification service functionality"""

    def test_notification_service_initialization_with_telegram_enabled(self):
        """Test notification service initialization with Telegram enabled"""
        # Test with Telegram enabled (use local mode for unit tests)
        config_with_telegram = ConfigManager(ConfigMode.LOCAL)
        logger = LoggerService(firebase_disabled=True)
        telegram_service = TelegramNotificationService(
            endpoint="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            api_key="47827973-e134-4ec1-9b11-458d3cc72962",
            logger=logger
        )
        service_with_telegram = NotificationService(
            config_manager=config_with_telegram,
            logger=logger,
            telegram_service=telegram_service
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
        config_without_telegram = ConfigManager(ConfigMode.LOCAL)
        logger = LoggerService(firebase_disabled=True)
        service_without_telegram = NotificationService(
            config_manager=config_without_telegram,
            logger=logger,
            telegram_service=None
        )
        assert service_without_telegram.telegram_service is None

    def test_notification_service_initialization_with_disabled_config(self):
        """Test notification service initialization when config has Telegram disabled"""
        # Create a config where Telegram is disabled
        with patch.object(
            ConfigManager, "telegram_enabled", new_callable=PropertyMock
        ) as mock_enabled:
            mock_enabled.return_value = False
            config_disabled = ConfigManager(ConfigMode.LOCAL)
            logger = LoggerService(firebase_disabled=True)
            service_disabled = NotificationService(
                config_manager=config_disabled,
                logger=logger,
                telegram_service=None
            )
            assert service_disabled.telegram_service is None
