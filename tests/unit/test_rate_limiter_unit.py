"""Unit tests for RateLimiter"""
import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock
from src.services.rate_limiter import RateLimiter, RateLimitConfig


class TestRateLimitConfig:
    """Test rate limiting configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = RateLimitConfig()
        assert config.requests_per_minute == 30
        assert config.burst_limit == 5
        assert config.backoff_multiplier == 2.0
        assert config.max_backoff_seconds == 300
        assert config.min_delay_seconds == 2.0
        assert config.max_delay_seconds == 8.0
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = RateLimitConfig(
            requests_per_minute=10,
            burst_limit=3,
            backoff_multiplier=1.5,
            max_backoff_seconds=60,
            min_delay_seconds=1.0,
            max_delay_seconds=5.0
        )
        assert config.requests_per_minute == 10
        assert config.burst_limit == 3
        assert config.backoff_multiplier == 1.5
        assert config.max_backoff_seconds == 60
        assert config.min_delay_seconds == 1.0
        assert config.max_delay_seconds == 5.0


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance"""
        return RateLimiter()
    
    @pytest.fixture
    def fast_rate_limiter(self):
        """Create rate limiter with fast settings for testing"""
        config = RateLimitConfig(
            requests_per_minute=5,
            min_delay_seconds=0.1,
            max_delay_seconds=0.2
        )
        return RateLimiter(config)
    
    def test_initialization(self, rate_limiter):
        """Test rate limiter initialization"""
        assert rate_limiter.config is not None
        assert len(rate_limiter.user_agents) > 0
        assert rate_limiter.request_times == {}
        assert rate_limiter.backoff_until == {}
    
    def test_get_random_user_agent(self, rate_limiter):
        """Test user agent rotation"""
        user_agents = set()
        for _ in range(10):
            user_agent = rate_limiter.get_random_user_agent()
            user_agents.add(user_agent)
            assert user_agent in rate_limiter.user_agents
        
        # Should have some variety (not always the same)
        assert len(user_agents) > 1
    
    def test_get_random_delay(self, rate_limiter):
        """Test random delay generation"""
        delays = []
        for _ in range(10):
            delay = rate_limiter.get_random_delay()
            delays.append(delay)
            assert rate_limiter.config.min_delay_seconds <= delay <= rate_limiter.config.max_delay_seconds
        
        # Should have some variety
        assert len(set(delays)) > 1
    
    def test_record_request(self, rate_limiter):
        """Test request recording"""
        domain = "x.com"
        
        # Initially no requests
        assert len(rate_limiter.request_times[domain]) == 0
        
        # Record a request
        rate_limiter.record_request(domain)
        assert len(rate_limiter.request_times[domain]) == 1
        
        # Record another request
        rate_limiter.record_request(domain)
        assert len(rate_limiter.request_times[domain]) == 2
    
    def test_is_rate_limited_false(self, rate_limiter):
        """Test rate limiting check when not limited"""
        domain = "x.com"
        
        # Should not be rate limited initially
        assert not rate_limiter.is_rate_limited(domain)
        
        # Add some requests but not enough to trigger limit
        for _ in range(5):
            rate_limiter.record_request(domain)
        
        assert not rate_limiter.is_rate_limited(domain)
    
    def test_is_rate_limited_true(self, fast_rate_limiter):
        """Test rate limiting check when limited"""
        domain = "x.com"
        
        # Add enough requests to trigger rate limit
        for _ in range(6):  # More than the 5 per minute limit
            fast_rate_limiter.record_request(domain)
        
        assert fast_rate_limiter.is_rate_limited(domain)
    
    def test_is_rate_limited_backoff(self, rate_limiter):
        """Test rate limiting during backoff period"""
        domain = "x.com"
        
        # Set backoff period
        rate_limiter.backoff_until[domain] = time.time() + 10
        
        assert rate_limiter.is_rate_limited(domain)
    
    def test_get_stats(self, rate_limiter):
        """Test statistics retrieval"""
        domain = "x.com"
        
        # Add some requests
        for _ in range(3):
            rate_limiter.record_request(domain)
        
        stats = rate_limiter.get_stats(domain)
        
        assert stats["requests_in_last_minute"] == 3
        assert stats["requests_per_minute_limit"] == 30
        assert not stats["is_rate_limited"]
        assert stats["backoff_until"] == 0
    
    def test_get_stats_rate_limited(self, fast_rate_limiter):
        """Test statistics when rate limited"""
        domain = "x.com"
        
        # Add enough requests to trigger rate limit
        for _ in range(6):
            fast_rate_limiter.record_request(domain)
        
        stats = fast_rate_limiter.get_stats(domain)
        
        assert stats["requests_in_last_minute"] == 6
        assert stats["requests_per_minute_limit"] == 5
        assert stats["is_rate_limited"]
    
    def test_reset_domain(self, rate_limiter):
        """Test domain reset"""
        domain = "x.com"
        
        # Add some requests and backoff
        rate_limiter.record_request(domain)
        rate_limiter.backoff_until[domain] = time.time() + 10
        
        # Reset the domain
        rate_limiter.reset_domain(domain)
        
        assert len(rate_limiter.request_times[domain]) == 0
        assert rate_limiter.backoff_until[domain] == 0
        assert not rate_limiter.is_rate_limited(domain)
    
    def test_reset_all(self, rate_limiter):
        """Test reset all domains"""
        domains = ["x.com", "api.x.com", "telegram.com"]
        
        # Add requests to multiple domains
        for domain in domains:
            rate_limiter.record_request(domain)
            rate_limiter.backoff_until[domain] = time.time() + 10
        
        # Reset all
        rate_limiter.reset_all()
        
        for domain in domains:
            assert len(rate_limiter.request_times[domain]) == 0
            assert rate_limiter.backoff_until[domain] == 0
            assert not rate_limiter.is_rate_limited(domain)
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_no_wait(self, fast_rate_limiter):
        """Test wait_if_needed when no waiting is required"""
        domain = "x.com"
        
        start_time = time.time()
        await fast_rate_limiter.wait_if_needed(domain)
        end_time = time.time()
        
        # Should have waited for random delay (0.1-0.2 seconds)
        elapsed = end_time - start_time
        assert 0.1 <= elapsed <= 0.3  # Allow some tolerance
        
        # Should have recorded the request
        assert len(fast_rate_limiter.request_times[domain]) == 1
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_rate_limited(self, fast_rate_limiter):
        """Test wait_if_needed when rate limited"""
        domain = "x.com"
        
        # Add enough requests to trigger rate limit
        for _ in range(5):
            fast_rate_limiter.record_request(domain)
        
        # Mock the sleep to avoid long waits
        with patch('asyncio.sleep') as mock_sleep:
            start_time = time.time()
            await fast_rate_limiter.wait_if_needed(domain)
            end_time = time.time()
            
            # Should have called sleep for backoff
            assert mock_sleep.called
            
            # Should still be rate limited after backoff
            assert fast_rate_limiter.is_rate_limited(domain)
    
    @pytest.mark.asyncio
    async def test_wait_if_needed_backoff_period(self, fast_rate_limiter):
        """Test wait_if_needed during backoff period"""
        domain = "x.com"
        
        # Set backoff period
        backoff_duration = 0.5  # 500ms
        fast_rate_limiter.backoff_until[domain] = time.time() + backoff_duration
        
        start_time = time.time()
        await fast_rate_limiter.wait_if_needed(domain)
        end_time = time.time()
        
        # Should have waited for the backoff duration
        elapsed = end_time - start_time
        assert elapsed >= backoff_duration
    
    def test_old_requests_cleanup(self, rate_limiter):
        """Test cleanup of old request times"""
        domain = "x.com"
        
        # Add some old requests (more than 60 seconds ago)
        old_time = time.time() - 70
        rate_limiter.request_times[domain].extend([old_time, old_time, old_time])
        
        # Add some recent requests
        recent_time = time.time()
        rate_limiter.request_times[domain].extend([recent_time, recent_time])
        
        # Check stats (should trigger cleanup)
        stats = rate_limiter.get_stats(domain)
        
        # Should only count recent requests
        assert stats["requests_in_last_minute"] == 2
        assert len(rate_limiter.request_times[domain]) == 2
    
    def test_multiple_domains(self, rate_limiter):
        """Test rate limiting for multiple domains"""
        domains = ["x.com", "api.x.com", "telegram.com"]
        
        # Add requests to different domains
        for domain in domains:
            rate_limiter.record_request(domain)
        
        # Each domain should be tracked separately
        for domain in domains:
            assert len(rate_limiter.request_times[domain]) == 1
            assert not rate_limiter.is_rate_limited(domain)
    
    @pytest.mark.asyncio
    async def test_backoff_calculation(self, rate_limiter):
        """Test exponential backoff calculation"""
        domain = "x.com"
        
        # Add many requests to trigger backoff
        for _ in range(35):  # More than 30 per minute
            rate_limiter.record_request(domain)
        
        # Should be rate limited
        assert rate_limiter.is_rate_limited(domain)
        
        # The backoff is only set when wait_if_needed is called, not on record_request
        # So we need to call wait_if_needed to trigger the backoff
        # But we'll mock the sleep to avoid the long wait
        with patch('asyncio.sleep') as mock_sleep:
            # This will set the backoff
            await rate_limiter.wait_if_needed(domain)
            
            # Now check that backoff is set
            assert rate_limiter.backoff_until[domain] > time.time() 