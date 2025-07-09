"""
Core monitor that orchestrates all services
"""

import asyncio
from typing import Optional

from src.config.config_manager import ConfigManager
from src.repositories.tweet_repository import TweetRepository
from src.services.browser_manager import BrowserManager
from src.services.logger_service import LoggerService
from src.services.notification_service import NotificationService
from src.services.service_provider import ServiceProvider
from src.services.twitter_scraper import TwitterScraper


class XMonitor:
    """Main monitor that orchestrates all services"""

    def __init__(self, provider: Optional[ServiceProvider] = None) -> None:
        """
        Initialize XMonitor with services from provider

        Args:
            provider: ServiceProvider instance. If None, uses the global provider.
        """
        # Get services from provider
        if provider is None:
            from src.services import get_service_provider

            provider = get_service_provider()

        self.logger = provider.get(LoggerService)
        self.config_manager = provider.get(ConfigManager)
        self.browser_manager = provider.get(BrowserManager)
        self.twitter_scraper = provider.get(TwitterScraper)
        self.notification_service = provider.get(NotificationService)
        self.tweet_repository = provider.get(TweetRepository)

        # Internal state
        self.is_running = False

        self.logger.info(
            "XMonitor initialized",
            {
                "config_mode": self.config_manager.mode.value,
                "headless": self.config_manager.headless,
                "page_timeout": self.config_manager.page_timeout,
                "accounts_count": len(self.config_manager.accounts),
            },
        )

    async def process_account(self, username: str) -> bool:
        """
        Process a single account

        Args:
            username: Twitter username to process

        Returns:
            True if successful, False otherwise
        """
        # Create domain-specific context with cookies
        # Note: Currently hardcoded to "x.com" since we only scrape Twitter/X
        # When adding support for other domains (Facebook, Instagram, etc.),
        # this should be made domain-aware based on the account or configuration
        context = await self.browser_manager.create_context_for_domain("x.com")
        if not context:
            await self.notification_service.notify_error(
                username, "Browser context not available"
            )
            return False

        page = await context.new_page()
        try:
            tweet = await self.twitter_scraper.get_latest_tweet(
                page, username, self.browser_manager
            )

            if not tweet:
                await self.notification_service.notify_error(
                    username, "Could not fetch tweet"
                )
                return False

            # Check if this is a new tweet
            if self.tweet_repository.has_new_tweet(username, tweet):
                # Check if this is the first time we've seen this account
                if self.tweet_repository.get_last_tweet_id(username) is None:
                    # First check - just establish baseline, don't alert
                    await self.notification_service.notify_status(
                        f"   @{username}: First check (baseline established)"
                    )
                    self.tweet_repository.save_last_tweet(username, tweet)
                else:
                    # This is actually a new tweet - alert!
                    await self.notification_service.notify_new_tweet(tweet)
                    self.tweet_repository.save_last_tweet(username, tweet)
            else:
                await self.notification_service.notify_status(
                    f"   @{username}: No new posts"
                )

            return True

        except Exception as e:
            await self.notification_service.notify_error(username, str(e))
            return False
        finally:
            await page.close()
            # Close context instead of returning to pool
            await context.close()

    async def run_monitoring_cycle(self) -> None:
        """Run one complete monitoring cycle"""
        # Process all accounts in each cycle - no more batching
        accounts = self.config_manager.accounts

        await self.notification_service.notify_status(
            f"\n🔄 Checking: {', '.join(accounts)}"
        )

        for username in accounts:
            await self.process_account(username)

    async def start(self) -> None:
        """Start the monitoring service"""
        if self.is_running:
            return

        self.is_running = True
        await self.browser_manager.start()

        try:
            while self.is_running:
                await self.run_monitoring_cycle()

                # Refresh configuration during idle period
                self.config_manager.refresh()

                check_interval = self.config_manager.check_interval
                await self.notification_service.notify_status(
                    f"✅ Waiting {check_interval}s..."
                )
                await asyncio.sleep(check_interval)

        except KeyboardInterrupt:
            await self.notification_service.notify_status("\n🛑 Stopping...")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the monitoring service"""
        self.is_running = False
        await self.browser_manager.stop()
