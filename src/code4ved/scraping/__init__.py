"""Code4Ved Web Scraping Module.

This module provides comprehensive web scraping capabilities for extracting
Vedic texts from multiple Sanskrit repositories with ethical scraping practices.
"""

from .base import BaseScraper
from .models import (
    ScrapedContent,
    ScrapingTask,
    ScrapingResult,
    TextFormat,
    SourceMetadata,
    ScrapingStatus,
)
from .config import ScrapingConfig, get_default_config
from .storage import FileSystemStorage
from .orchestrator import ScrapingOrchestrator

__version__ = "0.1.0"
__all__ = [
    "BaseScraper",
    "ScrapedContent",
    "ScrapingTask", 
    "ScrapingResult",
    "TextFormat",
    "SourceMetadata",
    "ScrapingStatus",
    "ScrapingConfig",
    "get_default_config",
    "FileSystemStorage",
    "ScrapingOrchestrator",
]
