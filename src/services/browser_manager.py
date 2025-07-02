"""
Browser management service with anti-detection features
"""
from typing import Optional, Dict, List
import json
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext
from src.services.rate_limiter import RateLimiter, RateLimitConfig
from src.services.pool_manager import PoolManager


class BrowserManager:
    """Manages browser lifecycle and context with anti-detection features"""
    
    def __init__(self, headless: bool = True, rate_limiter: Optional[RateLimiter] = None, 
                 enable_pooling: bool = True, max_contexts_per_domain: int = 3):
        """
        Initialize browser manager
        
        Args:
            headless: Whether to run browser in headless mode
            rate_limiter: Optional rate limiter for anti-detection
            enable_pooling: Whether to enable context pooling
            max_contexts_per_domain: Maximum contexts per domain when pooling is enabled
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.rate_limiter = rate_limiter or RateLimiter()
        self.enable_pooling = enable_pooling
        
        # Domain-specific cookie configurations
        self.domain_cookies = self._load_domain_cookies()
        
        # Context pooling
        if self.enable_pooling:
            self.pool_manager = PoolManager(max_contexts_per_domain)
        else:
            self.pool_manager = None
    
    def _load_domain_cookies(self) -> Dict[str, List[dict]]:
        """
        Load cookies for different domains
        
        Returns:
            Dictionary mapping domains to their cookie configurations
        """
        return {
            "x.com": self._load_cookies_from_file("config/twitter_cookies.json"),
            "twitter.com": self._load_cookies_from_file("config/twitter_cookies.json"),
            # Add more domains as needed:
            # "facebook.com": self._load_cookies_from_file("config/facebook_cookies.json"),
            # "instagram.com": self._load_cookies_from_file("config/instagram_cookies.json"),
            # "youtube.com": self._load_cookies_from_file("config/youtube_cookies.json"),
        }
    
    def _load_cookies_from_file(self, file_path: str) -> List[dict]:
        """
        Load cookies from a JSON file
        
        Args:
            file_path: Path to the cookie file
            
        Returns:
            List of cookie dictionaries
        """
        try:
            cookie_file = Path(file_path)
            if not cookie_file.exists():
                return []
            
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            return cookie_data
            
        except Exception as e:
            print(f"❌ Error loading cookies from {file_path}: {e}")
            return []
    
    def get_domain_cookies(self, domain: str) -> List[dict]:
        """
        Get cookies for a specific domain
        
        Args:
            domain: Domain to get cookies for
            
        Returns:
            List of cookie dictionaries for the domain
        """
        return self.domain_cookies.get(domain, [])
    
    async def start(self) -> BrowserContext:
        """Initialize browser and context with anti-detection features"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        
        # Initialize pool manager if enabled
        if self.enable_pooling and self.pool_manager:
            self.pool_manager.set_browser(self.browser)
        
        # Use rotating user agent for anti-detection
        user_agent = self.rate_limiter.get_random_user_agent()
        
        self.context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800}
        )
        
        # Note: Cookies are now injected per-domain when creating contexts
        # This maintains backward compatibility for the single context approach
        
        return self.context
    
    async def create_context_for_domain(self, domain: str) -> BrowserContext:
        """
        Create a new browser context with domain-specific cookies
        
        Args:
            domain: Domain to create context for
            
        Returns:
            Browser context with domain-specific cookies injected
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first.")
        
        # Use pooling if enabled
        if self.enable_pooling and self.pool_manager:
            cookies = self.get_domain_cookies(domain)
            user_agent = self.rate_limiter.get_random_user_agent()
            return await self.pool_manager.get_context_for_domain(domain, cookies, user_agent)
        
        # Fallback to direct context creation (backward compatibility)
        user_agent = self.rate_limiter.get_random_user_agent()
        
        context = await self.browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 800}
        )
        
        # Inject domain-specific cookies
        cookies = self.get_domain_cookies(domain)
        if cookies:
            await context.add_cookies(cookies)
            print(f"🔐 Loaded cookies for {domain}")
        
        return context
    
    async def return_context_to_pool(self, domain: str, context: BrowserContext) -> None:
        """
        Return a context to the pool for reuse
        
        Args:
            domain: Domain the context belongs to
            context: Context to return to the pool
        """
        if self.enable_pooling and self.pool_manager:
            await self.pool_manager.return_context_to_domain(domain, context)
    
    async def clear_cache(self):
        """Clear browser cache and cookies"""
        if self.context:
            # Clear storage (localStorage, sessionStorage)
            await self.context.clear_permissions()
    
    async def stop(self):
        """Clean up browser resources"""
        # Close all pooled contexts if pooling is enabled
        if self.enable_pooling and self.pool_manager:
            await self.pool_manager.close_all_pools()
        
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
    
    def get_domain_config(self, domain: str) -> dict:
        """
        Get configuration information for a domain
        
        Args:
            domain: Domain to get config for
            
        Returns:
            Dictionary with domain configuration
        """
        config = {
            "has_cookies": len(self.get_domain_cookies(domain)) > 0,
            "cookie_count": len(self.get_domain_cookies(domain)),
            "rate_limit_config": self.rate_limiter.get_domain_config(domain),
            "pooling_enabled": self.enable_pooling
        }
        
        # Add pooling stats if enabled
        if self.enable_pooling and self.pool_manager:
            config["pool_stats"] = self.pool_manager.get_pool_stats(domain)
        
        return config
    
    def get_pool_stats(self, domain: Optional[str] = None) -> dict:
        """
        Get context pool statistics
        
        Args:
            domain: Specific domain to get stats for, or None for all domains
            
        Returns:
            Dictionary with pool statistics
        """
        if not self.enable_pooling or not self.pool_manager:
            return {}
        
        return self.pool_manager.get_pool_stats(domain)
    
    def is_pooling_enabled(self) -> bool:
        """Check if context pooling is enabled"""
        return self.enable_pooling 