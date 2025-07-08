"""
Service Provider for dependency injection
"""

import threading
from typing import Any, Callable, Dict, Type, TypeVar

T = TypeVar("T")


class ServiceProvider:
    """Thread-safe service provider for dependency injection"""

    def __init__(self):
        self._singletons: Dict[type, Any] = {}
        self._factories: Dict[type, Callable] = {}
        self._lock = threading.RLock()

    def register_singleton(
        self, service_type: Type[T], factory: Callable[[], T]
    ) -> None:
        """
        Register a singleton service factory

        Args:
            service_type: The type of the service
            factory: Callable that creates the service instance
        """
        self._factories[service_type] = factory

    def get(self, service_type: Type[T]) -> T:
        """
        Get singleton instance (thread-safe)

        Args:
            service_type: The type of the service to retrieve

        Returns:
            The singleton instance of the service

        Raises:
            KeyError: If service type is not registered
        """
        if service_type not in self._singletons:
            with self._lock:
                if service_type not in self._singletons:
                    if service_type not in self._factories:
                        raise KeyError(
                            f"Service type {service_type.__name__} not registered"
                        )
                    self._singletons[service_type] = self._factories[service_type]()
        return self._singletons[service_type]

    def create_new(self, service_type: Type[T]) -> T:
        """
        Create new instance (for transient services)

        Args:
            service_type: The type of the service to create

        Returns:
            A new instance of the service

        Raises:
            KeyError: If service type is not registered
        """
        if service_type not in self._factories:
            raise KeyError(f"Service type {service_type.__name__} not registered")
        with self._lock:  # Thread-safe factory access
            return self._factories[service_type]()

    def is_registered(self, service_type: Type[T]) -> bool:
        """
        Check if a service type is registered

        Args:
            service_type: The type to check

        Returns:
            True if registered, False otherwise
        """
        return service_type in self._factories

    def clear(self) -> None:
        """Clear all registered services (useful for testing)"""
        with self._lock:
            self._singletons.clear()
            self._factories.clear()
