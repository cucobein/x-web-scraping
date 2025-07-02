"""
Pool manager for domain-specific context pools
"""
from typing import Dict, Optional
from playwright.async_api import Browser, BrowserContext
from src.services.context_pool import ContextPool


class PoolManager:
    """Manages multiple domain-specific context pools"""
    
    def __init__(self, max_contexts_per_domain: int = 3):
        """
        Initialize pool manager
        
        Args:
            max_contexts_per_domain: Maximum contexts per domain pool
        """
        self.max_contexts_per_domain = max_contexts_per_domain
        self.pools: Dict[str, ContextPool] = {}
        self.browser: Optional[Browser] = None
    
    def register_domain(self, domain: str) -> None:
        """
        Register a domain for context pooling
        
        Args:
            domain: Domain to register (e.g., 'x.com', 'instagram.com')
        """
        if domain not in self.pools:
            self.pools[domain] = ContextPool(domain, self.max_contexts_per_domain)
    
    def set_browser(self, browser: Browser) -> None:
        """
        Set the browser instance for context creation
        
        Args:
            browser: Browser instance to use for creating contexts
        """
        self.browser = browser
    
    async def get_context_for_domain(self, domain: str, cookies: list, user_agent: str) -> BrowserContext:
        """
        Get a context for a specific domain
        
        Args:
            domain: Domain to get context for
            cookies: Cookies to inject into the context
            user_agent: User agent string to use
            
        Returns:
            Browser context ready for use
        """
        if not self.browser:
            raise RuntimeError("Browser not set. Call set_browser() first.")
        
        # Register domain if not already registered
        self.register_domain(domain)
        
        # Get context from the domain's pool
        return await self.pools[domain].get_context(self.browser, cookies, user_agent)
    
    async def return_context_to_domain(self, domain: str, context: BrowserContext) -> None:
        """
        Return a context to its domain pool
        
        Args:
            domain: Domain the context belongs to
            context: Context to return to the pool
        """
        if domain in self.pools:
            await self.pools[domain].return_context(context)
    
    async def close_all_pools(self) -> None:
        """Close all context pools"""
        for pool in self.pools.values():
            await pool.close_all()
        self.pools.clear()
    
    def get_pool_stats(self, domain: Optional[str] = None) -> dict:
        """
        Get statistics for pools
        
        Args:
            domain: Specific domain to get stats for, or None for all domains
            
        Returns:
            Dictionary with pool statistics
        """
        if domain:
            if domain in self.pools:
                return self.pools[domain].get_stats()
            return {}
        
        # Return stats for all pools
        all_stats = {}
        for domain, pool in self.pools.items():
            all_stats[domain] = pool.get_stats()
        return all_stats
    
    def get_registered_domains(self) -> list:
        """Get list of registered domains"""
        return list(self.pools.keys())
    
    def has_domain(self, domain: str) -> bool:
        """Check if a domain is registered"""
        return domain in self.pools 