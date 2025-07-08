"""Unit tests for service registration"""

import pytest

from src.services import get_service_provider
from src.services.service_registration import register_core_services
from src.services.logger_service import LoggerService
from src.services.firebase_log_service import FirebaseLogService
from src.config.config_manager import ConfigManager, ConfigMode


class TestServiceRegistration:
    """Test service registration functionality"""

    def setup_method(self):
        """Reset service provider before each test"""
        self.provider = get_service_provider()
        self.provider.clear()

    def test_register_core_services(self):
        """Test that core services are registered correctly"""
        # Act
        register_core_services()
        
        # Assert
        assert self.provider.is_registered(LoggerService)
        assert self.provider.is_registered(FirebaseLogService)

    def test_logger_service_singleton(self):
        """Test that LoggerService is properly registered as singleton"""
        # Arrange
        register_core_services()
        
        # Act
        logger1 = self.provider.get(LoggerService)
        logger2 = self.provider.get(LoggerService)
        
        # Assert
        assert logger1 is logger2
        assert isinstance(logger1, LoggerService)

    def test_firebase_log_service_singleton(self):
        """Test that FirebaseLogService is properly registered as singleton"""
        # Arrange
        register_core_services()
        
        # Act
        firebase1 = self.provider.get(FirebaseLogService)
        firebase2 = self.provider.get(FirebaseLogService)
        
        # Assert
        assert firebase1 is firebase2
        assert isinstance(firebase1, FirebaseLogService)

    def test_configurable_registration_with_fixture_mode(self):
        """Test that services can be registered with FIXTURE mode for testing"""
        # Arrange
        register_core_services(ConfigMode.FIXTURE)
        
        # Act
        config_manager = self.provider.get(ConfigManager)
        
        # Assert
        assert config_manager.mode == ConfigMode.FIXTURE
        assert isinstance(config_manager, ConfigManager)

    def test_configurable_registration_with_firebase_mode(self):
        """Test that services can be registered with FIREBASE mode for production"""
        # Arrange
        register_core_services(ConfigMode.FIREBASE)
        
        # Act
        config_manager = self.provider.get(ConfigManager)
        
        # Assert
        assert config_manager.mode == ConfigMode.FIREBASE
        assert isinstance(config_manager, ConfigManager) 