"""
Rate limiting service for controlling request frequency and preventing detection
"""

import asyncio
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""

    requests_per_minute: int = 30
    burst_limit: int = 5
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 300  # 5 minutes
    min_delay_seconds: float = 2.0
    max_delay_seconds: float = 8.0


class RateLimiterService:
    """Handles rate limiting for different domains with anti-detection features"""

    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter

        Args:
            config: Rate limiting configuration (used as default for domains without specific config)
        """
        self.default_config = config or RateLimitConfig()
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque())
        self.backoff_until: Dict[str, float] = defaultdict(float)

        # Domain-specific configurations
        self.domain_configs: Dict[str, RateLimitConfig] = {
            "x.com": RateLimitConfig(
                requests_per_minute=10,  # Very conservative for Twitter
                min_delay_seconds=3.0,  # Longer delays
                max_delay_seconds=12.0,  # Longer delays
                backoff_multiplier=2.5,  # Steeper backoff
                max_backoff_seconds=600,  # 10 minutes max
            ),
            "twitter.com": RateLimitConfig(
                requests_per_minute=10,  # Same very conservative settings
                min_delay_seconds=3.0,
                max_delay_seconds=12.0,
                backoff_multiplier=2.5,
                max_backoff_seconds=600,
            ),
        }

        # Realistic user agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        ]

    def get_domain_config(self, domain: str) -> RateLimitConfig:
        """
        Get configuration for a specific domain

        Args:
            domain: Domain to get config for

        Returns:
            Domain-specific config or default config if not found
        """
        return self.domain_configs.get(domain, self.default_config)

    def get_random_user_agent(self) -> str:
        """Get a random user agent for rotation"""
        return random.choice(self.user_agents)

    def get_random_delay(self, domain: str = None) -> float:
        """
        Get a random delay between requests to simulate human behavior

        Args:
            domain: Domain to get delay for (uses domain-specific config if provided)
        """
        config = self.get_domain_config(domain) if domain else self.default_config
        return random.uniform(config.min_delay_seconds, config.max_delay_seconds)

    async def wait_if_needed(self, domain: str) -> None:
        """
        Wait if rate limit is exceeded for the domain

        Args:
            domain: Domain to check rate limit for
        """
        now = time.time()
        config = self.get_domain_config(domain)

        # Check if we're in backoff period
        if now < self.backoff_until[domain]:
            backoff_remaining = self.backoff_until[domain] - now
            await asyncio.sleep(backoff_remaining)
            return

        # Clean old request times (older than 1 minute)
        cutoff_time = now - 60
        while (
            self.request_times[domain] and self.request_times[domain][0] < cutoff_time
        ):
            self.request_times[domain].popleft()

        # Check if we've exceeded the rate limit
        if len(self.request_times[domain]) >= config.requests_per_minute:
            # Calculate backoff time using domain-specific config
            backoff_time = min(
                config.backoff_multiplier ** len(self.request_times[domain]),
                config.max_backoff_seconds,
            )
            self.backoff_until[domain] = now + backoff_time
            await asyncio.sleep(backoff_time)
            return

        # Add random delay to simulate human behavior (domain-specific)
        delay = self.get_random_delay(domain)
        await asyncio.sleep(delay)

        # Record this request
        self.request_times[domain].append(now)

    def record_request(self, domain: str) -> None:
        """
        Record a request for rate limiting purposes

        Args:
            domain: Domain that was requested
        """
        self.request_times[domain].append(time.time())

    def is_rate_limited(self, domain: str) -> bool:
        """
        Check if a domain is currently rate limited

        Args:
            domain: Domain to check

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()
        config = self.get_domain_config(domain)

        # Check backoff period
        if now < self.backoff_until[domain]:
            return True

        # Clean old request times
        cutoff_time = now - 60
        while (
            self.request_times[domain] and self.request_times[domain][0] < cutoff_time
        ):
            self.request_times[domain].popleft()

        # Check if we've exceeded the limit (domain-specific)
        return len(self.request_times[domain]) >= config.requests_per_minute

    def get_stats(self, domain: str) -> Dict[str, int]:
        """
        Get rate limiting statistics for a domain

        Args:
            domain: Domain to get stats for

        Returns:
            Dictionary with rate limiting statistics
        """
        now = time.time()
        config = self.get_domain_config(domain)

        # Clean old request times
        cutoff_time = now - 60
        while (
            self.request_times[domain] and self.request_times[domain][0] < cutoff_time
        ):
            self.request_times[domain].popleft()

        return {
            "requests_in_last_minute": len(self.request_times[domain]),
            "requests_per_minute_limit": config.requests_per_minute,
            "is_rate_limited": self.is_rate_limited(domain),
            "backoff_until": (
                int(self.backoff_until[domain])
                if self.backoff_until[domain] > now
                else 0
            ),
            "domain_config": {
                "requests_per_minute": config.requests_per_minute,
                "min_delay_seconds": config.min_delay_seconds,
                "max_delay_seconds": config.max_delay_seconds,
                "backoff_multiplier": config.backoff_multiplier,
            },
        }

    def reset_domain(self, domain: str) -> None:
        """
        Reset rate limiting for a specific domain

        Args:
            domain: Domain to reset
        """
        self.request_times[domain].clear()
        self.backoff_until[domain] = 0

    def reset_all(self) -> None:
        """Reset rate limiting for all domains"""
        self.request_times.clear()
        self.backoff_until.clear()
