"""
Example usage of the robust LoggerService
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.logger_service import LoggerService, LogLevel


def example_usage():
    """Example of how to use the LoggerService"""
    
    # Initialize logger
    logger = LoggerService(log_file_path="logs/app.log")
    
    # Different log levels
    logger.debug("Debug information", {"config_mode": "local"})
    logger.info("Application started")
    logger.warning("Rate limit approaching", {"domain": "x.com", "requests": 45})
    
    # Error logging
    try:
        # Simulate an error
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_exception("An error occurred", e, {"component": "example"})
    
    # Critical error
    logger.critical("Database connection lost", {
        "database": "local",
        "retry_attempts": 3
    })
    
    # Simple logging without context
    logger.info("Monitoring cycle completed")


if __name__ == "__main__":
    example_usage() 