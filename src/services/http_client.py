"""
HTTP client service for making network requests
"""
import asyncio
import aiohttp
from typing import Dict, Any, Optional, Tuple
from aiohttp import ClientTimeout, FormData


class HttpClient:
    """Handles HTTP requests with proper error handling and retries"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize HTTP client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (will be exponential)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def post_form_data(
        self, 
        url: str, 
        data: Dict[str, str], 
        headers: Optional[Dict[str, str]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Send POST request with form data
        
        Args:
            url: Target URL
            data: Form data fields
            headers: Additional headers
            
        Returns:
            Tuple of (status_code, response_data)
        """
        session = await self._get_session()
        
        # Prepare form data
        form_data = FormData()
        for key, value in data.items():
            form_data.add_field(key, value)
        
        # Prepare headers
        request_headers = headers or {}
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                async with session.post(url, data=form_data, headers=request_headers) as response:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    if response.status < 400:
                        return response.status, response_data
                    else:
                        # Don't retry on client errors (4xx) except 429 (rate limit)
                        if 400 <= response.status < 500 and response.status != 429:
                            return response.status, response_data
                        
                        # Retry on server errors (5xx) and rate limits (429)
                        if attempt < self.max_retries:
                            delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                            await asyncio.sleep(delay)
                            continue
                        else:
                            return response.status, response_data
                            
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
                    
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
    
    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close() 