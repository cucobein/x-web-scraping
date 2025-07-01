"""
Browser management service with anti-detection features
"""
from typing import Optional
import json
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext
from src.services.rate_limiter import RateLimiter, RateLimitConfig


class BrowserManager:
    """Manages browser lifecycle and context with anti-detection features"""
    
    def __init__(self, headless: bool = True, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize browser manager
        
        Args:
            headless: Whether to run browser in headless mode
            rate_limiter: Optional rate limiter for anti-detection
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.rate_limiter = rate_limiter or RateLimiter()
    
    async def start(self) -> BrowserContext:
        """Initialize browser and context with anti-detection features"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
        # Use rotating user agent for anti-detection
        user_agent = self.rate_limiter.get_random_user_agent()
        
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800}
        )
        
        # Inject Twitter cookies
        cookies = self._load_twitter_cookies()
        if cookies:
            await self.context.add_cookies(cookies)
            print("🔐 Loaded Twitter cookies for authenticated session")
        
        return self.context
    
    async def clear_cache(self):
        """Clear browser cache and cookies"""
        if self.context:
            # Clear storage (localStorage, sessionStorage)
            await self.context.clear_permissions()
    
    async def stop(self):
        """Clean up browser resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def get_context(self) -> Optional[BrowserContext]:
        """Get current browser context"""
        return self.context
    
    async def wait_for_rate_limit(self, domain: str) -> None:
        """
        Wait for rate limiting before making a request to a domain
        
        Args:
            domain: Domain to check rate limit for
        """
        await self.rate_limiter.wait_if_needed(domain)
    
    def record_request(self, domain: str) -> None:
        """
        Record a request for rate limiting purposes
        
        Args:
            domain: Domain that was requested
        """
        self.rate_limiter.record_request(domain)
    
    def get_rate_limit_stats(self, domain: str) -> dict:
        """
        Get rate limiting statistics for a domain
        
        Args:
            domain: Domain to get stats for
            
        Returns:
            Dictionary with rate limiting statistics
        """
        return self.rate_limiter.get_stats(domain)
    
    def _load_twitter_cookies(self) -> list:
        """Load Twitter cookies from config file"""
        try:
            cookie_file = Path("config/twitter_cookies.json")
            if not cookie_file.exists():
                return []
            
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            return cookie_data
            
        except Exception as e:
            print(f"❌ Error loading Twitter cookies: {e}")
            return [] 