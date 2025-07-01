"""
Unit tests for HTTP client service
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.http_client import HttpClient


class TestHttpClient:
    """Test HTTP client functionality"""
    
    @pytest.fixture
    def http_client(self):
        """Create HTTP client instance"""
        return HttpClient(timeout=5, max_retries=2, retry_delay=0.1)
    
    @pytest.mark.asyncio
    async def test_successful_post_request(self, http_client):
        """Test that successful POST request returns correct status and data"""
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.content_type = 'application/json'
        mock_response.json = AsyncMock(return_value={"success": True, "message": "OK"})
        
        # Create a mock context manager that returns our response
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        # Create a mock session that returns our context manager
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_context)
        
        # Mock the _get_session method to return our mock session
        with patch.object(http_client, '_get_session', return_value=mock_session):
            status_code, response_data = await http_client.post_form_data(
                url="https://api.example.com/test",
                data={"key": "value"},
                headers={"Authorization": "Bearer test-token"}
            )
            
            # Verify results
            assert status_code == 200
            assert response_data == {"success": True, "message": "OK"}
            
            # Verify the session.post was called
            mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_http_error_response(self, http_client):
        """Test handling of HTTP error responses"""
        # Create a mock response object for 404 error
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.content_type = 'application/json'
        mock_response.json = AsyncMock(return_value={"error": "Not Found"})
        
        # Create a mock context manager that returns our response
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        # Create a mock session that returns our context manager
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_context)
        
        # Mock the _get_session method to return our mock session
        with patch.object(http_client, '_get_session', return_value=mock_session):
            status_code, response_data = await http_client.post_form_data(
                url="https://api.example.com/test",
                data={"key": "value"}
            )
            
            # Should return error status without retrying
            assert status_code == 404
            assert response_data == {"error": "Not Found"}
    
    @pytest.mark.asyncio
    async def test_server_error_with_retry(self, http_client):
        """Test retry logic for server errors"""
        # Create mock responses: first 500, then 200
        mock_error_response = MagicMock()
        mock_error_response.status = 500
        mock_error_response.content_type = 'application/json'
        mock_error_response.json = AsyncMock(return_value={"error": "Internal Server Error"})

        mock_success_response = MagicMock()
        mock_success_response.status = 200
        mock_success_response.content_type = 'application/json'
        mock_success_response.json = AsyncMock(return_value={"success": True})

        # Create a mock context manager that returns our responses in sequence
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(side_effect=[mock_error_response, mock_success_response])
        mock_context.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session that returns our context manager
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_context)

        # Patch asyncio.sleep to avoid real delays
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Mock the _get_session method to return our mock session
            with patch.object(http_client, '_get_session', return_value=mock_session):
                status_code, response_data = await http_client.post_form_data(
                    url="https://api.example.com/test",
                    data={"key": "value"}
                )
                # Should succeed after retry
                assert status_code == 200
                assert response_data == {"success": True}
                # Should have retried once
                assert mock_session.post.call_count == 2
                assert mock_sleep.call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limit_retry(self, http_client):
        """Test retry logic for rate limit (429) errors"""
        # Create mock responses: first 429, then 200
        mock_rate_limit_response = MagicMock()
        mock_rate_limit_response.status = 429
        mock_rate_limit_response.content_type = 'application/json'
        mock_rate_limit_response.json = AsyncMock(return_value={"error": "Rate Limited"})

        mock_success_response = MagicMock()
        mock_success_response.status = 200
        mock_success_response.content_type = 'application/json'
        mock_success_response.json = AsyncMock(return_value={"success": True})

        # Create a mock context manager that returns our responses in sequence
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(side_effect=[mock_rate_limit_response, mock_success_response])
        mock_context.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session that returns our context manager
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_context)

        # Patch asyncio.sleep to avoid real delays
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Mock the _get_session method to return our mock session
            with patch.object(http_client, '_get_session', return_value=mock_session):
                status_code, response_data = await http_client.post_form_data(
                    url="https://api.example.com/test",
                    data={"key": "value"}
                )
                # Should succeed after retry
                assert status_code == 200
                assert response_data == {"success": True}
                # Should have retried once
                assert mock_session.post.call_count == 2
                assert mock_sleep.call_count == 1

    @pytest.mark.asyncio
    async def test_timeout_error_with_retry(self, http_client):
        """Test retry logic for timeout errors"""
        # Create a mock context manager that raises TimeoutError on __aenter__
        mock_context = MagicMock()
        mock_context.__aenter__ = AsyncMock(side_effect=[
            Exception('Timeout'), Exception('Timeout'), Exception('Timeout')
        ])
        mock_context.__aexit__ = AsyncMock(return_value=None)

        # Create a mock session that returns our context manager
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_context)

        # Patch asyncio.sleep to avoid real delays
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Mock the _get_session method to return our mock session
            with patch.object(http_client, '_get_session', return_value=mock_session):
                # Should raise after all retries
                with pytest.raises(Exception, match='Timeout'):
                    await http_client.post_form_data(
                        url="https://api.example.com/test",
                        data={"key": "value"}
                    )
                # Should have retried max_retries times (2 retries + 1 initial = 3 calls)
                assert mock_session.post.call_count == 3
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_context_manager(self, http_client):
        """Test HTTP client as context manager"""
        # Create a mock session with a close method
        mock_session = MagicMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()

        # Set the internal _session so close() will use it
        http_client._session = mock_session

        # Mock the _get_session method to return our mock session
        with patch.object(http_client, '_get_session', return_value=mock_session):
            async with http_client as client:
                assert client == http_client
            # Should close session
            mock_session.close.assert_called_once() 