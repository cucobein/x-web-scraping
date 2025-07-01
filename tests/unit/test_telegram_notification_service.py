"""
Unit tests for Telegram notification service
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from src.services.telegram_notification_service import TelegramNotificationService
from src.models.tweet import Tweet


class TestTelegramNotificationService:
    """Test Telegram notification service functionality"""
    
    @pytest.fixture
    def telegram_service(self):
        """Create Telegram notification service instance"""
        return TelegramNotificationService(
            endpoint="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
            api_key="test-api-key"
        )
    
    @pytest.fixture
    def sample_tweet(self):
        """Create sample tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet that could potentially support life. This discovery opens up new possibilities for understanding our universe and the potential for life beyond Earth.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789"
        )
    
    @pytest.fixture
    def success_response_data(self):
        """Load success response fixture"""
        with open("tests/fixtures/telegram/success_response.json", "r") as f:
            return json.load(f)
    
    @pytest.fixture
    def error_response_data(self):
        """Load error response fixture"""
        with open("tests/fixtures/telegram/error_response.json", "r") as f:
            return json.load(f)
    
    def test_format_tweet_message(self, telegram_service, sample_tweet):
        """Test tweet message formatting"""
        message = telegram_service._format_tweet_message(sample_tweet)
        
        # Check formatting
        assert "🔔 New Tweet from @nasa" in message
        assert "🚀 Exciting news from space!" in message
        assert "📅 2025-06-30T16:35:50.5680193-07:00" in message
        assert message.count("\n") >= 4  # Should have proper line breaks
    
    def test_format_tweet_message_truncation(self, telegram_service):
        """Test message truncation for long tweets"""
        long_content = "A" * 600  # Very long content
        long_tweet = Tweet(
            username="test",
            content=long_content,
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/test/status/123"
        )
        
        message = telegram_service._format_tweet_message(long_tweet)
        
        # Should be truncated
        assert len(message) < len(long_content) + 100  # Account for formatting
        assert "..." in message
    
    @pytest.mark.asyncio
    async def test_send_tweet_notification_no_url_raises_error(self, telegram_service):
        """Test that sending notification for tweet without URL raises error"""
        tweet_no_url = Tweet(
            username="test",
            content="Test tweet without URL",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url=None
        )
        
        with pytest.raises(ValueError, match="Cannot send notification for tweet without URL"):
            await telegram_service.send_tweet_notification(tweet_no_url)
    
    @pytest.mark.asyncio
    async def test_send_tweet_notification_success(self, telegram_service, sample_tweet, success_response_data):
        """Test successful tweet notification"""
        with patch.object(telegram_service.http_client, 'post_form_data') as mock_post:
            mock_post.return_value = (200, success_response_data)
            
            response = await telegram_service.send_tweet_notification(sample_tweet)
            
            # Check response
            assert response.success is True
            assert response.status_code == 200
            assert response.data == "Mensaje Enviado"
            assert response.message == "Ok"
            
            # Check that HTTP client was called correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            # Check URL
            assert call_args[1]['url'] == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
            
            # Check headers
            assert call_args[1]['headers']['x-api-key'] == "test-api-key"
            
            # Check form data
            form_data = call_args[1]['data']
            assert form_data['Message'].startswith("🔔 New Tweet from @nasa")
            assert form_data['Url'] == "https://x.com/nasa/status/123456789"
    
    @pytest.mark.asyncio
    async def test_send_tweet_notification_error(self, telegram_service, sample_tweet, error_response_data):
        """Test tweet notification with error response"""
        with patch.object(telegram_service.http_client, 'post_form_data') as mock_post:
            mock_post.return_value = (401, error_response_data)
            
            response = await telegram_service.send_tweet_notification(sample_tweet)
            
            # Check response
            assert response.success is False
            assert response.status_code == 401
            assert response.error == "The apikey don't correct"
            assert response.message == "Not Authorized"
    
    @pytest.mark.asyncio
    async def test_send_tweet_notification_network_error(self, telegram_service, sample_tweet):
        """Test tweet notification with network error"""
        with patch.object(telegram_service.http_client, 'post_form_data') as mock_post:
            mock_post.side_effect = Exception("Network connection failed")
            
            response = await telegram_service.send_tweet_notification(sample_tweet)
            
            # Check response
            assert response.success is False
            assert response.status_code == 0
            assert response.error == "Network connection failed"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, telegram_service):
        """Test Telegram service as context manager"""
        with patch.object(telegram_service.http_client, 'close') as mock_close:
            async with telegram_service as service:
                assert service == telegram_service
            
            # Should close HTTP client
            mock_close.assert_called_once() 