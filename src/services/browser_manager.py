"""
Browser management service
"""
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext


class BrowserManager:
    """Manages browser lifecycle and context"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
    
    async def start(self) -> BrowserContext:
        """Initialize browser and context"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
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