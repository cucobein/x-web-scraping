"""Unit tests for EnvironmentService"""

import os
from unittest.mock import patch

import pytest

from src.services.environment_service import EnvironmentService
from src.utils.env_helper import get_environment


class TestEnvironmentService:
    """Test EnvironmentService functionality"""

    def test_get_environment_returns_same_as_helper(self):
        """Test that EnvironmentService returns the same value as get_environment()"""
        # Arrange
        env_service = EnvironmentService()
        
        # Act
        service_env = env_service.get_environment()
        helper_env = get_environment()
        
        # Assert
        assert service_env == helper_env

    def test_is_development_returns_correct_value(self):
        """Test is_development() method"""
        # Arrange
        env_service = EnvironmentService()
        
        # Act & Assert
        if env_service.get_environment() == "dev":
            assert env_service.is_development() is True
            assert env_service.is_production() is False
        else:
            assert env_service.is_development() is False
            assert env_service.is_production() is True

    def test_is_production_returns_correct_value(self):
        """Test is_production() method"""
        # Arrange
        env_service = EnvironmentService()
        
        # Act & Assert
        if env_service.get_environment() == "prod":
            assert env_service.is_production() is True
            assert env_service.is_development() is False
        else:
            assert env_service.is_production() is False
            assert env_service.is_development() is True

    def test_environment_property(self):
        """Test environment property"""
        # Arrange
        env_service = EnvironmentService()
        
        # Act
        env_property = env_service.environment
        env_method = env_service.get_environment()
        
        # Assert
        assert env_property == env_method

    @patch.dict(os.environ, {"ENVIRONMENT": "dev"})
    def test_with_dev_environment(self):
        """Test with dev environment set"""
        # Arrange & Act
        env_service = EnvironmentService()
        
        # Assert
        assert env_service.get_environment() == "dev"
        assert env_service.is_development() is True
        assert env_service.is_production() is False

    @patch.dict(os.environ, {"ENVIRONMENT": "prod"})
    def test_with_prod_environment(self):
        """Test with prod environment set"""
        # Arrange & Act
        env_service = EnvironmentService()
        
        # Assert
        assert env_service.get_environment() == "prod"
        assert env_service.is_production() is True
        assert env_service.is_development() is False

    def test_singleton_behavior(self):
        """Test that EnvironmentService can be used as singleton"""
        # Arrange & Act
        env_service1 = EnvironmentService()
        env_service2 = EnvironmentService()
        
        # Assert
        assert env_service1.get_environment() == env_service2.get_environment() 