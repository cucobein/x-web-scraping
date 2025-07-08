"""
Unit tests for TwitterScraper
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.twitter_scraper import TwitterScraper
from src.services.logger_service import LoggerService


class TestTwitterScraper:
    """Test Twitter scraping functionality"""

    def test_scraper_initialization(self):
        """Test scraper initialization with custom timeout"""
        # Test default timeout
        scraper_default = TwitterScraper()
        assert scraper_default.page_timeout == 5000

        # Test custom timeout
        scraper_custom = TwitterScraper(page_timeout=10000)
        assert scraper_custom.page_timeout == 10000

    @pytest.mark.asyncio
    async def test_get_latest_tweet_timeout_error(self):
        """Test handling of timeout errors"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(page_timeout=5000, logger=logger)

        # Mock page with timeout error
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Timeout 5000ms exceeded")

        # Execute
        result = await scraper.get_latest_tweet(mock_page, "nasa")

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_get_latest_tweet_no_tweets_found(self):
        """Test when no tweets are found"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(page_timeout=5000, logger=logger)

        # Mock page with no tweets
        mock_page = AsyncMock()
        mock_tweets = AsyncMock()
        mock_tweets.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=mock_tweets)

        # Execute
        result = await scraper.get_latest_tweet(mock_page, "nasa")

        # Verify
        assert result is None

    @pytest.mark.asyncio
    async def test_extract_tweet_data_success(self):
        """Test successful tweet data extraction"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(logger=logger)
        mock_tweet = MagicMock()

        # Mock locator responses
        mock_text_locator = MagicMock()
        mock_text_locator.count = AsyncMock(return_value=1)
        mock_text_first = MagicMock()
        mock_text_first.inner_text = AsyncMock(return_value="Test tweet content")
        mock_text_locator.first = mock_text_first

        mock_time_locator = MagicMock()
        mock_time_locator.count = AsyncMock(return_value=1)
        mock_time_first = MagicMock()
        mock_time_first.get_attribute = AsyncMock(
            return_value="2025-01-27T12:00:00.000Z"
        )
        mock_time_locator.first = mock_time_first

        mock_link_locator = MagicMock()
        mock_link_locator.count = AsyncMock(return_value=1)
        mock_link_first = MagicMock()
        mock_link_first.get_attribute = AsyncMock(return_value="/nasa/status/123456789")
        mock_link_locator.first = mock_link_first

        def locator_side_effect(selector):
            if selector == '[data-testid="tweetText"]':
                return mock_text_locator
            elif selector == "time":
                return mock_time_locator
            elif selector == 'a[href*="/status/"]':
                return mock_link_locator
            else:
                return MagicMock()

        mock_tweet.locator.side_effect = locator_side_effect

        content, timestamp, url = await scraper._extract_tweet_data(mock_tweet)

        assert content == "Test tweet content"
        assert timestamp == "2025-01-27T12:00:00.000Z"
        assert url == "https://x.com/nasa/status/123456789"

    @pytest.mark.asyncio
    async def test_extract_tweet_data_fallback_content(self):
        """Test fallback to inner_text when tweetText not found"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(logger=logger)
        mock_tweet = MagicMock()
        mock_tweet.inner_text = AsyncMock(return_value="Fallback tweet content")

        # Mock locator responses - no text elements found
        mock_text_locator = MagicMock()
        mock_text_locator.count = AsyncMock(return_value=0)

        mock_time_locator = MagicMock()
        mock_time_locator.count = AsyncMock(return_value=1)
        mock_time_first = MagicMock()
        mock_time_first.get_attribute = AsyncMock(
            return_value="2025-01-27T12:00:00.000Z"
        )
        mock_time_locator.first = mock_time_first

        mock_link_locator = MagicMock()
        mock_link_locator.count = AsyncMock(return_value=1)
        mock_link_first = MagicMock()
        mock_link_first.get_attribute = AsyncMock(return_value="/nasa/status/123456789")
        mock_link_locator.first = mock_link_first

        def locator_side_effect(selector):
            if selector == '[data-testid="tweetText"]':
                return mock_text_locator
            elif selector == "time":
                return mock_time_locator
            elif selector == 'a[href*="/status/"]':
                return mock_link_locator
            else:
                return MagicMock()

        mock_tweet.locator.side_effect = locator_side_effect

        content, timestamp, url = await scraper._extract_tweet_data(mock_tweet)

        assert content == "Fallback tweet content"
        assert timestamp == "2025-01-27T12:00:00.000Z"
        assert url == "https://x.com/nasa/status/123456789"

    @pytest.mark.asyncio
    async def test_extract_tweet_data_no_timestamp(self):
        """Test handling when timestamp is not found"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(logger=logger)
        mock_tweet = MagicMock()
        mock_tweet.inner_text = AsyncMock(return_value="Test tweet content")

        # Mock locator responses
        mock_text_locator = MagicMock()
        mock_text_locator.count = AsyncMock(return_value=1)
        mock_text_first = MagicMock()
        mock_text_first.inner_text = AsyncMock(return_value="Test tweet content")
        mock_text_locator.first = mock_text_first

        mock_time_locator = MagicMock()
        mock_time_locator.count = AsyncMock(return_value=0)  # No timestamp found

        mock_link_locator = MagicMock()
        mock_link_locator.count = AsyncMock(return_value=1)
        mock_link_first = MagicMock()
        mock_link_first.get_attribute = AsyncMock(return_value="/nasa/status/123456789")
        mock_link_locator.first = mock_link_first

        def locator_side_effect(selector):
            if selector == '[data-testid="tweetText"]':
                return mock_text_locator
            elif selector == "time":
                return mock_time_locator
            elif selector == 'a[href*="/status/"]':
                return mock_link_locator
            else:
                return MagicMock()

        mock_tweet.locator.side_effect = locator_side_effect

        # Execute with datetime patch
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2025-01-27T12:00:00.000Z"
            )
            content, timestamp, url = await scraper._extract_tweet_data(mock_tweet)

        assert content == "Test tweet content"
        assert timestamp == "2025-01-27T12:00:00.000Z"  # Should use current time
        assert url == "https://x.com/nasa/status/123456789"

    @pytest.mark.asyncio
    async def test_extract_tweet_data_no_url(self):
        """Test handling when URL is not found"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(logger=logger)
        mock_tweet = MagicMock()
        mock_tweet.inner_text = AsyncMock(return_value="Test tweet content")

        # Mock locator responses
        mock_text_locator = MagicMock()
        mock_text_locator.count = AsyncMock(return_value=1)
        mock_text_first = MagicMock()
        mock_text_first.inner_text = AsyncMock(return_value="Test tweet content")
        mock_text_locator.first = mock_text_first

        mock_time_locator = MagicMock()
        mock_time_locator.count = AsyncMock(return_value=1)
        mock_time_first = MagicMock()
        mock_time_first.get_attribute = AsyncMock(
            return_value="2025-01-27T12:00:00.000Z"
        )
        mock_time_locator.first = mock_time_first

        mock_link_locator = MagicMock()
        mock_link_locator.count = AsyncMock(return_value=0)  # No URL found

        def locator_side_effect(selector):
            if selector == '[data-testid="tweetText"]':
                return mock_text_locator
            elif selector == "time":
                return mock_time_locator
            elif selector == 'a[href*="/status/"]':
                return mock_link_locator
            else:
                return MagicMock()

        mock_tweet.locator.side_effect = locator_side_effect

        content, timestamp, url = await scraper._extract_tweet_data(mock_tweet)

        assert content == "Test tweet content"
        assert timestamp == "2025-01-27T12:00:00.000Z"
        assert url is None

    @pytest.mark.asyncio
    async def test_extract_tweet_data_relative_url(self):
        """Test handling of relative URLs"""
        logger = LoggerService(firebase_logger=None)  # Disable Firebase in tests
        scraper = TwitterScraper(logger=logger)
        mock_tweet = MagicMock()
        mock_tweet.inner_text = AsyncMock(return_value="Test tweet content")

        # Mock locator responses
        mock_text_locator = MagicMock()
        mock_text_locator.count = AsyncMock(return_value=1)
        mock_text_first = MagicMock()
        mock_text_first.inner_text = AsyncMock(return_value="Test tweet content")
        mock_text_locator.first = mock_text_first

        mock_time_locator = MagicMock()
        mock_time_locator.count = AsyncMock(return_value=1)
        mock_time_first = MagicMock()
        mock_time_first.get_attribute = AsyncMock(
            return_value="2025-01-27T12:00:00.000Z"
        )
        mock_time_locator.first = mock_time_first

        mock_link_locator = MagicMock()
        mock_link_locator.count = AsyncMock(return_value=1)
        mock_link_first = MagicMock()
        mock_link_first.get_attribute = AsyncMock(
            return_value="/nasa/status/123456789"
        )  # Relative URL
        mock_link_locator.first = mock_link_first

        def locator_side_effect(selector):
            if selector == '[data-testid="tweetText"]':
                return mock_text_locator
            elif selector == "time":
                return mock_time_locator
            elif selector == 'a[href*="/status/"]':
                return mock_link_locator
            else:
                return MagicMock()

        mock_tweet.locator.side_effect = locator_side_effect

        content, timestamp, url = await scraper._extract_tweet_data(mock_tweet)

        assert content == "Test tweet content"
        assert timestamp == "2025-01-27T12:00:00.000Z"
        assert (
            url == "https://x.com/nasa/status/123456789"
        )  # Should be converted to full URL
