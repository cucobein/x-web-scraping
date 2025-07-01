"""
Integration tests for full monitoring workflow - Real World Scenarios
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, PropertyMock
from src.core.monitor import XMonitor
from src.models.tweet import Tweet


class TestMonitorIntegration:
    """Test real-world scenarios for full monitoring workflow integration"""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance with test config"""
        return XMonitor("config/config.json")
    
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
    def baseline_tweet(self):
        """Create baseline tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Baseline tweet from NASA",
            timestamp="2025-06-30T10:00:00.0000000-07:00",
            url="https://x.com/nasa/status/111111111"
        )
    
    @pytest.fixture
    def new_tweet(self):
        """Create new tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789"
        )
    
    @pytest.mark.asyncio
    async def test_first_time_monitoring_no_notification(self, monitor, new_tweet):
        """Scenario: First time monitoring an account - should establish baseline without notification"""
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet', new=AsyncMock(return_value=new_tweet)):
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data') as mock_post:
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_context.return_value = mock_context_instance
                    
                    # First time monitoring - should establish baseline
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed
                    assert result is True
                    # Should NOT send Telegram notification (first check)
                    mock_post.assert_not_called()
                    # Should save baseline tweet
                    assert monitor.tweet_repository.get_last_tweet_id("nasa") == new_tweet.unique_id
    
    @pytest.mark.asyncio
    async def test_new_tweet_detected_with_notification(self, monitor, baseline_tweet, new_tweet, success_response_data):
        """Scenario: New tweet detected - should send Telegram notification"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)
        
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet', new=AsyncMock(return_value=new_tweet)):
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data', new=AsyncMock(return_value=(200, success_response_data))) as mock_post:
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_context.return_value = mock_context_instance
                    
                    # New tweet detected - should send notification
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed
                    assert result is True
                    # Should send Telegram notification
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args
                    
                    # Verify notification content
                    form_data = call_args[1]['data']
                    assert form_data['Message'].startswith("🔔 New Tweet from @nasa")
                    assert form_data['Url'] == "https://x.com/nasa/status/123456789"
                    
                    # Verify API authentication
                    headers = call_args[1]['headers']
                    assert headers['x-api-key'] == "47827973-e134-4ec1-9b11-458d3cc72962"
                    
                    # Should update to new tweet
                    assert monitor.tweet_repository.get_last_tweet_id("nasa") == new_tweet.unique_id
    
    @pytest.mark.asyncio
    async def test_no_new_tweets(self, monitor, baseline_tweet):
        """Scenario: No new tweets - should report no new posts"""
        # Setup: Account has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)
        
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet', new=AsyncMock(return_value=baseline_tweet)):
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data') as mock_post:
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_context.return_value = mock_context_instance
                    
                    # Same tweet - no new posts
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed
                    assert result is True
                    # Should NOT send Telegram notification
                    mock_post.assert_not_called()
                    # Should keep same baseline
                    assert monitor.tweet_repository.get_last_tweet_id("nasa") == baseline_tweet.unique_id
    
    @pytest.mark.asyncio
    async def test_telegram_api_failure_continues_monitoring(self, monitor, baseline_tweet, new_tweet, error_response_data):
        """Scenario: Telegram API fails - system should continue monitoring"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)
        
        with patch.object(monitor.twitter_scraper, 'get_latest_tweet', new=AsyncMock(return_value=new_tweet)):
            with patch.object(monitor.notification_service.telegram_service.http_client, 'post_form_data', new=AsyncMock(return_value=(401, error_response_data))) as mock_post:
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_context.return_value = mock_context_instance
                    
                    # Telegram API fails but monitoring continues
                    result = await monitor.process_account("nasa")
                    
                    # Should still succeed (Telegram failure doesn't break monitoring)
                    assert result is True
                    # Should attempt Telegram notification
                    mock_post.assert_called_once()
                    # Should still update to new tweet
                    assert monitor.tweet_repository.get_last_tweet_id("nasa") == new_tweet.unique_id
    
    @pytest.mark.asyncio
    async def test_telegram_disabled_in_config(self, monitor, baseline_tweet, new_tweet):
        """Scenario: Telegram disabled in config - should work without notifications"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)
        
        # Disable Telegram in config
        with patch.object(type(monitor.config_manager), 'telegram_enabled', new_callable=PropertyMock) as mock_enabled:
            mock_enabled.return_value = False
            monitor.notification_service = monitor.notification_service.__class__(monitor.config_manager)
            
            with patch.object(monitor.twitter_scraper, 'get_latest_tweet', new=AsyncMock(return_value=new_tweet)):
                with patch.object(monitor.browser_manager, 'get_context') as mock_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_context.return_value = mock_context_instance
                    
                    # New tweet but Telegram disabled
                    result = await monitor.process_account("nasa")
                    
                    # Should succeed without Telegram
                    assert result is True
                    # Telegram service should be None
                    assert monitor.notification_service.telegram_service is None
                    # Should still update to new tweet
                    assert monitor.tweet_repository.get_last_tweet_id("nasa") == new_tweet.unique_id
    
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