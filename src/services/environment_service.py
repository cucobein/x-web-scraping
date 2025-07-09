"""
Environment Service

Provides environment information as a service, allowing other services to get
environment data through dependency injection instead of direct function calls.
"""

import os
from typing import Literal

EnvironmentType = Literal["dev", "prod"]


class EnvironmentService:
    """Service for providing environment information"""

    @staticmethod
    def get_default_environment() -> EnvironmentType:
        """Get the default environment value"""
        return os.getenv("ENVIRONMENT", "dev")  # type: ignore[return-value]

    def __init__(self) -> None:
        """Initialize with current environment"""
        self._environment = self.get_default_environment()

    def get_environment(self) -> EnvironmentType:
        """
        Get the current environment

        Returns:
            Environment type: "dev" or "prod"
        """
        return self._environment

    def is_development(self) -> bool:
        """
        Check if running in development environment

        Returns:
            True if development, False otherwise
        """
        return self._environment == "dev"

    def is_production(self) -> bool:
        """
        Check if running in production environment

        Returns:
            True if production, False otherwise
        """
        return self._environment == "prod"

    @property
    def environment(self) -> EnvironmentType:
        """
        Get environment as property

        Returns:
            Current environment
        """
        return self._environment
