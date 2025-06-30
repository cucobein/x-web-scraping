"""
Unit tests for HTTP client service
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from src.services.http_client import HttpClient


class TestHttpClient:
    """Test HTTP client functionality"""
    
    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance"""
        return HttpClient(timeout=5, max_retries=2, retry_delay=0.1)
    
    @pytest.fixture
    def success_response_data(self):
        """Load success response fixture"""
        with open("tests/fixtures/telegram/success_response.json", "r") as f:
            return json.load(f)
    
    @pytest.fixture
    def error_response_data(self):
        """Load error response fixture"""
        with open("tests/fixtures/telegram/error_response.json", "r") as f:
            return json.load(f)
    
    @pytest.mark.asyncio
    async def test_post_form_data_success(self, http_client, success_response_data):
        """Test successful POST request with form data"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.content_type = 'application/json'
            mock_response.json = AsyncMock(return_value=success_response_data)
            
            # Mock session
            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value.__aenter__.return_value = mock_response
            mock_session.return_value = mock_session_instance
            
            # Test request
            status_code, response_data = await http_client.post_form_data(
                url="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                data={"Message": "Test message", "Url": "https://example.com"},
                headers={"x-api-key": "test-key"}
            )
            
            # Assertions
            assert status_code == 200
            assert response_data == success_response_data
            assert response_data["code"] == 200
            assert response_data["data"] == "Mensaje Enviado"
    
    @pytest.mark.asyncio
    async def test_post_form_data_error(self, http_client, error_response_data):
        """Test POST request with error response"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock response
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_response.content_type = 'application/json'
            mock_response.json = AsyncMock(return_value=error_response_data)
            
            # Mock session
            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value.__aenter__.return_value = mock_response
            mock_session.return_value = mock_session_instance
            
            # Test request
            status_code, response_data = await http_client.post_form_data(
                url="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                data={"Message": "Test message", "Url": "https://example.com"},
                headers={"x-api-key": "invalid-key"}
            )
            
            # Assertions
            assert status_code == 401
            assert response_data == error_response_data
            assert response_data["code"] == 401
            assert response_data["exception"] == "The apikey don't correct"
    
    @pytest.mark.asyncio
    async def test_post_form_data_retry_on_server_error(self, http_client):
        """Test retry logic on server errors"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock responses: first 500, then 200
            mock_response_500 = AsyncMock()
            mock_response_500.status = 500
            mock_response_500.content_type = 'application/json'
            mock_response_500.json = AsyncMock(return_value={"error": "Internal Server Error"})
            
            mock_response_200 = AsyncMock()
            mock_response_200.status = 200
            mock_response_200.content_type = 'application/json'
            mock_response_200.json = AsyncMock(return_value={"success": True})
            
            # Mock session with retry behavior
            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value.__aenter__.side_effect = [
                mock_response_500, mock_response_200
            ]
            mock_session.return_value = mock_session_instance
            
            # Test request
            status_code, response_data = await http_client.post_form_data(
                url="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                data={"Message": "Test message", "Url": "https://example.com"}
            )
            
            # Should succeed after retry
            assert status_code == 200
            assert response_data["success"] is True
    
    @pytest.mark.asyncio
    async def test_post_form_data_no_retry_on_client_error(self, http_client):
        """Test that client errors (4xx) are not retried"""
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock 400 response
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.content_type = 'application/json'
            mock_response.json = AsyncMock(return_value={"error": "Bad Request"})
            
            # Mock session
            mock_session_instance = AsyncMock()
            mock_session_instance.post.return_value.__aenter__.return_value = mock_response
            mock_session.return_value = mock_session_instance
            
            # Test request
            status_code, response_data = await http_client.post_form_data(
                url="https://api-com-notifications.mobzilla.com/api/Telegram/SendMessage",
                data={"Message": "Test message", "Url": "https://example.com"}
            )
            
            # Should not retry on 400
            assert status_code == 400
            assert response_data["error"] == "Bad Request"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, http_client):
        """Test HTTP client as context manager"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value = mock_session_instance
            
            async with http_client as client:
                assert client == http_client
            
            # Should close session
            mock_session_instance.close.assert_called_once() 