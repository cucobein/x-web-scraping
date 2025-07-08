"""
Unit tests for EnvironmentService
"""

import os

from src.services.environment_service import EnvironmentService


class TestEnvironmentService:
    """Test EnvironmentService functionality"""

    def test_get_environment_returns_default_when_not_set(self):
        """Test that EnvironmentService returns default environment when ENVIRONMENT not set"""
        # Clear environment variable
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        
        env_service = EnvironmentService()
        assert env_service.get_environment() == "dev"

    def test_is_development_returns_correct_value(self):
        """Test is_development method"""
        env_service = EnvironmentService()
        if env_service.get_environment() == "dev":
            assert env_service.is_development() is True
            assert env_service.is_production() is False
        else:
            assert env_service.is_development() is False
            assert env_service.is_production() is True

    def test_is_production_returns_correct_value(self):
        """Test is_production method"""
        env_service = EnvironmentService()
        if env_service.get_environment() == "prod":
            assert env_service.is_production() is True
            assert env_service.is_development() is False
        else:
            assert env_service.is_production() is False
            assert env_service.is_development() is True

    def test_environment_property(self):
        """Test environment property"""
        env_service = EnvironmentService()
        env_method = env_service.get_environment()
        env_property = env_service.environment
        
        assert env_method == env_property

    def test_with_dev_environment(self):
        """Test with dev environment set"""
        os.environ["ENVIRONMENT"] = "dev"
        env_service = EnvironmentService()
        
        assert env_service.get_environment() == "dev"
        assert env_service.is_development() is True
        assert env_service.is_production() is False

    def test_with_prod_environment(self):
        """Test with prod environment set"""
        os.environ["ENVIRONMENT"] = "prod"
        env_service = EnvironmentService()
        
        assert env_service.get_environment() == "prod"
        assert env_service.is_production() is True
        assert env_service.is_development() is False

    def test_singleton_behavior(self):
        """Test that multiple instances return the same environment value"""
        env_service1 = EnvironmentService()
        env_service2 = EnvironmentService()
        
        assert env_service1.get_environment() == env_service2.get_environment() 