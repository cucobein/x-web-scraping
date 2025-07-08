"""
Service Provider Instance Module

This module provides a singleton instance of ServiceProvider that can be imported
and used throughout the application for dependency injection.
"""

from .service_provider import ServiceProvider

# Module-level singleton instance
_service_provider = ServiceProvider()


def get_service_provider() -> ServiceProvider:
    """
    Get the singleton ServiceProvider instance.

    Returns:
        ServiceProvider: The singleton instance
    """
    return _service_provider
