"""
Unit tests for PoolManager
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.pool_manager import PoolManager


class TestPoolManager:
    """Test pool manager functionality"""
    
    @pytest.fixture
    def pool_manager(self):
        """Create pool manager instance"""
        return PoolManager(max_contexts_per_domain=3)
    
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
    
    def test_initialization(self, pool_manager):
        """Test pool manager initialization"""
        assert pool_manager.max_contexts_per_domain == 3
        assert len(pool_manager.pools) == 0
        assert pool_manager.browser is None
    
    def test_initialization_with_custom_max_contexts(self):
        """Test initialization with custom max contexts"""
        manager = PoolManager(max_contexts_per_domain=5)
        assert manager.max_contexts_per_domain == 5
    
    def test_register_domain(self, pool_manager):
        """Test registering a domain"""
        pool_manager.register_domain("x.com")
        
        assert "x.com" in pool_manager.pools
        assert pool_manager.pools["x.com"].domain == "x.com"
        assert pool_manager.pools["x.com"].max_contexts == 3
    
    def test_register_domain_twice(self, pool_manager):
        """Test registering the same domain twice"""
        pool_manager.register_domain("x.com")
        pool_manager.register_domain("x.com")  # Should not create duplicate
        
        assert len(pool_manager.pools) == 1
        assert "x.com" in pool_manager.pools
    
    def test_set_browser(self, pool_manager, mock_browser):
        """Test setting browser instance"""
        pool_manager.set_browser(mock_browser)
        
        assert pool_manager.browser == mock_browser
    
    @pytest.mark.asyncio
    async def test_get_context_for_domain_without_browser(self, pool_manager, sample_cookies):
        """Test getting context without setting browser"""
        with pytest.raises(RuntimeError, match="Browser not set. Call set_browser\\(\\) first."):
            await pool_manager.get_context_for_domain("x.com", sample_cookies, "test_user_agent")
    
    @pytest.mark.asyncio
    async def test_get_context_for_domain_auto_registers(self, pool_manager, mock_browser, mock_context, sample_cookies):
        """Test getting context auto-registers domain"""
        pool_manager.set_browser(mock_browser)
        mock_browser.new_context.return_value = mock_context
        
        context = await pool_manager.get_context_for_domain("x.com", sample_cookies, "test_user_agent")
        
        # Verify domain was registered
        assert "x.com" in pool_manager.pools
        assert context == mock_context
    
    @pytest.mark.asyncio
    async def test_get_context_for_domain_uses_pool(self, pool_manager, mock_browser, mock_context, sample_cookies):
        """Test getting context uses the domain's pool"""
        pool_manager.set_browser(mock_browser)
        mock_browser.new_context.return_value = mock_context
        
        context = await pool_manager.get_context_for_domain("x.com", sample_cookies, "test_user_agent")
        
        # Verify the pool was used
        assert "x.com" in pool_manager.pools
        assert context == mock_context
    
    @pytest.mark.asyncio
    async def test_return_context_to_domain(self, pool_manager, mock_context):
        """Test returning context to domain pool"""
        # Register domain first
        pool_manager.register_domain("x.com")
        
        # Add context to in_use in the pool
        pool_manager.pools["x.com"].in_use_contexts.append(mock_context)
        
        await pool_manager.return_context_to_domain("x.com", mock_context)
        
        # Verify context was returned to pool
        assert len(pool_manager.pools["x.com"].in_use_contexts) == 0
        assert len(pool_manager.pools["x.com"].available_contexts) == 1
    
    @pytest.mark.asyncio
    async def test_return_context_to_nonexistent_domain(self, pool_manager, mock_context):
        """Test returning context to non-existent domain"""
        # Should not raise error, just do nothing
        await pool_manager.return_context_to_domain("nonexistent.com", mock_context)
    
    @pytest.mark.asyncio
    async def test_close_all_pools(self, pool_manager, mock_context):
        """Test closing all pools"""
        # Register domains and add contexts
        pool_manager.register_domain("x.com")
        pool_manager.register_domain("instagram.com")
        
        pool_manager.pools["x.com"].available_contexts.append(mock_context)
        pool_manager.pools["instagram.com"].in_use_contexts.append(mock_context)
        
        await pool_manager.close_all_pools()
        
        # Verify all pools are cleared
        assert len(pool_manager.pools) == 0
    
    def test_get_pool_stats_specific_domain(self, pool_manager):
        """Test getting stats for specific domain"""
        pool_manager.register_domain("x.com")
        
        stats = pool_manager.get_pool_stats("x.com")
        
        assert stats["domain"] == "x.com"
        assert stats["max_contexts"] == 3
    
    def test_get_pool_stats_nonexistent_domain(self, pool_manager):
        """Test getting stats for non-existent domain"""
        stats = pool_manager.get_pool_stats("nonexistent.com")
        
        assert stats == {}
    
    def test_get_pool_stats_all_domains(self, pool_manager):
        """Test getting stats for all domains"""
        pool_manager.register_domain("x.com")
        pool_manager.register_domain("instagram.com")
        
        all_stats = pool_manager.get_pool_stats()
        
        assert "x.com" in all_stats
        assert "instagram.com" in all_stats
        assert all_stats["x.com"]["domain"] == "x.com"
        assert all_stats["instagram.com"]["domain"] == "instagram.com"
    
    def test_get_registered_domains(self, pool_manager):
        """Test getting list of registered domains"""
        pool_manager.register_domain("x.com")
        pool_manager.register_domain("instagram.com")
        
        domains = pool_manager.get_registered_domains()
        
        assert "x.com" in domains
        assert "instagram.com" in domains
        assert len(domains) == 2
    
    def test_has_domain(self, pool_manager):
        """Test checking if domain is registered"""
        pool_manager.register_domain("x.com")
        
        assert pool_manager.has_domain("x.com") is True
        assert pool_manager.has_domain("instagram.com") is False 