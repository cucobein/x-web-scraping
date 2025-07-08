"""Unit tests for ServiceProvider"""

import threading
import time
from unittest.mock import Mock

import pytest

from src.services.service_provider import ServiceProvider


class TestService:
    """Test service class"""
    def __init__(self, value: str = "default"):
        self.value = value


class TestServiceProvider:
    """Test ServiceProvider functionality"""

    def setup_method(self):
        """Reset service provider before each test"""
        self.provider = ServiceProvider()

    def test_register_singleton(self):
        """Test registering a singleton service"""
        # Arrange
        factory = lambda: TestService("test_value")
        
        # Act
        self.provider.register_singleton(TestService, factory)
        
        # Assert
        assert self.provider.is_registered(TestService)
        assert not self.provider.is_registered(str)  # Different type

    def test_get_singleton_returns_same_instance(self):
        """Test that get() returns the same instance for singletons"""
        # Arrange
        factory = lambda: TestService("test_value")
        self.provider.register_singleton(TestService, factory)
        
        # Act
        instance1 = self.provider.get(TestService)
        instance2 = self.provider.get(TestService)
        
        # Assert
        assert instance1 is instance2
        assert instance1.value == "test_value"

    def test_create_new_returns_different_instances(self):
        """Test that create_new() returns different instances"""
        # Arrange
        factory = lambda: TestService("test_value")
        self.provider.register_singleton(TestService, factory)
        
        # Act
        instance1 = self.provider.create_new(TestService)
        instance2 = self.provider.create_new(TestService)
        
        # Assert
        assert instance1 is not instance2
        assert instance1.value == "test_value"
        assert instance2.value == "test_value"

    def test_get_unregistered_service_raises_keyerror(self):
        """Test that getting unregistered service raises KeyError"""
        # Act & Assert
        with pytest.raises(KeyError, match="TestService not registered"):
            self.provider.get(TestService)

    def test_create_new_unregistered_service_raises_keyerror(self):
        """Test that creating unregistered service raises KeyError"""
        # Act & Assert
        with pytest.raises(KeyError, match="TestService not registered"):
            self.provider.create_new(TestService)

    def test_is_registered(self):
        """Test is_registered method"""
        # Arrange
        factory = lambda: TestService()
        
        # Act & Assert
        assert not self.provider.is_registered(TestService)
        
        self.provider.register_singleton(TestService, factory)
        assert self.provider.is_registered(TestService)

    def test_clear_removes_all_services(self):
        """Test that clear() removes all registered services"""
        # Arrange
        factory = lambda: TestService()
        self.provider.register_singleton(TestService, factory)
        
        # Act
        self.provider.clear()
        
        # Assert
        assert not self.provider.is_registered(TestService)
        with pytest.raises(KeyError):
            self.provider.get(TestService)

    def test_thread_safety_singleton_creation(self):
        """Test that singleton creation is thread-safe"""
        # Arrange
        call_count = 0
        
        def factory():
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate slow initialization
            return TestService(f"instance_{call_count}")
        
        self.provider.register_singleton(TestService, factory)
        
        # Act - Create multiple threads trying to get the service simultaneously
        results = []
        
        def get_service():
            results.append(self.provider.get(TestService))
        
        threads = [threading.Thread(target=get_service) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Assert - Only one instance should be created
        assert call_count == 1
        assert len(set(id(result) for result in results)) == 1
        assert all(result.value == "instance_1" for result in results)

    def test_thread_safety_create_new(self):
        """Test that create_new is thread-safe"""
        # Arrange
        call_count = 0
        
        def factory():
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate slow initialization
            return TestService(f"instance_{call_count}")
        
        self.provider.register_singleton(TestService, factory)
        
        # Act - Create multiple threads trying to create new instances simultaneously
        results = []
        
        def create_new_service():
            results.append(self.provider.create_new(TestService))
        
        threads = [threading.Thread(target=create_new_service) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # Assert - Each call should create a new instance
        assert call_count == 5
        assert len(set(id(result) for result in results)) == 5
        assert len(set(result.value for result in results)) == 5

    def test_multiple_service_types(self):
        """Test handling multiple different service types"""
        # Arrange
        class ServiceA:
            def __init__(self): self.name = "A"
        
        class ServiceB:
            def __init__(self): self.name = "B"
        
        self.provider.register_singleton(ServiceA, lambda: ServiceA())
        self.provider.register_singleton(ServiceB, lambda: ServiceB())
        
        # Act
        service_a = self.provider.get(ServiceA)
        service_b = self.provider.get(ServiceB)
        
        # Assert
        assert service_a.name == "A"
        assert service_b.name == "B"
        assert service_a is not service_b
        assert self.provider.is_registered(ServiceA)
        assert self.provider.is_registered(ServiceB) 