"""Unit tests for Monitor"""
import pytest
from unittest.mock import AsyncMock, patch, PropertyMock
from src.core.monitor import XMonitor
from src.models.tweet import Tweet


class TestMonitor:
    """Test monitor functionality"""
    
    @pytest.fixture
    def monitor(self):
        """Create monitor instance for testing"""
        return XMonitor("config/config.json")
    
    @pytest.fixture
    def baseline_tweet(self):
        """Create baseline tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789"
        )
    
    @pytest.fixture
    def new_tweet(self):
        """Create new tweet for testing"""
        return Tweet(
            username="nasa",
            content="🌌 Breaking: New images from the James Webb Space Telescope reveal unprecedented details of distant galaxies!",
            timestamp="2025-06-30T17:45:30.1234567-07:00",
            url="https://x.com/nasa/status/987654321"
        )
    
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