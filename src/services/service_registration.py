"""
Service Registration Module

This module handles registering all services with the ServiceProvider singleton.
It should be imported early in the application lifecycle to set up dependencies.
"""

from src.config.config_manager import ConfigManager, ConfigMode
from src.services import get_service_provider
from src.services.logger_service import LoggerService
from src.services.firebase_log_service import FirebaseLogService
from src.services.rate_limiter import RateLimiter
from src.services.browser_manager import BrowserManager
from src.repositories.tweet_repository import TweetRepository
from src.services.notification_service import NotificationService
from src.services.telegram_notification_service import TelegramNotificationService
from src.services.http_client import HttpClient
from src.services.twitter_scraper import TwitterScraper
from src.utils.env_helper import get_environment


def register_core_services(config_mode: ConfigMode = ConfigMode.FIREBASE):
    """Register core services with the ServiceProvider"""
    provider = get_service_provider()
    
    # Register LoggerService as singleton
    provider.register_singleton(LoggerService, lambda: LoggerService.get_instance())
    
    # Register FirebaseLogService as singleton
    provider.register_singleton(FirebaseLogService, lambda: FirebaseLogService())
    
    # Register ConfigManager as singleton
    provider.register_singleton(ConfigManager, lambda: ConfigManager(
        mode=config_mode,
        environment=get_environment(),
        logger=provider.get(LoggerService)
    ))
    
    # Register RateLimiter as singleton
    provider.register_singleton(RateLimiter, lambda: RateLimiter())

    # Register BrowserManager as singleton
    provider.register_singleton(BrowserManager, lambda: BrowserManager(
        headless=provider.get(ConfigManager).headless,
        rate_limiter=provider.get(RateLimiter),
        logger=provider.get(LoggerService)
    ))
    
    # Register TweetRepository as singleton
    provider.register_singleton(TweetRepository, lambda: TweetRepository())
    
    # Register NotificationService as singleton
    provider.register_singleton(NotificationService, lambda: NotificationService(
        config_manager=provider.get(ConfigManager),
        logger=provider.get(LoggerService)
    ))
    
    # Register TelegramNotificationService as transient
    provider.register_singleton(TelegramNotificationService, lambda: TelegramNotificationService(
        endpoint=provider.get(ConfigManager).telegram_endpoint,
        api_key=provider.get(ConfigManager).telegram_api_key,
        logger=provider.get(LoggerService)
    ))

    # Register HttpClient as transient (factory returns new instance)
    provider.register_singleton(HttpClient, lambda: HttpClient(
        timeout=provider.get(ConfigManager).page_timeout
    ))

    # Register TwitterScraper as transient (factory returns new instance)
    provider.register_singleton(TwitterScraper, lambda: TwitterScraper(
        page_timeout=provider.get(ConfigManager).page_timeout,
        logger=provider.get(LoggerService)
    ))


def register_all_services(config_mode: ConfigMode = ConfigMode.FIREBASE):
    """Register all services with the ServiceProvider"""
    register_core_services(config_mode)
    # TODO: Add other service registrations in phases 