#!/usr/bin/env python3
"""
X Feed Monitor - Main Entry Point
"""
import asyncio

import nest_asyncio
from dotenv import load_dotenv

from src.core.monitor import XMonitor
from src.services.logger_service import LoggerService
from src.services.environment_service import EnvironmentService
from src.services.service_registration import setup_services

# Load environment variables from .env file
load_dotenv()

# Allow async code to run in Jupyter notebooks if needed
nest_asyncio.apply()


async def main():
    """Main application entry point"""
    # Setup centralized logging and get provider
    provider = setup_services()
    logger = provider.get(LoggerService)
    
    # Log application startup
    env_service = provider.get(EnvironmentService)
    environment = env_service.get_environment()
    logger.info(
        "Application starting", {"environment": environment, "log_file": "logs/app.log"}
    )

    try:
        monitor = XMonitor(provider=provider)
        await monitor.start()
    except Exception as e:
        logger.log_exception("Application failed to start", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
