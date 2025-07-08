# Services package

from .service_provider import ServiceProvider
from .service_provider_instance import get_service_provider

__all__ = ["ServiceProvider", "get_service_provider"]
