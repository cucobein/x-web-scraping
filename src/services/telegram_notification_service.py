"""
Telegram notification service for sending tweet alerts
"""
from typing import Optional
from src.services.http_client import HttpClient
from src.models.telegram_message import TelegramMessageRequest, TelegramMessageResponse
from src.models.tweet import Tweet


class TelegramNotificationService:
    """Handles sending notifications to Telegram endpoint"""
    
    def __init__(self, endpoint: str, api_key: str):
        """
        Initialize Telegram notification service
        
        Args:
            endpoint: Telegram endpoint URL
            api_key: API key for authentication
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.http_client = HttpClient()
    
    async def send_tweet_notification(self, tweet: Tweet) -> TelegramMessageResponse:
        """
        Send a tweet notification to Telegram
        
        Args:
            tweet: Tweet object to send
            
        Returns:
            TelegramMessageResponse with result
            
        Raises:
            ValueError: If tweet has no URL
        """
        # Validate that tweet has a URL
        if not tweet.url:
            raise ValueError("Cannot send notification for tweet without URL")
            
        try:
            # Create message request
            message_text = self._format_tweet_message(tweet)
            request = TelegramMessageRequest(
                message=message_text,
                url=tweet.url
            )
            
            # Prepare headers with API key
            headers = {
                "x-api-key": self.api_key
            }
            
            # Send request
            status_code, response_data = await self.http_client.post_form_data(
                url=self.endpoint,
                data=request.to_form_data(),
                headers=headers
            )
            
            # Create response object
            return TelegramMessageResponse.from_response(status_code, response_data)
            
        except Exception as e:
            # Handle network/connection errors
            return TelegramMessageResponse.from_error(0, str(e))
    
    def _format_tweet_message(self, tweet: Tweet) -> str:
        """
        Format tweet content for Telegram message
        
        Args:
            tweet: Tweet object
            
        Returns:
            Formatted message string
        """
        # Truncate content if too long (Telegram has limits)
        content = tweet.content[:500] + "..." if len(tweet.content) > 500 else tweet.content
        
        # Format message
        message = f"🔔 New Tweet from @{tweet.username}\n\n"
        message += f"{content}\n\n"
        message += f"📅 {tweet.timestamp}"
        
        return message
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close() 