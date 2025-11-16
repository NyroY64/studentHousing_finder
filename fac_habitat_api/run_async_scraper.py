#!/usr/bin/env python3
"""Main entry point for running the async scraper."""

import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers.async_scraper import AsyncScraper

if __name__ == "__main__":
    scraper = AsyncScraper()
    asyncio.run(scraper.run())
