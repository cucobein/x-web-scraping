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
from src.services.rate_limiter import RateLimiter
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
    
    provider.register_singleton(LoggerService, lambda: LoggerService(
        firebase_disabled=False,
        log_file_path="logs/app.log"
    ))
    
    provider.register_singleton(FirebaseLogService, lambda: FirebaseLogService(
        logger=provider.get(LoggerService),
        env_service=provider.get(EnvironmentService)
    ))
    
    provider.register_singleton(ConfigManager, lambda: ConfigManager(
        mode=ConfigMode.FIREBASE
    ))
    
    provider.register_singleton(RateLimiter, lambda: RateLimiter())
    
    # Business services
    provider.register_singleton(BrowserManager, lambda: BrowserManager(
        headless=True,
        rate_limiter=provider.get(RateLimiter),
        logger=provider.get(LoggerService)
    ))
    
    provider.register_singleton(TweetRepository, lambda: TweetRepository())
    
    provider.register_singleton(NotificationService, lambda: NotificationService(
        config_manager=provider.get(ConfigManager),
        logger=provider.get(LoggerService)
    ))
    
    # Transient services (factories return new instances)
    provider.register_singleton(TelegramNotificationService, lambda: TelegramNotificationService(
        endpoint=provider.get(ConfigManager).telegram_endpoint,
        api_key=provider.get(ConfigManager).telegram_api_key,
        logger=provider.get(LoggerService)
    ))
    
    provider.register_singleton(HttpClient, lambda: HttpClient(
        timeout=provider.get(ConfigManager).page_timeout
    ))
    
    provider.register_singleton(TwitterScraper, lambda: TwitterScraper(
        page_timeout=provider.get(ConfigManager).page_timeout,
        logger=provider.get(LoggerService)
    ))
    
    return provider


def setup_services_for_testing():
    """
    Setup services with test configuration
    
    Used for integration tests that need the provider.
    Unit tests should use direct instantiation instead.
    """
    provider = get_service_provider()
    
    # Core services with test config
    provider.register_singleton(EnvironmentService, lambda: EnvironmentService())
    
    provider.register_singleton(LoggerService, lambda: LoggerService(
        firebase_disabled=True,  # Disable Firebase in tests
        log_file_path="logs/test.log"
    ))
    
    provider.register_singleton(FirebaseLogService, lambda: FirebaseLogService(
        logger=provider.get(LoggerService),
        disabled=True,  # Disable Firebase in tests
        env_service=provider.get(EnvironmentService)
    ))
    
    provider.register_singleton(ConfigManager, lambda: ConfigManager(
        mode=ConfigMode.FIXTURE  # Use fixture mode for tests
    ))
    
    provider.register_singleton(RateLimiter, lambda: RateLimiter())
    
    # Business services with test config
    provider.register_singleton(BrowserManager, lambda: BrowserManager(
        headless=True,
        rate_limiter=provider.get(RateLimiter),
        logger=provider.get(LoggerService)
    ))
    
    provider.register_singleton(TweetRepository, lambda: TweetRepository())
    
    provider.register_singleton(NotificationService, lambda: NotificationService(
        config_manager=provider.get(ConfigManager),
        logger=provider.get(LoggerService)
    ))
    
    # Transient services for testing
    provider.register_singleton(TelegramNotificationService, lambda: TelegramNotificationService(
        endpoint=provider.get(ConfigManager).telegram_endpoint,
        api_key=provider.get(ConfigManager).telegram_api_key,
        logger=provider.get(LoggerService)
    ))
    
    provider.register_singleton(HttpClient, lambda: HttpClient(
        timeout=provider.get(ConfigManager).page_timeout
    ))
    
    provider.register_singleton(TwitterScraper, lambda: TwitterScraper(
        page_timeout=provider.get(ConfigManager).page_timeout,
        logger=provider.get(LoggerService)
    ))
    
    return provider 