"""
Rate limiting service for controlling request frequency and preventing detection
"""
import asyncio
import random
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 30
    burst_limit: int = 5
    backoff_multiplier: float = 2.0
    max_backoff_seconds: int = 300  # 5 minutes
    min_delay_seconds: float = 2.0
    max_delay_seconds: float = 8.0


class RateLimiter:
    """Handles rate limiting for different domains with anti-detection features"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter
        
        Args:
            config: Rate limiting configuration
        """
        self.config = config or RateLimitConfig()
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque())
        self.backoff_until: Dict[str, float] = defaultdict(float)
        
        # Realistic user agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent for rotation"""
        return random.choice(self.user_agents)
    
    def get_random_delay(self) -> float:
        """Get a random delay between requests to simulate human behavior"""
        return random.uniform(self.config.min_delay_seconds, self.config.max_delay_seconds)
    
    async def wait_if_needed(self, domain: str) -> None:
        """
        Wait if rate limit is exceeded for the domain
        
        Args:
            domain: Domain to check rate limit for
        """
        now = time.time()
        
        # Check if we're in backoff period
        if now < self.backoff_until[domain]:
            backoff_remaining = self.backoff_until[domain] - now
            await asyncio.sleep(backoff_remaining)
            return
        
        # Clean old request times (older than 1 minute)
        cutoff_time = now - 60
        while (self.request_times[domain] and 
               self.request_times[domain][0] < cutoff_time):
            self.request_times[domain].popleft()
        
        # Check if we've exceeded the rate limit
        if len(self.request_times[domain]) >= self.config.requests_per_minute:
            # Calculate backoff time
            backoff_time = min(
                self.config.backoff_multiplier ** len(self.request_times[domain]),
                self.config.max_backoff_seconds
            )
            self.backoff_until[domain] = now + backoff_time
            await asyncio.sleep(backoff_time)
            return
        
        # Add random delay to simulate human behavior
        delay = self.get_random_delay()
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
        
        # Check backoff period
        if now < self.backoff_until[domain]:
            return True
        
        # Clean old request times
        cutoff_time = now - 60
        while (self.request_times[domain] and 
               self.request_times[domain][0] < cutoff_time):
            self.request_times[domain].popleft()
        
        # Check if we've exceeded the limit
        return len(self.request_times[domain]) >= self.config.requests_per_minute
    
    def get_stats(self, domain: str) -> Dict[str, int]:
        """
        Get rate limiting statistics for a domain
        
        Args:
            domain: Domain to get stats for
            
        Returns:
            Dictionary with rate limiting statistics
        """
        now = time.time()
        
        # Clean old request times
        cutoff_time = now - 60
        while (self.request_times[domain] and 
               self.request_times[domain][0] < cutoff_time):
            self.request_times[domain].popleft()
        
        return {
            "requests_in_last_minute": len(self.request_times[domain]),
            "requests_per_minute_limit": self.config.requests_per_minute,
            "is_rate_limited": self.is_rate_limited(domain),
            "backoff_until": int(self.backoff_until[domain]) if self.backoff_until[domain] > now else 0
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