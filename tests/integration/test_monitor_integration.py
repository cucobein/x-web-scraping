"""
Integration tests for full monitoring workflow - Real World Scenarios
"""

import json
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from src.core.monitor import XMonitor
from src.models.tweet import Tweet
from src.services.browser_manager import BrowserManager


class TestMonitorIntegration:
    """Test real-world scenarios for full monitoring workflow integration"""

    @pytest.fixture
    def monitor(self):
        """Create monitor instance with test config"""
        return XMonitor("config/config.json")

    @pytest_asyncio.fixture
    async def browser_manager(self):
        """Create and start browser manager for testing"""
        manager = BrowserManager(headless=True)
        await manager.start()
        yield manager
        await manager.stop()

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
            url="https://x.com/nasa/status/111111111",
        )

    @pytest.fixture
    def new_tweet(self):
        """Create new tweet for testing"""
        return Tweet(
            username="nasa",
            content="🚀 Exciting news from space! We've discovered a new exoplanet.",
            timestamp="2025-06-30T16:35:50.5680193-07:00",
            url="https://x.com/nasa/status/123456789",
        )

    @pytest.mark.asyncio
    async def test_first_time_monitoring_no_notification(
        self, monitor, browser_manager
    ):
        """Scenario: First time monitoring an account - should establish baseline without notification using real HTML fixtures"""
        # Replace monitor's browser manager with the one from fixture
        monitor.browser_manager = browser_manager

        # Load the real NASA HTML fixture
        with open(
            "tests/fixtures/twitter/nasa_profile.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()

        # Get browser context and create page (browser manager already started in fixture)
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Mock only the Telegram API (external dependency)
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
            ) as mock_post:
                # Use the fast HTML method to extract real tweet
                tweet = await monitor.twitter_scraper.get_latest_tweet_from_html(
                    page, "nasa", html_content
                )

                # Should extract a tweet from the fixture
                assert tweet is not None, "Should extract tweet from NASA profile"
                assert tweet.username == "nasa"

                # Mock the scraper to return the tweet we just extracted
                with patch.object(
                    monitor.twitter_scraper,
                    "get_latest_tweet",
                    new=AsyncMock(return_value=tweet),
                ):
                    # First time monitoring - should establish baseline
                    result = await monitor.process_account("nasa")

                    # Should succeed
                    assert result is True
                    # Should NOT send Telegram notification (first check)
                    mock_post.assert_not_called()
                    # Should save baseline tweet
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == tweet.unique_id
                    )

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_new_tweet_detected_with_notification(
        self, monitor, browser_manager, success_response_data
    ):
        """Scenario: New tweet detected - should send Telegram notification using real HTML fixtures"""
        # Replace monitor's browser manager with the one from fixture
        monitor.browser_manager = browser_manager

        # Load the real NASA HTML fixture
        with open(
            "tests/fixtures/twitter/nasa_profile.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()

        # Get browser context and create page (browser manager already started in fixture)
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Mock only the Telegram API (external dependency)
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
                new=AsyncMock(return_value=(200, success_response_data)),
            ) as mock_post:
                # Use the fast HTML method to extract real tweet
                tweet = await monitor.twitter_scraper.get_latest_tweet_from_html(
                    page, "nasa", html_content
                )

                # Should extract a tweet from the fixture
                assert tweet is not None, "Should extract tweet from NASA profile"
                assert tweet.username == "nasa"

                # Setup: Account already has baseline tweet (different from the one we just extracted)
                baseline_tweet = Tweet(
                    username="nasa",
                    content="🚀 Old baseline tweet from NASA",
                    timestamp="2025-06-30T10:00:00.0000000-07:00",
                    url="https://x.com/nasa/status/111111111",
                )
                monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)

                # Mock the scraper to return the tweet we just extracted
                with patch.object(
                    monitor.twitter_scraper,
                    "get_latest_tweet",
                    new=AsyncMock(return_value=tweet),
                ):
                    # New tweet detected - should send notification
                    result = await monitor.process_account("nasa")

                    # Should succeed
                    assert result is True
                    # Should send Telegram notification
                    mock_post.assert_called_once()
                    call_args = mock_post.call_args

                    # Verify notification content
                    form_data = call_args[1]["data"]
                    assert form_data["Message"].startswith("🔔 New Tweet from @nasa")
                    assert form_data["Url"] == tweet.url

                    # Verify API authentication
                    headers = call_args[1]["headers"]
                    assert (
                        headers["x-api-key"] == "47827973-e134-4ec1-9b11-458d3cc72962"
                    )

                    # Should update to new tweet
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == tweet.unique_id
                    )

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_no_new_tweets(self, monitor, browser_manager):
        """Scenario: No new tweets - should report no new posts using real HTML fixtures"""
        # Replace monitor's browser manager with the one from fixture
        monitor.browser_manager = browser_manager

        # Load the real NASA HTML fixture
        with open(
            "tests/fixtures/twitter/nasa_profile.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()

        # Get browser context and create page (browser manager already started in fixture)
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Mock only the Telegram API (external dependency)
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
            ) as mock_post:
                # Use the fast HTML method to extract real tweet
                tweet = await monitor.twitter_scraper.get_latest_tweet_from_html(
                    page, "nasa", html_content
                )

                # Should extract a tweet from the fixture
                assert tweet is not None, "Should extract tweet from NASA profile"
                assert tweet.username == "nasa"

                # Setup: Account has baseline tweet (same as the one we just extracted)
                monitor.tweet_repository.save_last_tweet("nasa", tweet)

                # Mock the scraper to return the same tweet
                with patch.object(
                    monitor.twitter_scraper,
                    "get_latest_tweet",
                    new=AsyncMock(return_value=tweet),
                ):
                    # Same tweet - no new posts
                    result = await monitor.process_account("nasa")

                    # Should succeed
                    assert result is True
                    # Should NOT send Telegram notification
                    mock_post.assert_not_called()
                    # Should keep same baseline
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == tweet.unique_id
                    )

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_telegram_api_failure_continues_monitoring(
        self, monitor, baseline_tweet, new_tweet, error_response_data
    ):
        """Scenario: Telegram API fails - system should continue monitoring"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)

        with patch.object(
            monitor.twitter_scraper,
            "get_latest_tweet",
            new=AsyncMock(return_value=new_tweet),
        ):
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
                new=AsyncMock(return_value=(401, error_response_data)),
            ) as mock_post:
                with patch.object(
                    monitor.browser_manager, "create_context_for_domain"
                ) as mock_create_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_create_context.return_value = mock_context_instance

                    # Telegram API fails but monitoring continues
                    result = await monitor.process_account("nasa")

                    # Should still succeed (Telegram failure doesn't break monitoring)
                    assert result is True
                    # Should attempt Telegram notification with retries (3 attempts)
                    assert mock_post.call_count == 3
                    # Should still update to new tweet
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == new_tweet.unique_id
                    )

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(
        self, monitor, browser_manager, success_response_data
    ):
        """Test that rate limiting is properly integrated into the monitoring workflow using real HTML fixtures"""
        # Replace monitor's browser manager with the one from fixture
        monitor.browser_manager = browser_manager

        # Load the real NASA HTML fixture
        with open(
            "tests/fixtures/twitter/nasa_profile.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()

        # Get browser context and create page (browser manager already started in fixture)
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Mock only the Telegram API (external dependency)
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
                new=AsyncMock(return_value=(200, success_response_data)),
            ) as mock_post:
                # Use the fast HTML method to test rate limiting integration
                tweet = await monitor.twitter_scraper.get_latest_tweet_from_html(
                    page, "nasa", html_content
                )

                # Should extract a tweet from the fixture
                assert tweet is not None, "Should extract tweet from NASA profile"
                assert tweet.username == "nasa"

                # Manually record a request to test rate limiting stats
                browser_manager.record_request("x.com")

                # Verify rate limiting stats are available and incremented
                stats = browser_manager.get_rate_limit_stats("x.com")
                assert "requests_in_last_minute" in stats
                assert "is_rate_limited" in stats
                assert stats["requests_in_last_minute"] >= 1

                # Now test the full monitor workflow with the extracted tweet
                # Mock the scraper to return the tweet we just extracted
                with patch.object(
                    monitor.twitter_scraper,
                    "get_latest_tweet",
                    new=AsyncMock(return_value=tweet),
                ):
                    # First check establishes baseline (no notification)
                    result = await monitor.process_account("nasa")
                    assert result is True
                    mock_post.assert_not_called()  # First check doesn't send notification

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_rate_limiting_with_multiple_accounts(self, monitor, browser_manager):
        """Test rate limiting behavior when processing multiple accounts using real HTML fixtures"""
        # Replace monitor's browser manager with the one from fixture
        monitor.browser_manager = browser_manager

        # Load the real NASA HTML fixture
        with open(
            "tests/fixtures/twitter/nasa_profile.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()

        # Get browser context and create page (browser manager already started in fixture)
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Process multiple accounts using fast HTML method
            accounts = ["nasa", "elonmusk", "BreakingNews"]
            for username in accounts:
                # Use the fast HTML method to extract tweets
                tweet = await monitor.twitter_scraper.get_latest_tweet_from_html(
                    page, username, html_content
                )
                assert tweet is not None, f"Should extract tweet for @{username}"

                # Manually record requests to test rate limiting
                browser_manager.record_request("x.com")

            # Check rate limiting stats
            stats = browser_manager.get_rate_limit_stats("x.com")
            assert stats["requests_in_last_minute"] >= len(accounts)
            assert not stats[
                "is_rate_limited"
            ]  # Should not be rate limited with default settings

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_telegram_retry_success_after_failure(
        self, monitor, baseline_tweet, new_tweet, success_response_data
    ):
        """Scenario: Telegram API succeeds after initial failure - should retry and succeed"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)

        # Mock HTTP client to fail twice, then succeed
        mock_post = AsyncMock()
        mock_post.side_effect = [
            (500, {"error": "Internal Server Error"}),  # First attempt fails
            (503, {"error": "Service Unavailable"}),  # Second attempt fails
            (200, success_response_data),  # Third attempt succeeds
        ]

        with patch.object(
            monitor.twitter_scraper,
            "get_latest_tweet",
            new=AsyncMock(return_value=new_tweet),
        ):
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
                new=mock_post,
            ) as mock_post:
                with patch.object(
                    monitor.browser_manager, "create_context_for_domain"
                ) as mock_create_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_create_context.return_value = mock_context_instance

                    # Should succeed after retries
                    result = await monitor.process_account("nasa")

                    # Should succeed
                    assert result is True
                    # Should attempt Telegram notification 3 times (2 failures + 1 success)
                    assert mock_post.call_count == 3
                    # Should still update to new tweet
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == new_tweet.unique_id
                    )

    @pytest.mark.asyncio
    async def test_telegram_retry_exhausted_after_multiple_failures(
        self, monitor, baseline_tweet, new_tweet, error_response_data
    ):
        """Scenario: Telegram API fails all retry attempts - should continue monitoring"""
        # Setup: Account already has baseline tweet
        monitor.tweet_repository.save_last_tweet("nasa", baseline_tweet)

        # Mock HTTP client to fail all 3 attempts
        mock_post = AsyncMock()
        mock_post.side_effect = [
            (500, {"error": "Internal Server Error"}),  # First attempt fails
            (503, {"error": "Service Unavailable"}),  # Second attempt fails
            (401, error_response_data),  # Third attempt fails
        ]

        with patch.object(
            monitor.twitter_scraper,
            "get_latest_tweet",
            new=AsyncMock(return_value=new_tweet),
        ):
            with patch.object(
                monitor.notification_service.telegram_service.http_client,
                "post_form_data",
                new=mock_post,
            ) as mock_post:
                with patch.object(
                    monitor.browser_manager, "create_context_for_domain"
                ) as mock_create_context:
                    mock_page = AsyncMock()
                    mock_context_instance = AsyncMock()
                    mock_context_instance.new_page = AsyncMock(return_value=mock_page)
                    mock_create_context.return_value = mock_context_instance

                    # Should succeed even after all retries fail
                    result = await monitor.process_account("nasa")

                    # Should succeed (Telegram failure doesn't break monitoring)
                    assert result is True
                    # Should attempt Telegram notification 3 times (all failures)
                    assert mock_post.call_count == 3
                    # Should still update to new tweet
                    assert (
                        monitor.tweet_repository.get_last_tweet_id("nasa")
                        == new_tweet.unique_id
                    )
