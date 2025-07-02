"""
Context pool management for browser contexts
"""
from typing import List
from playwright.async_api import Browser, BrowserContext


class ContextPool:
    """Manages a pool of browser contexts for a specific domain"""
    
    def __init__(self, domain: str, max_contexts: int = 3):
        """
        Initialize context pool for a domain
        
        Args:
            domain: Domain this pool manages contexts for
            max_contexts: Maximum number of contexts to maintain
        """
        self.domain = domain
        self.max_contexts = max_contexts
        self.available_contexts: List[BrowserContext] = []
        self.in_use_contexts: List[BrowserContext] = []
    
    async def get_context(self, browser: Browser, cookies: List[dict], user_agent: str) -> BrowserContext:
        """
        Get a context from the pool, creating a new one if needed
        
        Args:
            browser: Browser instance to create contexts with
            cookies: Cookies to inject into the context
            user_agent: User agent string to use
            
        Returns:
            Browser context ready for use
        """
        # Try to get an available context
        if self.available_contexts:
            context = self.available_contexts.pop()
            self.in_use_contexts.append(context)
            return context
        
        # Create new context if under limit
        if len(self.in_use_contexts) < self.max_contexts:
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1280, "height": 800}
            )
            
            # Inject cookies if provided
            if cookies:
                await context.add_cookies(cookies)
            
            self.in_use_contexts.append(context)
            return context
        
        # Wait for a context to become available (simple approach for now)
        # In a real implementation, this would be more sophisticated
        raise RuntimeError(f"No available contexts in pool for {self.domain}")
    
    async def return_context(self, context: BrowserContext) -> None:
        """
        Return a context to the pool
        
        Args:
            context: Context to return to the pool
        """
        if context in self.in_use_contexts:
            self.in_use_contexts.remove(context)
            self.available_contexts.append(context)
    
    async def close_all(self) -> None:
        """Close all contexts in the pool"""
        for context in self.available_contexts + self.in_use_contexts:
            try:
                await context.close()
            except Exception as e:
                print(f"Error closing context: {e}")
        
        self.available_contexts.clear()
        self.in_use_contexts.clear()
    
    def get_stats(self) -> dict:
        """Get pool statistics"""
        return {
            "domain": self.domain,
            "available": len(self.available_contexts),
            "in_use": len(self.in_use_contexts),
            "total": len(self.available_contexts) + len(self.in_use_contexts),
            "max_contexts": self.max_contexts
        } 