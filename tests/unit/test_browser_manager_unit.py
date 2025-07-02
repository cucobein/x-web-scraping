"""
Unit tests for BrowserManager
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from src.services.browser_manager import BrowserManager
from src.services.rate_limiter import RateLimiter


class TestBrowserManager:
    """Test browser management functionality"""
    
    @pytest.fixture
    def browser_manager(self):
        """Create browser manager instance"""
        return BrowserManager(headless=True)
    
    @pytest.fixture
    def mock_cookie_data(self):
        """Sample cookie data for testing"""
        return [
            {
                "name": "auth_token",
                "value": "test_auth_token",
                "domain": ".x.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "Lax"
            },
            {
                "name": "ct0",
                "value": "test_csrf_token",
                "domain": ".x.com",
                "path": "/",
                "secure": True,
                "httpOnly": False,
                "sameSite": "Lax"
            }
        ]
    
    def test_initialization(self, browser_manager):
        """Test browser manager initialization"""
        assert browser_manager.headless is True
        assert browser_manager.browser is None
        assert browser_manager.context is None
        assert browser_manager.playwright is None
        assert isinstance(browser_manager.rate_limiter, RateLimiter)
        assert isinstance(browser_manager.domain_cookies, dict)
    
    def test_load_domain_cookies_structure(self, browser_manager):
        """Test that domain cookies are loaded with correct structure"""
        domain_cookies = browser_manager.domain_cookies
        
        # Should have expected domains
        assert "x.com" in domain_cookies
        assert "twitter.com" in domain_cookies
        
        # Should be lists (even if empty)
        assert isinstance(domain_cookies["x.com"], list)
        assert isinstance(domain_cookies["twitter.com"], list)
    
    def test_load_cookies_from_file_success(self, browser_manager, mock_cookie_data):
        """Test successful cookie loading from file"""
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_cookie_data))):
            with patch("pathlib.Path.exists", return_value=True):
                cookies = browser_manager._load_cookies_from_file("config/test_cookies.json")
                
                assert cookies == mock_cookie_data
    
    def test_load_cookies_from_file_not_found(self, browser_manager):
        """Test cookie loading when file doesn't exist"""
        with patch("pathlib.Path.exists", return_value=False):
            cookies = browser_manager._load_cookies_from_file("config/nonexistent.json")
            
            assert cookies == []
    
    def test_load_cookies_from_file_invalid_json(self, browser_manager):
        """Test cookie loading with invalid JSON"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch("pathlib.Path.exists", return_value=True):
                cookies = browser_manager._load_cookies_from_file("config/invalid.json")
                
                assert cookies == []
    
    def test_load_cookies_from_file_exception(self, browser_manager):
        """Test cookie loading when file read fails"""
        with patch("builtins.open", side_effect=Exception("File read error")):
            with patch("pathlib.Path.exists", return_value=True):
                cookies = browser_manager._load_cookies_from_file("config/error.json")
                
                assert cookies == []
    
    def test_get_domain_cookies_existing_domain(self, browser_manager, mock_cookie_data):
        """Test getting cookies for existing domain"""
        # Mock the domain cookies
        browser_manager.domain_cookies["x.com"] = mock_cookie_data
        
        cookies = browser_manager.get_domain_cookies("x.com")
        assert cookies == mock_cookie_data
    
    def test_get_domain_cookies_nonexistent_domain(self, browser_manager):
        """Test getting cookies for non-existent domain"""
        cookies = browser_manager.get_domain_cookies("nonexistent.com")
        assert cookies == []
    
    def test_get_domain_cookies_empty_domain(self, browser_manager):
        """Test getting cookies for domain with empty cookie list"""
        browser_manager.domain_cookies["empty.com"] = []
        
        cookies = browser_manager.get_domain_cookies("empty.com")
        assert cookies == []
    
    def test_get_domain_config(self, browser_manager, mock_cookie_data):
        """Test getting domain configuration"""
        # Mock domain cookies
        browser_manager.domain_cookies["x.com"] = mock_cookie_data
        
        config = browser_manager.get_domain_config("x.com")
        
        assert config["has_cookies"] is True
        assert config["cookie_count"] == 2
        assert "rate_limit_config" in config
    
    def test_get_domain_config_no_cookies(self, browser_manager):
        """Test getting domain configuration for domain without cookies"""
        config = browser_manager.get_domain_config("nonexistent.com")
        
        assert config["has_cookies"] is False
        assert config["cookie_count"] == 0
        assert "rate_limit_config" in config
    
    @pytest.mark.asyncio
    async def test_create_context_for_domain_success(self, browser_manager, mock_cookie_data):
        """Test creating context for domain with cookies"""
        # Mock browser and context
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context
        
        browser_manager.browser = mock_browser
        browser_manager.domain_cookies["x.com"] = mock_cookie_data
        # Ensure pool manager's browser is set if pooling is enabled
        if getattr(browser_manager, "pool_manager", None):
            browser_manager.pool_manager.set_browser(mock_browser)
        
        # Mock rate limiter
        browser_manager.rate_limiter.get_random_user_agent = MagicMock(return_value="test_user_agent")
        
        context = await browser_manager.create_context_for_domain("x.com")
        
        # Verify context was created with correct parameters
        mock_browser.new_context.assert_called_once_with(
            user_agent="test_user_agent",
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True,
            bypass_csp=True,
            ignore_https_errors=True,
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        
        # Verify cookies were added
        mock_context.add_cookies.assert_called_once_with(mock_cookie_data)
        
        assert context == mock_context
    
    @pytest.mark.asyncio
    async def test_create_context_for_domain_no_cookies(self, browser_manager):
        """Test creating context for domain without cookies"""
        # Mock browser and context
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context
        
        browser_manager.browser = mock_browser
        # Ensure pool manager's browser is set if pooling is enabled
        if getattr(browser_manager, "pool_manager", None):
            browser_manager.pool_manager.set_browser(mock_browser)
        browser_manager.rate_limiter.get_random_user_agent = MagicMock(return_value="test_user_agent")
        
        context = await browser_manager.create_context_for_domain("nonexistent.com")
        
        # Verify context was created
        mock_browser.new_context.assert_called_once()
        
        # Verify no cookies were added
        mock_context.add_cookies.assert_not_called()
        
        assert context == mock_context
    
    @pytest.mark.asyncio
    async def test_create_context_for_domain_browser_not_started(self, browser_manager):
        """Test creating context when browser is not started"""
        with pytest.raises(RuntimeError, match="Browser not started"):
            await browser_manager.create_context_for_domain("x.com")
    
    @pytest.mark.asyncio
    async def test_rate_limiter_integration(self, browser_manager):
        """Test that rate limiter integration works correctly"""
        # Test rate limiting methods delegate to rate limiter
        with patch.object(browser_manager.rate_limiter, 'wait_if_needed') as mock_wait:
            await browser_manager.wait_for_rate_limit("x.com")
            mock_wait.assert_called_once_with("x.com")
        
        with patch.object(browser_manager.rate_limiter, 'record_request') as mock_record:
            browser_manager.record_request("x.com")
            mock_record.assert_called_once_with("x.com")
        
        with patch.object(browser_manager.rate_limiter, 'get_stats') as mock_stats:
            browser_manager.get_rate_limit_stats("x.com")
            mock_stats.assert_called_once_with("x.com")
    
    def test_twitter_domain_has_twitter_cookies(self, browser_manager):
        """Test that Twitter domain loads Twitter cookies"""
        twitter_cookies = [{"name": "auth_token", "value": "twitter_token"}]
        
        with patch.object(browser_manager, '_load_cookies_from_file') as mock_load:
            mock_load.return_value = twitter_cookies
            
            # Reload domain cookies
            browser_manager.domain_cookies = browser_manager._load_domain_cookies()
            
            # Check that Twitter domain has Twitter cookies
            assert browser_manager.get_domain_cookies("x.com") == twitter_cookies
            assert browser_manager.get_domain_cookies("twitter.com") == twitter_cookies
    
    def test_unconfigured_domain_has_no_cookies(self, browser_manager):
        """Test that unconfigured domain has no cookies"""
        with patch.object(browser_manager, '_load_cookies_from_file') as mock_load:
            mock_load.return_value = []
            
            # Reload domain cookies
            browser_manager.domain_cookies = browser_manager._load_domain_cookies()
            
            # Check that unconfigured domain has no cookies
            assert browser_manager.get_domain_cookies("instagram.com") == []
    
    def test_custom_rate_limiter_injection(self):
        """Test that custom rate limiter can be injected"""
        custom_rate_limiter = RateLimiter()
        browser_manager = BrowserManager(rate_limiter=custom_rate_limiter)
        
        assert browser_manager.rate_limiter is custom_rate_limiter
    
    def test_headless_mode_configuration(self):
        """Test headless mode configuration"""
        # Test headless mode
        headless_manager = BrowserManager(headless=True)
        assert headless_manager.headless is True
        
        # Test non-headless mode
        non_headless_manager = BrowserManager(headless=False)
        assert non_headless_manager.headless is False 