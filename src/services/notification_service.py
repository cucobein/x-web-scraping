"""
Notification service for alerts
"""
from src.models.tweet import Tweet


class NotificationService:
    """Handles notifications and alerts"""
    
    def __init__(self):
        pass
    
    async def notify_new_tweet(self, tweet: Tweet):
        """
        Notify about a new tweet
        
        Args:
            tweet: The new tweet to notify about
        """
        print(f"🔔 NEW POST: @{tweet.username}")
        print(f"   Time: {tweet.timestamp}")
        print(f"   Content: {tweet.content[:200]}...")
        if tweet.url:
            print(f"   URL: {tweet.url}")
        print("-" * 50)
    
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