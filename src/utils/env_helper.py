"""
Environment detection helper
"""
import os
from typing import Literal

EnvironmentType = Literal["dev", "prod"]


def get_environment() -> EnvironmentType:
    """
    Get the current environment from ENVIRONMENT env var
    
    Returns:
        Environment type: "dev" or "prod"
        
    Defaults to "dev" if not set
    """
    env = os.getenv("ENVIRONMENT", "dev").lower()
    
    if env not in ["dev", "prod"]:
        print(f"⚠️ Invalid ENVIRONMENT value: {env}. Defaulting to 'dev'")
        return "dev"
    
    return env


def is_development() -> bool:
    """Check if running in development environment"""
    return get_environment() == "dev"


def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == "prod" 