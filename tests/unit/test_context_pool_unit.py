"""
Unit tests for ContextPool
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.context_pool import ContextPool


class TestContextPool:
    """Test context pool functionality"""
    
    @pytest.fixture
    def context_pool(self):
        """Create context pool instance"""
        return ContextPool("x.com", max_contexts=3)
    
    @pytest.fixture
    def mock_browser(self):
        """Create mock browser"""
        browser = AsyncMock()
        browser.new_context = AsyncMock()
        return browser
    
    @pytest.fixture
    def mock_context(self):
        """Create mock browser context"""
        context = AsyncMock()
        context.add_cookies = AsyncMock()
        return context
    
    @pytest.fixture
    def sample_cookies(self):
        """Sample cookie data"""
        return [
            {"name": "auth_token", "value": "test_token", "domain": ".x.com"},
            {"name": "ct0", "value": "test_csrf", "domain": ".x.com"}
        ]
    
    def test_initialization(self, context_pool):
        """Test context pool initialization"""
        assert context_pool.domain == "x.com"
        assert context_pool.max_contexts == 3
        assert len(context_pool.available_contexts) == 0
        assert len(context_pool.in_use_contexts) == 0
    
    def test_initialization_with_custom_max_contexts(self):
        """Test initialization with custom max contexts"""
        pool = ContextPool("instagram.com", max_contexts=5)
        assert pool.max_contexts == 5
    
    @pytest.mark.asyncio
    async def test_get_context_creates_new_when_pool_empty(self, context_pool, mock_browser, mock_context, sample_cookies):
        """Test getting context creates new one when pool is empty"""
        mock_browser.new_context.return_value = mock_context
        
        context = await context_pool.get_context(mock_browser, sample_cookies, "test_user_agent")
        
        # Verify context was created
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
        
        # Verify cookies were injected
        mock_context.add_cookies.assert_called_once_with(sample_cookies)
        
        # Verify context is in use
        assert context == mock_context
        assert len(context_pool.in_use_contexts) == 1
        assert len(context_pool.available_contexts) == 0
    
    @pytest.mark.asyncio
    async def test_get_context_creates_new_without_cookies(self, context_pool, mock_browser, mock_context):
        """Test getting context without cookies"""
        mock_browser.new_context.return_value = mock_context
        
        context = await context_pool.get_context(mock_browser, [], "test_user_agent")
        
        # Verify context was created
        mock_browser.new_context.assert_called_once()
        
        # Verify no cookies were injected
        mock_context.add_cookies.assert_not_called()
        
        assert context == mock_context
    
    @pytest.mark.asyncio
    async def test_get_context_reuses_available_context(self, context_pool, mock_browser, mock_context, sample_cookies):
        """Test getting context reuses available context from pool"""
        # Add a context to available pool
        context_pool.available_contexts.append(mock_context)
        
        context = await context_pool.get_context(mock_browser, sample_cookies, "test_user_agent")
        
        # Verify no new context was created
        mock_browser.new_context.assert_not_called()
        
        # Verify context was moved from available to in_use
        assert context == mock_context
        assert len(context_pool.in_use_contexts) == 1
        assert len(context_pool.available_contexts) == 0
    
    @pytest.mark.asyncio
    async def test_get_context_raises_error_when_pool_full(self, context_pool, mock_browser, mock_context, sample_cookies):
        """Test getting context raises error when pool is at max capacity"""
        # Fill the pool to max capacity
        for _ in range(3):
            context_pool.in_use_contexts.append(mock_context)
        
        # Try to get another context
        with pytest.raises(RuntimeError, match="No available contexts in pool for x.com"):
            await context_pool.get_context(mock_browser, sample_cookies, "test_user_agent")
    
    @pytest.mark.asyncio
    async def test_return_context(self, context_pool, mock_context):
        """Test returning context to pool"""
        # Add context to in_use
        context_pool.in_use_contexts.append(mock_context)
        
        await context_pool.return_context(mock_context)
        
        # Verify context was moved from in_use to available
        assert len(context_pool.in_use_contexts) == 0
        assert len(context_pool.available_contexts) == 1
        assert context_pool.available_contexts[0] == mock_context
    
    @pytest.mark.asyncio
    async def test_return_context_not_in_use(self, context_pool, mock_context):
        """Test returning context that's not in use"""
        # Context is not in in_use list
        await context_pool.return_context(mock_context)
        
        # Should not be added to available
        assert len(context_pool.available_contexts) == 0
    
    @pytest.mark.asyncio
    async def test_close_all(self, context_pool, mock_context):
        """Test closing all contexts"""
        # Add contexts to both lists
        context_pool.available_contexts.append(mock_context)
        context_pool.in_use_contexts.append(mock_context)
        
        await context_pool.close_all()
        
        # Verify all contexts were closed
        assert mock_context.close.call_count == 2
        
        # Verify lists are cleared
        assert len(context_pool.available_contexts) == 0
        assert len(context_pool.in_use_contexts) == 0
    
    @pytest.mark.asyncio
    async def test_close_all_with_exception(self, context_pool, mock_context):
        """Test closing all contexts handles exceptions gracefully"""
        # Make close method raise an exception
        mock_context.close.side_effect = Exception("Close error")
        
        # Add context to pool
        context_pool.available_contexts.append(mock_context)
        
        # Should not raise exception
        await context_pool.close_all()
        
        # Verify lists are cleared even if close fails
        assert len(context_pool.available_contexts) == 0
        assert len(context_pool.in_use_contexts) == 0
    
    def test_get_stats_empty_pool(self, context_pool):
        """Test getting stats for empty pool"""
        stats = context_pool.get_stats()
        
        assert stats["domain"] == "x.com"
        assert stats["available"] == 0
        assert stats["in_use"] == 0
        assert stats["total"] == 0
        assert stats["max_contexts"] == 3
    
    def test_get_stats_with_contexts(self, context_pool, mock_context):
        """Test getting stats with contexts in pool"""
        # Add contexts to both lists
        context_pool.available_contexts.append(mock_context)
        context_pool.in_use_contexts.append(mock_context)
        context_pool.in_use_contexts.append(mock_context)
        
        stats = context_pool.get_stats()
        
        assert stats["domain"] == "x.com"
        assert stats["available"] == 1
        assert stats["in_use"] == 2
        assert stats["total"] == 3
        assert stats["max_contexts"] == 3 