"""
Telegram notification service for sending tweet alerts
"""

from typing import Optional

from src.models.telegram_message import TelegramMessageRequest, TelegramMessageResponse
from src.models.tweet import Tweet
from src.services.http_client_service import HttpClientService
from src.services.logger_service import LoggerService


class TelegramNotificationService:
    """Handles sending notifications to Telegram endpoint"""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        http_client: HttpClientService,
        logger: Optional[LoggerService] = None,
    ):
        """
        Initialize Telegram notification service

        Args:
            endpoint: Telegram endpoint URL
            api_key: API key for authentication
            http_client: HTTP client service (required)
            logger: Logger service (optional, uses default if not provided)
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.http_client = http_client
        self.logger = logger

    async def _send_telegram_request(
        self, request: TelegramMessageRequest, headers: dict
    ) -> tuple[int, dict]:
        """
        Send request to Telegram API with retry logic

        Args:
            request: Telegram message request
            headers: Request headers

        Returns:
            Tuple of (status_code, response_data)

        Raises:
            Exception: If all retry attempts fail
        """
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                status_code, response_data = await self.http_client.post_form_data(
                    url=self.endpoint, data=request.to_form_data(), headers=headers
                )

                # Consider 4xx and 5xx status codes as failures for retry
                if status_code >= 400:
                    raise Exception(f"HTTP {status_code}: {response_data}")

                return status_code, response_data

            except Exception as e:
                if attempt < max_attempts:
                    # Calculate exponential backoff delay
                    delay = min(2 ** (attempt - 1), 10)  # Max 10 seconds
                    if self.logger:
                        self.logger.warning(
                            f"Telegram API call failed (attempt {attempt}/{max_attempts})",
                            {
                                "error": str(e),
                                "retry_delay": delay,
                                "endpoint": self.endpoint,
                            },
                        )
                    import asyncio

                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed, re-raise the exception
                    raise
        return 500, {"error": "All retries failed"}

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
            request = TelegramMessageRequest(message=message_text, url=tweet.url)

            # Prepare headers with API key
            headers = {"x-api-key": self.api_key}

            # Send request with retry logic
            status_code, response_data = await self._send_telegram_request(
                request, headers
            )

            # Create response object
            return TelegramMessageResponse.from_response(status_code, response_data)

        except Exception as e:
            # Handle network/connection errors (after all retries exhausted)
            if self.logger:
                self.logger.error(
                    "All retry attempts failed for tweet notification",
                    {
                        "error": str(e),
                        "tweet_username": tweet.username,
                        "tweet_url": tweet.url,
                    },
                )
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
        content = (
            tweet.content[:500] + "..." if len(tweet.content) > 500 else tweet.content
        )

        # Format message
        message = f"🔔 New Tweet from @{tweet.username}\n\n"
        message += f"{content}\n\n"
        message += f"📅 {tweet.timestamp}"

        return message

    async def close(self) -> None:
        """Close the HTTP client"""
        await self.http_client.close()

    async def __aenter__(self) -> "TelegramNotificationService":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit"""
        await self.close()
