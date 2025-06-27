#!/usr/bin/env python3
"""
X Feed Monitor - Main Entry Point
"""
import asyncio
import nest_asyncio

from src.core.monitor import XMonitor

# Allow async code to run in Jupyter notebooks if needed
nest_asyncio.apply()


async def main():
    """Main application entry point"""
    monitor = XMonitor()
    await monitor.start()


if __name__ == "__main__":
    asyncio.run(main()) 