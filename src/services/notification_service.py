"""
Notification service for alerts
"""
from typing import Optional
from src.models.tweet import Tweet
from src.services.telegram_notification_service import TelegramNotificationService
from src.config.config_manager import ConfigManager
from src.services.logger_service import LoggerService


class NotificationService:
    """Handles notifications and alerts"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, logger: Optional[LoggerService] = None):
        """
        Initialize notification service
        
        Args:
            config_manager: Configuration manager instance
            logger: Optional logger service
        """
        self.config_manager = config_manager
        self.telegram_service = None
        self.logger = logger or LoggerService()
        
        # Initialize Telegram service if configured
        if self.config_manager and self.config_manager.telegram_enabled:
            self.telegram_service = TelegramNotificationService(
                endpoint=self.config_manager.telegram_endpoint,
                api_key=self.config_manager.telegram_api_key
            )
    
    async def notify_new_tweet(self, tweet: Tweet):
        """
        Notify about a new tweet
        
        Args:
            tweet: The new tweet to notify about
        """
        # Console notification (always show)
        self.logger.info(f"NEW POST: @{tweet.username}", {
            "time": tweet.timestamp,
            "content": tweet.content[:200],
            "url": tweet.url
        })
        
        # Telegram notification (if configured)
        if self.telegram_service:
            try:
                response = await self.telegram_service.send_tweet_notification(tweet)
                if response.success:
                    self.logger.info("Telegram notification sent successfully")
                else:
                    self.logger.warning("Telegram notification failed", {"error": response.error})
            except Exception as e:
                self.logger.error("Telegram notification error", {"error": str(e)})
    
    async def notify_error(self, username: str, error: str):
        """
        Notify about an error
        
        Args:
            username: Username that caused the error
            error: Error message
        """
        self.logger.warning(f"Error with @{username}", {"error": error})
    
    async def notify_status(self, message: str):
        """
        Notify about status updates
        
        Args:
            message: Status message
        """
        self.logger.info(message) 