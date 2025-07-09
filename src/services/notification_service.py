"""
Notification service for alerts
"""

from typing import Optional

from src.config.config_manager import ConfigManager
from src.models.tweet import Tweet
from src.services.logger_service import LoggerService
from src.services.telegram_notification_service import TelegramNotificationService


class NotificationService:
    """Handles notifications and alerts"""

    def __init__(
        self,
        config_manager: ConfigManager,
        telegram_service: Optional[TelegramNotificationService] = None,
        logger: Optional[LoggerService] = None,
    ) -> None:
        """
        Initialize notification service

        Args:
            config_manager: Configuration manager instance (required)
            telegram_service: Optional Telegram notification service
            logger: Logger service (optional, uses default if not provided)
        """
        self.config_manager = config_manager
        self.logger = logger
        self.telegram_service = telegram_service

    async def notify_new_tweet(self, tweet: Tweet) -> None:
        """
        Notify about a new tweet

        Args:
            tweet: The new tweet to notify about
        """
        # Console notification (always show)
        if self.logger:
            self.logger.info(
                f"NEW POST: @{tweet.username}",
                {
                    "time": tweet.timestamp,
                    "content": tweet.content[:200],
                    "url": tweet.url,
                },
            )

        # Telegram notification (if configured)
        if self.telegram_service:
            try:
                response = await self.telegram_service.send_tweet_notification(tweet)
                if response.success:
                    if self.logger:
                        self.logger.info("Telegram notification sent successfully")
                else:
                    if self.logger:
                        self.logger.warning(
                            "Telegram notification failed", {"error": response.error}
                        )
            except Exception as e:
                if self.logger:
                    self.logger.error("Telegram notification error", {"error": str(e)})

    async def notify_error(self, username: str, error: str) -> None:
        """
        Notify about an error

        Args:
            username: Username that caused the error
            error: Error message
        """
        if self.logger:
            self.logger.warning(f"Error with @{username}", {"error": error})

    async def notify_status(self, message: str) -> None:
        """
        Notify about status updates

        Args:
            message: Status message
        """
        if self.logger:
            self.logger.info(message)
