"""
Notification service for alerts
"""
from typing import Optional
from src.models.tweet import Tweet
from src.services.telegram_notification_service import TelegramNotificationService
from src.config.config_manager import ConfigManager


class NotificationService:
    """Handles notifications and alerts"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        Initialize notification service
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.telegram_service = None
        
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
        print(f"🔔 NEW POST: @{tweet.username}")
        print(f"   Time: {tweet.timestamp}")
        print(f"   Content: {tweet.content[:200]}...")
        if tweet.url:
            print(f"   URL: {tweet.url}")
        print("-" * 50)
        
        # Telegram notification (if configured)
        if self.telegram_service:
            try:
                response = await self.telegram_service.send_tweet_notification(tweet)
                if response.success:
                    print(f"✅ Telegram notification sent successfully")
                else:
                    print(f"⚠️ Telegram notification failed: {response.error}")
            except Exception as e:
                print(f"❌ Telegram notification error: {e}")
    
    async def notify_error(self, username: str, error: str):
        """
        Notify about an error
        
        Args:
            username: Username that caused the error
            error: Error message
        """
        print(f"⚠️ Error with @{username}: {error}")
    
    async def notify_status(self, message: str):
        """
        Notify about status updates
        
        Args:
            message: Status message
        """
        print(message) 