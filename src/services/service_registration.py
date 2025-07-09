"""
Service Registration - Composition Root

This module serves as the composition root for the application.
All service registration happens here, following the ASP.NET Core pattern.
"""

from src.config.config_manager import ConfigManager, ConfigMode
from src.repositories.tweet_repository import TweetRepository
from src.services import get_service_provider
from src.services.browser_manager import BrowserManager
from src.services.environment_service import EnvironmentService
from src.services.firebase_service import FirebaseService
from src.services.http_client_service import HttpClientService
from src.services.logger_service import LoggerService
from src.services.notification_service import NotificationService
from src.services.rate_limiter_service import RateLimiterService
from src.services.telegram_notification_service import TelegramNotificationService
from src.services.twitter_scraper import TwitterScraper


def setup_services() -> None:
    """
    Setup all services - Composition Root

    This is the single place where all service registration happens.
    Following ASP.NET Core pattern where Program.cs registers all services.
    """
    provider = get_service_provider()

    # Core services
    provider.register_singleton(EnvironmentService, lambda: EnvironmentService())

    # Create FirebaseService first (centralized Firebase management)
    provider.register_singleton(
        FirebaseService,
        lambda: FirebaseService(env_service=provider.get(EnvironmentService)),
    )

    # Create LoggerService
    provider.register_singleton(
        LoggerService,
        lambda: LoggerService(
            log_file_path="logs/app.log",
            environment_service=provider.get(EnvironmentService),
        ),
    )

    provider.register_singleton(
        ConfigManager,
        lambda: ConfigManager(
            mode=ConfigMode.FIREBASE,
            logger=provider.get(LoggerService),
            env_service=provider.get(EnvironmentService),
            firebase_service=provider.get(FirebaseService),
        ),
    )

    provider.register_singleton(RateLimiterService, lambda: RateLimiterService())

    # Business services
    provider.register_singleton(
        BrowserManager,
        lambda: BrowserManager(
            rate_limiter=provider.get(RateLimiterService),
            logger=provider.get(LoggerService),
            headless=True,
        ),
    )

    provider.register_singleton(TweetRepository, lambda: TweetRepository())

    # Register HttpClientService first since TelegramNotificationService needs it
    provider.register_singleton(
        HttpClientService,
        lambda: HttpClientService(timeout=provider.get(ConfigManager).page_timeout),
    )

    # Transient services (factories return new instances)
    provider.register_singleton(
        TelegramNotificationService,
        lambda: TelegramNotificationService(
            endpoint=provider.get(ConfigManager).telegram_endpoint,
            api_key=provider.get(ConfigManager).telegram_api_key,
            http_client=provider.get(HttpClientService),
            logger=provider.get(LoggerService),
        ),
    )

    # Get Telegram service conditionally
    telegram_service = None
    config_manager = provider.get(ConfigManager)
    if config_manager.telegram_enabled:
        telegram_service = provider.get(TelegramNotificationService)

    provider.register_singleton(
        NotificationService,
        lambda: NotificationService(
            config_manager=config_manager,
            telegram_service=telegram_service,
            logger=provider.get(LoggerService),
        ),
    )

    provider.register_singleton(
        TwitterScraper,
        lambda: TwitterScraper(
            page_timeout=provider.get(ConfigManager).page_timeout,
            logger=provider.get(LoggerService),
        ),
    )

    return provider
