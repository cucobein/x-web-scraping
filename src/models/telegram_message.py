"""
Telegram message models for notification requests and responses
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TelegramMessageRequest:
    """Request model for Telegram message endpoint"""
    
    message: str
    url: str
    
    def to_form_data(self) -> Dict[str, str]:
        """Convert to form data format expected by the endpoint"""
        return {
            "Message": self.message,
            "Url": self.url
        }


@dataclass
class TelegramMessageResponse:
    """Response model for Telegram message endpoint"""
    
    status_code: int
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_response(cls, status_code: int, response_data: Dict[str, Any]) -> 'TelegramMessageResponse':
        """
        Create response object from HTTP response
        
        Args:
            status_code: HTTP status code
            response_data: Response JSON data
            
        Returns:
            TelegramMessageResponse object
        """
        success = 200 <= status_code < 300
        
        # Handle structured response format
        if response_data:
            # Extract fields from structured response
            message = response_data.get('message') or response_data.get('Message')
            error = response_data.get('exception') or response_data.get('error') or response_data.get('Error')
            data = response_data.get('data') or response_data.get('Data')
        else:
            # Fallback for non-structured responses
            message = response_data.get('message') or response_data.get('Message')
            error = response_data.get('error') or response_data.get('Error')
            data = None
        
        return cls(
            status_code=status_code,
            success=success,
            message=message,
            error=error,
            data=data,
            raw_data=response_data
        )
    
    @classmethod
    def from_error(cls, status_code: int, error_message: str) -> 'TelegramMessageResponse':
        """
        Create error response object
        
        Args:
            status_code: HTTP status code
            error_message: Error message
            
        Returns:
            TelegramMessageResponse object
        """
        return cls(
            status_code=status_code,
            success=False,
            error=error_message
        ) 