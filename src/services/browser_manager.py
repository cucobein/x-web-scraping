"""
Browser management service with anti-detection features
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, async_playwright

from src.services.logger_service import LoggerService
from src.services.rate_limiter_service import RateLimiterService


class BrowserManager:
    """Manages browser lifecycle and context with anti-detection features"""

    def __init__(
        self,
        rate_limiter: RateLimiterService,
        logger: Optional[LoggerService] = None,
        headless: bool = True,
    ):
        """
        Initialize browser manager

        Args:
            rate_limiter: Rate limiter for anti-detection
            logger: Logger service (optional, uses default if not provided)
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.playwright = None
        self.rate_limiter = rate_limiter
        self.logger = logger

        # Domain-specific cookie configurations
        self.domain_cookies = self._load_domain_cookies()

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

            with open(cookie_file, "r") as f:
                cookie_data = json.load(f)

            return cookie_data  # type: ignore[no-any-return]

        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"Error loading cookies from {file_path}", {"error": str(e)}
                )
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

        # Add headless-specific arguments to make it behave more like regular browser
        browser_args = []
        if self.headless:
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Speed up loading
                "--disable-javascript-harmony-shipping",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ]

        if self.playwright is None:
            raise RuntimeError("Playwright not initialized")
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless, args=browser_args
        )

        # Use rotating user agent for anti-detection
        user_agent = self.rate_limiter.get_random_user_agent()

        # Prepare context settings based on headless mode
        context_settings = {
            "user_agent": user_agent,
            "viewport": {"width": 1280, "height": 800},
            "java_script_enabled": True,
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        }

        # Add headless-specific settings only in headless mode
        if self.headless:
            context_settings.update(
                {
                    "bypass_csp": True,  # Bypass Content Security Policy
                    "ignore_https_errors": True,
                }
            )
            context_settings["extra_http_headers"]["DNT"] = "1"  # type: ignore[index]

        self.context = await self.browser.new_context(**context_settings)

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

        # Always create fresh context (bypass pooling)
        user_agent = self.rate_limiter.get_random_user_agent()

        # Prepare context settings based on headless mode
        context_settings = {
            "user_agent": user_agent,
            "viewport": {"width": 1280, "height": 800},
            "java_script_enabled": True,
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        }

        # Add headless-specific settings only in headless mode
        if self.headless:
            context_settings.update(
                {
                    "bypass_csp": True,  # Bypass Content Security Policy
                    "ignore_https_errors": True,
                }
            )
            context_settings["extra_http_headers"]["DNT"] = "1"  # type: ignore[index]

        context = await self.browser.new_context(**context_settings)

        # Inject domain-specific cookies
        cookies = self.get_domain_cookies(domain)
        if cookies:
            await context.add_cookies(cookies)
            if self.logger:
                self.logger.info(f"Loaded cookies for {domain}")
        else:
            if self.logger:
                self.logger.warning(f"No cookies found for {domain}")

        return context

    async def clear_cache(self) -> None:
        """Clear browser cache and cookies"""
        if self.context:
            # Clear storage (localStorage, sessionStorage)
            await self.context.clear_permissions()

    async def stop(self) -> None:
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
        }

        return config
