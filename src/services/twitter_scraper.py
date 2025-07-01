"""
Twitter scraping service
"""
from typing import Optional, Tuple
from playwright.async_api import Page

from src.models.tweet import Tweet


class TwitterScraper:
    """Handles Twitter/X scraping operations"""
    
    def __init__(self, page_timeout: int = 5000):
        """
        Initialize Twitter scraper
        
        Args:
            page_timeout: Timeout for page operations in milliseconds
        """
        self.page_timeout = page_timeout
    
    async def get_latest_tweet(self, page: Page, username: str) -> Optional[Tweet]:
        """
        Get the latest tweet from a user's profile
        
        Args:
            page: Playwright page object
            username: Twitter username to scrape
            
        Returns:
            Tweet object or None if failed
        """
        try:
            await page.goto(f"https://x.com/{username}", timeout=60000)
            
            # Wait for page to load completely
            await page.wait_for_load_state("networkidle")
            
            # Try multiple selectors for tweets
            tweet_selectors = [
                "article[data-testid='tweet']",
                "article",
                "[data-testid='tweet']"
            ]
            
            tweets = None
            for selector in tweet_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=self.page_timeout)
                    tweets = page.locator(selector)
                    count = await tweets.count()
                    if count > 0:
                        break
                except:
                    continue
            
            if not tweets:
                print(f"No tweets found for @{username}")
                return None
            
            count = await tweets.count()
            print(f"Found {count} tweets for @{username}")
            
            for i in range(count):
                tweet = tweets.nth(i)
                
                # Check if this tweet is pinned (has pin icon)
                try:
                    pin_icon = tweet.locator('[data-testid="icon-pin"]')
                    is_pinned = await pin_icon.count() > 0
                    if is_pinned:
                        continue  # Skip pinned tweets
                except:
                    pass
                
                # Extract content, timestamp, and URL
                try:
                    content, timestamp, url = await self._extract_tweet_data(tweet)
                    if content and timestamp:
                        return Tweet(
                            username=username,
                            content=content,
                            timestamp=timestamp,
                            url=url
                        )
                except Exception as e:
                    print(f"Error extracting tweet data: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error with @{username}: {e}")
            return None
    
    async def _extract_tweet_data(self, tweet_element) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract content, timestamp, and URL from tweet element"""
        try:
            # Get tweet text - try multiple selectors
            text_selectors = [
                '[data-testid="tweetText"]',
                '[data-testid="tweet"] span',
                'span'
            ]
            
            content = None
            for selector in text_selectors:
                try:
                    text_elements = tweet_element.locator(selector)
                    if await text_elements.count() > 0:
                        content = await text_elements.first.inner_text()
                        if content and len(content.strip()) > 0:
                            break
                except:
                    continue
            
            if not content:
                # Fallback: get all text from tweet
                content = await tweet_element.inner_text()
            
            # Get timestamp
            time_elements = tweet_element.locator('time')
            if await time_elements.count() > 0:
                timestamp = await time_elements.first.get_attribute('datetime')
            else:
                from datetime import datetime
                timestamp = datetime.now().isoformat()
            
            # Get tweet URL
            url = None
            try:
                # Look for the tweet link (usually in an anchor tag with href)
                link_elements = tweet_element.locator('a[href*="/status/"]')
                if await link_elements.count() > 0:
                    url = await link_elements.first.get_attribute('href')
                    # Make sure it's a full URL
                    if url and not url.startswith('http'):
                        url = f"https://x.com{url}"
            except Exception as e:
                print(f"Error extracting URL: {e}")
            
            return (content.strip(), timestamp, url)
            
        except Exception as e:
            print(f"Error extracting tweet data: {e}")
            return None, None, None 