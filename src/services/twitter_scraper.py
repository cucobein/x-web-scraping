"""
Twitter scraping service
"""

from typing import Any, Optional, Tuple

from playwright.async_api import Page

from src.models.tweet import Tweet
from src.services.logger_service import LoggerService


class TwitterScraper:
    """Handles Twitter/X scraping operations"""

    def __init__(
        self, page_timeout: int = 5000, logger: Optional[LoggerService] = None
    ):
        """
        Initialize Twitter scraper

        Args:
            page_timeout: Timeout for page operations in milliseconds
            logger: Optional logger service
        """
        self.page_timeout = page_timeout
        self.logger = logger

    async def get_latest_tweet(
        self, page: Page, username: str, browser_manager: Optional[Any] = None
    ) -> Optional[Tweet]:
        """
        Get the latest tweet from a user's profile

        Args:
            page: Playwright page object
            username: Twitter username to scrape
            browser_manager: Optional browser manager for rate limiting

        Returns:
            Tweet object or None if failed
        """
        try:
            # Apply rate limiting if browser manager is provided
            if browser_manager:
                await browser_manager.wait_for_rate_limit("x.com")

            await page.goto(f"https://x.com/{username}", timeout=self.page_timeout)

            # Record the request for rate limiting
            if browser_manager:
                browser_manager.record_request("x.com")

            # Wait for page to load completely
            await page.wait_for_load_state("domcontentloaded")

            # Add short wait for dynamic content
            await page.wait_for_timeout(5000)

            return await self._extract_latest_tweet_from_page(page, username)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error with @{username}", {"error": str(e)})
            return None

    async def get_latest_tweet_from_html(
        self, page: Page, username: str, html_content: str
    ) -> Optional[Tweet]:
        """
        Get the latest tweet from pre-loaded HTML content (for testing)

        This method uses a fast extraction approach with shorter timeouts since the HTML
        content is already loaded and doesn't require network requests. This significantly
        improves test performance, especially for fixtures that contain no tweets.

        Args:
            page: Playwright page object
            username: Twitter username to scrape
            html_content: HTML content to load into the page

        Returns:
            Tweet object or None if failed
        """
        try:
            # Set HTML content directly
            await page.set_content(html_content)

            # Use shorter timeout for HTML content (faster for tests)
            return await self._extract_latest_tweet_from_page_fast(page, username)

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Error extracting tweet from HTML for @{username}",
                    {"error": str(e)},
                )
            return None

    async def _extract_latest_tweet_from_page(
        self, page: Page, username: str
    ) -> Optional[Tweet]:
        """
        Extract the latest tweet from a loaded page

        Args:
            page: Playwright page object with loaded content
            username: Twitter username

        Returns:
            Tweet object or None if failed
        """
        # Try multiple selectors for tweets
        tweet_selectors = [
            "article[data-testid='tweet']",
            "article",
            "[data-testid='tweet']",
        ]

        tweets = None
        for selector in tweet_selectors:
            try:
                await page.wait_for_selector(selector, timeout=self.page_timeout)
                tweets = page.locator(selector)
                count = await tweets.count()
                if count > 0:
                    break
            except Exception:
                continue

        if not tweets:
            if self.logger:
                self.logger.info(f"No tweets found for @{username}")
            return None

        count = await tweets.count()
        if self.logger:
            self.logger.info(f"Found {count} tweets for @{username}")

        for i in range(count):
            tweet = tweets.nth(i)

            # Check if this tweet is pinned (has pin icon)
            try:
                pin_icon = tweet.locator('[data-testid="icon-pin"]')
                is_pinned = await pin_icon.count() > 0
                if is_pinned:
                    continue  # Skip pinned tweets
            except Exception:
                pass

            # Extract content, timestamp, and URL
            try:
                content, timestamp, url = await self._extract_tweet_data(tweet)
                if content and timestamp:
                    return Tweet(
                        username=username, content=content, timestamp=timestamp, url=url
                    )
            except Exception as e:
                if self.logger:
                    self.logger.error("Error extracting tweet data", {"error": str(e)})
                continue

        return None

    async def _extract_latest_tweet_from_page_fast(
        self, page: Page, username: str
    ) -> Optional[Tweet]:
        """
        Extract the latest tweet from a loaded page with fast timeout (for testing)

        This method is optimized for testing scenarios where HTML content is pre-loaded.
        It uses shorter timeouts (500ms vs 5000ms) because:
        1. No network requests are needed (content is already loaded)
        2. DOM elements are immediately available
        3. Significantly improves test performance for edge cases (no tweets, errors)

        Performance improvement: Reduces wait time from 15 seconds to 1.5 seconds
        when no tweets are found (3 selectors × 500ms vs 3 selectors × 5000ms).

        Args:
            page: Playwright page object with loaded content
            username: Twitter username

        Returns:
            Tweet object or None if failed
        """
        # Try multiple selectors for tweets with shorter timeout
        tweet_selectors = [
            "article[data-testid='tweet']",
            "article",
            "[data-testid='tweet']",
        ]

        tweets = None
        for selector in tweet_selectors:
            try:
                # Use much shorter timeout for tests (500ms instead of 5000ms)
                await page.wait_for_selector(selector, timeout=500)
                tweets = page.locator(selector)
                count = await tweets.count()
                if count > 0:
                    break
            except Exception:
                continue

        if not tweets:
            if self.logger:
                self.logger.info(f"No tweets found for @{username}")
            return None

        count = await tweets.count()
        if self.logger:
            self.logger.info(f"Found {count} tweets for @{username}")

        for i in range(count):
            tweet = tweets.nth(i)

            # Check if this tweet is pinned (has pin icon)
            try:
                pin_icon = tweet.locator('[data-testid="icon-pin"]')
                is_pinned = await pin_icon.count() > 0
                if is_pinned:
                    continue  # Skip pinned tweets
            except Exception:
                pass

            # Extract content, timestamp, and URL
            try:
                content, timestamp, url = await self._extract_tweet_data(tweet)
                if content and timestamp:
                    return Tweet(
                        username=username, content=content, timestamp=timestamp, url=url
                    )
            except Exception as e:
                if self.logger:
                    self.logger.error("Error extracting tweet data", {"error": str(e)})
                continue

        return None

    async def _extract_tweet_data(
        self, tweet_element: Any
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract content, timestamp, and URL from tweet element"""
        try:
            # Get tweet text - try multiple selectors
            text_selectors = [
                '[data-testid="tweetText"]',
                '[data-testid="tweet"] span',
                "span",
            ]

            content = None
            for selector in text_selectors:
                try:
                    text_elements = tweet_element.locator(selector)
                    if await text_elements.count() > 0:
                        content = await text_elements.first.inner_text()
                        if content and len(content.strip()) > 0:
                            break
                except Exception:
                    continue

            if not content:
                # Fallback: get all text from tweet
                content = await tweet_element.inner_text()

            # Get timestamp
            time_elements = tweet_element.locator("time")
            if await time_elements.count() > 0:
                timestamp = await time_elements.first.get_attribute("datetime")
            else:
                from datetime import datetime

                timestamp = datetime.now().isoformat()

            # Get tweet URL
            url = None
            try:
                # Look for the tweet link (usually in an anchor tag with href)
                link_elements = tweet_element.locator('a[href*="/status/"]')
                if await link_elements.count() > 0:
                    url = await link_elements.first.get_attribute("href")
                    # Make sure it's a full URL
                    if url and not url.startswith("http"):
                        url = f"https://x.com{url}"
            except Exception as e:
                if self.logger:
                    self.logger.error("Error extracting URL", {"error": str(e)})

            return (content.strip(), timestamp, url)

        except Exception as e:
            if self.logger:
                self.logger.error("Error extracting tweet data", {"error": str(e)})
            return None, None, None
