"""Python-specific scraper implementations."""

from .vedicheritage_scraper import VedicHeritageScraper
from .gretil_scraper import GretilScraper
from .ambuda_scraper import AmbudaScraper
from .pdf_extractor import PDFExtractor

__all__ = [
    "VedicHeritageScraper",
    "GretilScraper", 
    "AmbudaScraper",
    "PDFExtractor",
]
