"""
Integration tests for Telegram notification flow
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from src.core.monitor import XMonitor
from src.models.tweet import Tweet


class TestTelegramIntegration:
    """Test full integration flow from tweet detection to Telegram notification"""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance with test config"""
        return XMonitor("tests/fixtures/test_config.json")
    
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
    
    @pytest.fixture
    def sample_tweet(self):
        """Create sample tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789"
        )
    
    @pytest.mark.asyncio
    async def test_full_flow_success(self, monitor, sample_tweet, success_response_data):
        """Test complete flow: tweet detection -> Telegram notification -> success"""
        # Mock the Twitter scraper to return our sample tweet
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet') as mock_get_tweet:
            mock_get_tweet.return_value = sample_tweet
            
            # Mock the HTTP client to return success
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data') as mock_post:
                mock_post.return_value = (200, success_response_data)
                
                # Mock browser context
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context.return_value.new_page.return_value = mock_page
                    
                    # Process the account
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed
                    assert result is True
                    
                    # Check that Telegram was called
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args
                    
                    # Verify the request format
                    form_data = call_args[1]['data']
                    assert form_data['Message'].startswith("🔔 New Tweet from @nasa")
                    assert form_data['Url'] == "https://x.com/nasa/status/123456789"
                    
                    # Verify headers
                    headers = call_args[1]['headers']
                    assert headers['x-api-key'] == "47827973-e134-4ec1-9b11-458d3cc72962"
    
    @pytest.mark.asyncio
    async def test_full_flow_telegram_error(self, monitor, sample_tweet, error_response_data):
        """Test complete flow: tweet detection -> Telegram notification -> error"""
        # Mock the Twitter scraper to return our sample tweet
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet') as mock_get_tweet:
            mock_get_tweet.return_value = sample_tweet
            
            # Mock the HTTP client to return error
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data') as mock_post:
                mock_post.return_value = (401, error_response_data)
                
                # Mock browser context
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context.return_value.new_page.return_value = mock_page
                    
                    # Process the account
                    result = await monitor.process_account("nasa")
                    
                    # Should still succeed (Telegram error doesn't fail the process)
                    assert result is True
                    
                    # Check that Telegram was called
                    mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_full_flow_telegram_disabled(self, monitor, sample_tweet):
        """Test flow when Telegram is disabled in config"""
        # Create monitor with disabled Telegram
        with patch.object(monitor.config_manager, 'telegram_enabled', False):
            # Recreate notification service without Telegram
            monitor.notification_service = monitor.notification_service.__class__(monitor.config_manager)
            
            # Mock the Twitter scraper to return our sample tweet
            with patch.object(monitor.twitter_scraper, 'get_latest_tweet') as mock_get_tweet:
                mock_get_tweet.return_value = sample_tweet
                
                # Mock browser context
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context.return_value.new_page.return_value = mock_page
                    
                    # Process the account
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed without Telegram
                    assert result is True
                    
                    # Telegram service should be None
                    assert monitor.notification_service.telegram_service is None
    
    @pytest.mark.asyncio
    async def test_full_flow_network_error(self, monitor, sample_tweet):
        """Test flow when network error occurs during Telegram notification"""
        # Mock the Twitter scraper to return our sample tweet
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet') as mock_get_tweet:
            mock_get_tweet.return_value = sample_tweet
            
            # Mock the HTTP client to raise network error
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data') as mock_post:
                mock_post.side_effect = Exception("Network connection failed")
                
                # Mock browser context
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context.return_value.new_page.return_value = mock_page
                    
                    # Process the account
                    result = await monitor.process_account("nasa")
                    
                    # Should still succeed (network error doesn't fail the process)
                    assert result is True
                    
                    # Check that Telegram was called
                    mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_notification_service_initialization(self):
        """Test notification service initialization with different configs"""
        from src.services.notification_service import NotificationService
        from src.config.config_manager import ConfigManager
        
        # Test with Telegram enabled
        config_with_telegram = ConfigManager("config/config.json")
        service_with_telegram = NotificationService(config_with_telegram)
        assert service_with_telegram.telegram_service is not None
        assert service_with_telegram.telegram_service.endpoint == "https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage"
        assert service_with_telegram.telegram_service.api_key == "47827973-e134-4ec1-9b11-458d3cc72962"
        
        # Test with Telegram disabled
        service_without_telegram = NotificationService(None)
        assert service_without_telegram.telegram_service is None 