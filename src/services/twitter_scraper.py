"""
Twitter scraping service
"""
from typing import Optional, Tuple
from playwright.async_api import Page

from src.models.tweet import Tweet


class TwitterScraper:
    """Handles Twitter/X scraping operations"""
    
    def __init__(self):
        pass
    
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
            await page.wait_for_load_state("networkidle")
            
            # Wait for tweets to load
            await page.wait_for_selector("article", timeout=15000)
            
            # Get all tweets and find the latest (first one that's not pinned)
            tweets = page.locator("article")
            count = await tweets.count()
            
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
            # Get tweet text
            text_elements = tweet_element.locator('[data-testid="tweetText"]')
            if await text_elements.count() > 0:
                content = await text_elements.first.inner_text()
            else:
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