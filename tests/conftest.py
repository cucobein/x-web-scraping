"""
Pytest configuration and shared fixtures
"""

import asyncio
from pathlib import Path

import pytest
from playwright.async_api import Page
from unittest.mock import AsyncMock

from src.models.tweet import Tweet


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_tweet():
    """Sample tweet for testing"""
    return Tweet(
        username="testuser",
        content="This is a test tweet content",
        timestamp="2024-01-15T10:30:00Z",
        url="https://x.com/testuser/status/123456789",
    )


@pytest.fixture
def mock_page():
    """Mock Playwright page for testing"""
    page = AsyncMock(spec=Page)

    # Mock page methods
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.new_page = AsyncMock()
    page.close = AsyncMock()

    return page


def load_html_fixture(fixture_name: str) -> str:
    """Load HTML fixture from file"""
    fixture_path = (
        Path(__file__).parent / "fixtures" / "twitter" / f"{fixture_name}.html"
    )
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


def create_mock_page_with_html(html_content: str) -> AsyncMock:
    """Create a mock page that returns specific HTML content"""
    page = AsyncMock(spec=Page)

    # Mock the locator to return HTML content
    def mock_locator(selector):
        locator = AsyncMock()

        if selector == "article":
            # Mock article elements
            locator.count = AsyncMock(return_value=2)  # Assume 2 tweets
            locator.nth = AsyncMock(return_value=mock_tweet_element())
        elif selector == '[data-testid="tweetText"]':
            # Mock tweet text elements
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.inner_text = AsyncMock(return_value="Test tweet content")
        elif selector == "time":
            # Mock time elements
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.get_attribute = AsyncMock(return_value="2024-01-15T10:30:00Z")
        elif selector == 'a[href*="/status/"]':
            # Mock link elements
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.get_attribute = AsyncMock(
                return_value="/testuser/status/123456789"
            )
        elif selector == '[data-testid="icon-pin"]':
            # Mock pin icon (not present by default)
            locator.count = AsyncMock(return_value=0)

        return locator

    page.locator = mock_locator
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.close = AsyncMock()

    return page


def mock_tweet_element():
    """Create a mock tweet element"""
    element = AsyncMock()

    # Mock locator method for the tweet element
    def mock_tweet_locator(selector):
        locator = AsyncMock()

        if selector == '[data-testid="icon-pin"]':
            # No pin icon by default
            locator.count = AsyncMock(return_value=0)
        elif selector == '[data-testid="tweetText"]':
            # Mock tweet text
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.inner_text = AsyncMock(return_value="Test tweet content")
        elif selector == "time":
            # Mock timestamp
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.get_attribute = AsyncMock(return_value="2024-01-15T10:30:00Z")
        elif selector == 'a[href*="/status/"]':
            # Mock tweet URL
            locator.count = AsyncMock(return_value=1)
            locator.first = AsyncMock()
            locator.first.get_attribute = AsyncMock(
                return_value="/testuser/status/123456789"
            )

        return locator

    element.locator = mock_tweet_locator
    element.inner_text = AsyncMock(return_value="Test tweet content")

    return element
