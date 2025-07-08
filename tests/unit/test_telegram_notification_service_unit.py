"""Unit tests for TelegramNotificationService"""

from unittest.mock import AsyncMock, patch

import pytest

from src.models.tweet import Tweet
from src.services.http_client_service import HttpClientService
from src.services.logger_service import LoggerService
from src.services.telegram_notification_service import TelegramNotificationService


class TestTelegramNotificationService:
    """Test Telegram notification functionality"""

    @pytest.fixture
    def telegram_service(self):
        """Create Telegram service instance"""
        logger = LoggerService()
        http_client = HttpClientService(timeout=5)
        return TelegramNotificationService(
            endpoint="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            api_key="test-api-key",
            http_client=http_client,
            logger=logger,
        )

    @pytest.fixture
    def sample_tweet(self):
        """Create sample tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789",
        )

    def test_service_initialization(self, telegram_service):
        """Test service initialization"""
        assert (
            telegram_service.endpoint
            == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
        )
        assert telegram_service.api_key == "test-api-key"
        assert telegram_service.http_client is not None

    @pytest.mark.asyncio
    async def test_send_tweet_notification_success(
        self, telegram_service, sample_tweet
    ):
        """Test successful tweet notification"""
        # Mock successful HTTP response
        mock_response = (200, {"success": True, "message": "Notification sent"})

        with patch.object(
            telegram_service.http_client,
            "post_form_data",
            new=AsyncMock(return_value=mock_response),
        ):
            result = await telegram_service.send_tweet_notification(sample_tweet)

        assert result.success is True
        assert result.status_code == 200
        assert "success" in result.raw_data

    @pytest.mark.asyncio
    async def test_send_tweet_notification_retry_success(
        self, telegram_service, sample_tweet
    ):
        """Test retry logic with eventual success"""
        # Mock HTTP client to fail twice, then succeed
        mock_post = AsyncMock()
        mock_post.side_effect = [
            (500, {"error": "Internal Server Error"}),  # First attempt fails
            (503, {"error": "Service Unavailable"}),  # Second attempt fails
            (
                200,
                {"success": True, "message": "Notification sent"},
            ),  # Third attempt succeeds
        ]

        with patch.object(
            telegram_service.http_client, "post_form_data", new=mock_post
        ):
            result = await telegram_service.send_tweet_notification(sample_tweet)

        assert result.success is True
        assert result.status_code == 200
        assert mock_post.call_count == 3

    @pytest.mark.asyncio
    async def test_send_tweet_notification_retry_exhausted(
        self, telegram_service, sample_tweet
    ):
        """Test retry logic with all attempts failing"""
        # Mock HTTP client to fail all 3 attempts
        mock_post = AsyncMock()
        mock_post.side_effect = [
            (500, {"error": "Internal Server Error"}),  # First attempt fails
            (503, {"error": "Service Unavailable"}),  # Second attempt fails
            (401, {"error": "Unauthorized"}),  # Third attempt fails
        ]

        with patch.object(
            telegram_service.http_client, "post_form_data", new=mock_post
        ):
            result = await telegram_service.send_tweet_notification(sample_tweet)

        assert result.success is False
        assert result.status_code == 0  # Error status code
        assert "HTTP 401" in (result.error or "")  # Should contain the final error
        assert mock_post.call_count == 3

    @pytest.mark.asyncio
    async def test_send_tweet_notification_no_url(self, telegram_service):
        """Test notification with tweet that has no URL"""
        tweet_without_url = Tweet(
            username="nasa",
            content="🚀 Exciting news from space!",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url=None,
        )

        with pytest.raises(
            ValueError, match="Cannot send notification for tweet without URL"
        ):
            await telegram_service.send_tweet_notification(tweet_without_url)

    def test_format_tweet_message(self, telegram_service, sample_tweet):
        """Test tweet message formatting"""
        message = telegram_service._format_tweet_message(sample_tweet)

        assert "🔔 New Tweet from @nasa" in message
        assert "🚀 Exciting news from space!" in message
        assert "📅 2025-06-30T16:35:50.5680193-07:00" in message

    def test_format_tweet_message_long_content(self, telegram_service):
        """Test message formatting with long content (truncation)"""
        long_tweet = Tweet(
            username="nasa",
            content="🚀 " + "A" * 600,  # Very long content
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789",
        )

        message = telegram_service._format_tweet_message(long_tweet)

        # Should be truncated
        assert len(message) < 1000
        assert "..." in message
        assert "🔔 New Tweet from @nasa" in message

    @pytest.mark.asyncio
    async def test_send_telegram_request_success(self, telegram_service):
        """Test _send_telegram_request method with success"""
        from src.models.telegram_message import TelegramMessageRequest

        request = TelegramMessageRequest(
            message="Test message", url="https://x.com/test/status/123"
        )
        headers = {"x-api-key": "test-key"}

        mock_response = (200, {"success": True})

        with patch.object(
            telegram_service.http_client,
            "post_form_data",
            new=AsyncMock(return_value=mock_response),
        ):
            status_code, response_data = await telegram_service._send_telegram_request(
                request, headers
            )

        assert status_code == 200
        assert response_data == {"success": True}

    @pytest.mark.asyncio
    async def test_send_telegram_request_http_error(self, telegram_service):
        """Test _send_telegram_request method with HTTP error"""
        from src.models.telegram_message import TelegramMessageRequest

        request = TelegramMessageRequest(
            message="Test message", url="https://x.com/test/status/123"
        )
        headers = {"x-api-key": "test-key"}

        mock_response = (500, {"error": "Internal Server Error"})

        with patch.object(
            telegram_service.http_client,
            "post_form_data",
            new=AsyncMock(return_value=mock_response),
        ):
            with pytest.raises(Exception) as exc_info:
                await telegram_service._send_telegram_request(request, headers)
            # Check that the error message contains the HTTP error
            assert "HTTP 500" in str(exc_info.value)
