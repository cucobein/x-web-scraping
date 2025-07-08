#!/usr/bin/env python3
"""
X Feed Monitor - Main Entry Point
"""
import asyncio

import nest_asyncio

from src.core.monitor import XMonitor
from src.services.logger_service import LoggerService
from src.utils.env_helper import get_environment

# Allow async code to run in Jupyter notebooks if needed
nest_asyncio.apply()


def setup_logging():
    """Configure centralized logging for the application"""
    environment = get_environment()

    # Get the global logger instance
    logger = LoggerService.get_instance()

    logger.info(
        "Application starting", {"environment": environment, "log_file": "logs/app.log"}
    )

    return logger


async def main():
    """Main application entry point"""
    # Setup centralized logging
    logger = setup_logging()

    try:
        monitor = XMonitor()
        await monitor.start()
    except Exception as e:
        logger.log_exception("Application failed to start", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
