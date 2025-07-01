"""
Core monitor that orchestrates all services
"""
import asyncio
from typing import List

from src.config.config_manager import ConfigManager
from src.services.browser_manager import BrowserManager
from src.services.twitter_scraper import TwitterScraper
from src.services.notification_service import NotificationService
from src.repositories.tweet_repository import TweetRepository
from src.models.tweet import Tweet


class XMonitor:
    """Main monitor that orchestrates all services"""
    
    def __init__(self, config_path: str = "config/config.json"):
        # Initialize all services
        self.config_manager = ConfigManager(config_path)
        self.browser_manager = BrowserManager(self.config_manager.headless)
        self.twitter_scraper = TwitterScraper(page_timeout=self.config_manager.page_timeout)
        self.notification_service = NotificationService(self.config_manager)
        self.tweet_repository = TweetRepository()
        
        # Internal state
        self.current_index = 0
        self.is_running = False
    
    def get_next_batch(self, batch_size: int) -> List[str]:
        """Get next batch of accounts in order, cycling back to start when reaching end"""
        accounts = self.config_manager.accounts
        batch = []
        for _ in range(batch_size):
            batch.append(accounts[self.current_index])
            self.current_index = (self.current_index + 1) % len(accounts)
        return batch
    
    async def process_account(self, username: str) -> bool:
        """
        Process a single account
        
        Args:
            username: Twitter username to process
            
        Returns:
            True if successful, False otherwise
        """
        context = self.browser_manager.get_context()
        if not context:
            await self.notification_service.notify_error(username, "Browser context not available")
            return False
        
        page = await context.new_page()
        try:
            tweet = await self.twitter_scraper.get_latest_tweet(page, username)
            
            if not tweet:
                await self.notification_service.notify_error(username, "Could not fetch tweet")
                return False
            
            # Check if this is a new tweet
            if self.tweet_repository.has_new_tweet(username, tweet):
                # Check if this is the first time we've seen this account
                if self.tweet_repository.get_last_tweet_id(username) is None:
                    # First check - just establish baseline, don't alert
                    await self.notification_service.notify_status(f"   @{username}: First check (baseline established)")
                    self.tweet_repository.save_last_tweet(username, tweet)
                else:
                    # This is actually a new tweet - alert!
                    await self.notification_service.notify_new_tweet(tweet)
                    self.tweet_repository.save_last_tweet(username, tweet)
            else:
                await self.notification_service.notify_status(f"   @{username}: No new posts")
            
            return True
            
        except Exception as e:
            await self.notification_service.notify_error(username, str(e))
            return False
        finally:
            await page.close()
    
    async def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        sample_size = self.config_manager.sample_size
        selected = self.get_next_batch(sample_size)
        
        await self.notification_service.notify_status(f"\n🔄 Checking: {', '.join(selected)}")
        
        for username in selected:
            await self.process_account(username)
    
    async def start(self):
        """Start the monitoring service"""
        if self.is_running:
            return
        
        self.is_running = True
        await self.browser_manager.start()
        
        try:
            while self.is_running:
                await self.run_monitoring_cycle()
                
                check_interval = self.config_manager.check_interval
                await self.notification_service.notify_status(f"✅ Waiting {check_interval}s...")
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            await self.notification_service.notify_status("\n🛑 Stopping...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the monitoring service"""
        self.is_running = False
        await self.browser_manager.stop() 