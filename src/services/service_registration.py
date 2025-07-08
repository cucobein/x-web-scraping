"""
Service Registration - Composition Root

This module serves as the composition root for the application.
All service registration happens here, following the ASP.NET Core pattern.
"""

from src.config.config_manager import ConfigManager, ConfigMode
from src.services import get_service_provider
from src.services.environment_service import EnvironmentService
from src.services.logger_service import LoggerService
from src.services.firebase_log_service import FirebaseLogService
from src.services.rate_limiter_service import RateLimiterService
from src.services.browser_manager import BrowserManager
from src.repositories.tweet_repository import TweetRepository
from src.services.notification_service import NotificationService
from src.services.telegram_notification_service import TelegramNotificationService
from src.services.http_client import HttpClient
from src.services.twitter_scraper import TwitterScraper


def setup_services():
    """
    Setup all services - Composition Root
    
    This is the single place where all service registration happens.
    Following ASP.NET Core pattern where Program.cs registers all services.
    """
    provider = get_service_provider()
    
    # Core services
    provider.register_singleton(EnvironmentService, lambda: EnvironmentService())
    
    # Create LoggerService first without FirebaseLogService
    provider.register_singleton(LoggerService, lambda: LoggerService(
        log_file_path="logs/app.log"
    ))
    
    # Create FirebaseLogService with LoggerService
    provider.register_singleton(FirebaseLogService, lambda: FirebaseLogService(
        logger=provider.get(LoggerService),
        env_service=provider.get(EnvironmentService)
    ))
    
    # Update LoggerService to include FirebaseLogService
    logger_service = provider.get(LoggerService)
    firebase_logger = provider.get(FirebaseLogService)
    logger_service._firebase_logger = firebase_logger
    
    provider.register_singleton(ConfigManager, lambda: ConfigManager(
        mode=ConfigMode.FIREBASE,
        logger=provider.get(LoggerService),
        env_service=provider.get(EnvironmentService)
    ))
    
    provider.register_singleton(RateLimiterService, lambda: RateLimiterService())
    
    # Business services
    provider.register_singleton(BrowserManager, lambda: BrowserManager(
        rate_limiter=provider.get(RateLimiterService),
        logger=provider.get(LoggerService),
        headless=True
    ))
    
    provider.register_singleton(TweetRepository, lambda: TweetRepository())
    
    # Transient services (factories return new instances)
    provider.register_singleton(TelegramNotificationService, lambda: TelegramNotificationService(
        endpoint=provider.get(ConfigManager).telegram_endpoint,
        api_key=provider.get(ConfigManager).telegram_api_key,
        logger=provider.get(LoggerService)
    ))
    
    # Get Telegram service conditionally
    telegram_service = None
    config_manager = provider.get(ConfigManager)
    if config_manager.telegram_enabled:
        telegram_service = provider.get(TelegramNotificationService)
    
    provider.register_singleton(NotificationService, lambda: NotificationService(
        config_manager=config_manager,
        logger=provider.get(LoggerService),
        telegram_service=telegram_service
    ))
    
    provider.register_singleton(HttpClient, lambda: HttpClient(
        timeout=provider.get(ConfigManager).page_timeout
    ))
    
    provider.register_singleton(TwitterScraper, lambda: TwitterScraper(
        page_timeout=provider.get(ConfigManager).page_timeout,
        logger=provider.get(LoggerService)
    ))
    
    return provider


 