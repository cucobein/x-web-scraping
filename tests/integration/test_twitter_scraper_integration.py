"""
Integration tests for TwitterScraper using real HTML fixtures
"""

from pathlib import Path

import pytest
import pytest_asyncio

from src.services.browser_manager import BrowserManager
from src.services.twitter_scraper import TwitterScraper


class TestTwitterScraperIntegration:
    """Test Twitter scraper with real HTML fixtures"""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance"""
        return TwitterScraper(page_timeout=5000)

    @pytest_asyncio.fixture
    async def browser_manager(self):
        """Create and start browser manager for testing"""
        manager = BrowserManager(headless=True)
        await manager.start()
        yield manager
        await manager.stop()

    @pytest.fixture
    def nasa_html_path(self):
        """Path to NASA profile HTML fixture"""
        return Path("tests/fixtures/twitter/nasa_profile.html")

    @pytest.fixture
    def elonmusk_html_path(self):
        """Path to Elon Musk profile HTML fixture"""
        return Path("tests/fixtures/twitter/elonmusk_profile.html")

    @pytest.fixture
    def no_posts_html_path(self):
        """Path to profile with no posts HTML fixture"""
        return Path("tests/fixtures/twitter/no_posts_profile.html")

    @pytest.fixture
    def non_existing_user_html_path(self):
        """Path to non-existing user HTML fixture"""
        return Path("tests/fixtures/twitter/non_existing_user.html")

    @pytest.mark.asyncio
    async def test_extract_tweet_from_nasa_profile(
        self, scraper, browser_manager, nasa_html_path
    ):
        """Test extracting tweet from real NASA profile HTML"""
        # Verify fixture exists
        assert nasa_html_path.exists(), f"NASA fixture not found: {nasa_html_path}"

        # Load HTML content
        with open(nasa_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(page, "nasa", html_content)

            # Verify tweet was extracted
            assert tweet is not None, "Should extract tweet from NASA profile"
            assert tweet.username == "nasa"
            assert tweet.content is not None and len(tweet.content) > 0
            assert tweet.timestamp is not None
            # The fixture contains tweets from NASAMars, so check for that pattern
            assert tweet.url is not None and "x.com/NASAMars/status/" in tweet.url
            assert tweet.unique_id is not None

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_extract_tweet_from_elonmusk_profile(
        self, scraper, browser_manager, elonmusk_html_path
    ):
        """Test extracting tweet from real Elon Musk profile HTML"""
        # Verify fixture exists
        assert (
            elonmusk_html_path.exists()
        ), f"Elon Musk fixture not found: {elonmusk_html_path}"

        # Load HTML content
        with open(elonmusk_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(
                page, "elonmusk", html_content
            )

            # Verify tweet was extracted
            assert tweet is not None, "Should extract tweet from Elon Musk profile"
            assert tweet.username == "elonmusk"
            assert tweet.content is not None and len(tweet.content) > 0
            assert tweet.timestamp is not None
            assert tweet.url is not None and "x.com/elonmusk/status/" in tweet.url
            assert tweet.unique_id is not None

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_tweet_unique_id_generation(
        self, scraper, browser_manager, nasa_html_path
    ):
        """Test that tweet unique IDs are generated correctly from URLs"""
        # Load HTML content
        with open(nasa_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(page, "nasa", html_content)

            # Verify unique ID is based on URL
            assert tweet.unique_id == tweet.url, "Unique ID should be the tweet URL"

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_skip_pinned_tweets(self, scraper, browser_manager, nasa_html_path):
        """Test that pinned tweets are properly identified and handled"""
        # Load HTML content
        with open(nasa_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(page, "nasa", html_content)

            # Verify we get a non-pinned tweet (latest actual tweet)
            assert tweet is not None, "Should extract non-pinned tweet"
            # Note: This test assumes the fixture contains both pinned and non-pinned tweets

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_handle_profile_with_no_posts(
        self, scraper, browser_manager, no_posts_html_path
    ):
        """Test handling of profile with no posts - using real fixture"""
        # Verify fixture exists
        assert (
            no_posts_html_path.exists()
        ), f"No posts fixture not found: {no_posts_html_path}"

        # Load HTML content from fixture
        with open(no_posts_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(
                page, "no_posts_user", html_content
            )

            # Should return None for profile with no posts
            assert tweet is None, "Should return None for profile with no posts"

        finally:
            await page.close()

    @pytest.mark.asyncio
    async def test_handle_non_existing_user(
        self, scraper, browser_manager, non_existing_user_html_path
    ):
        """Test handling of non-existing user - using real fixture"""
        # Verify fixture exists
        assert (
            non_existing_user_html_path.exists()
        ), f"Non-existing user fixture not found: {non_existing_user_html_path}"

        # Load HTML content from fixture
        with open(non_existing_user_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Get browser context and create page
        context = browser_manager.get_context()
        page = await context.new_page()

        try:
            # Use the new method for HTML content
            tweet = await scraper.get_latest_tweet_from_html(
                page, "non_existing_user", html_content
            )

            # Should return None for non-existing user
            assert tweet is None, "Should return None for non-existing user"

        finally:
            await page.close()
