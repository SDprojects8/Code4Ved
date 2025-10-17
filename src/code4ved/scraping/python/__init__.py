"""Python-specific scraper implementations."""

from .vedicheritage_scraper import VedicHeritageScraper
from .gretil_scraper import GretilScraper
from .ambuda_scraper import AmbudaScraper
from .pdf_extractor import PDFExtractor
from .sanskritdocuments_scraper import SanskritDocumentsScraper
from .vedpuran_scraper import VedPuranScraper
from .veducation_scraper import VeducationScraper
from .ignca_scraper import IgncaScraper
from .sanskritebooks_scraper import SanskritEbooksScraper
from .sanskritlinguistics_scraper import SanskritLinguisticsScraper
from .sanskritlibrary_scraper import SanskritLibraryScraper
from .titus_scraper import TitusScraper
from .templepurohit_scraper import TemplePurohitScraper
from .vyasaonline_scraper import VyasaOnlineScraper
from .gitasupersite_scraper import GitaSupersiteScraper
from .adhyeta_scraper import AdhyetaScraper

__all__ = [
    "VedicHeritageScraper",
    "GretilScraper", 
    "AmbudaScraper",
    "PDFExtractor",
    "SanskritDocumentsScraper",
    "VedPuranScraper",
    "VeducationScraper",
    "IgncaScraper",
    "SanskritEbooksScraper",
    "SanskritLinguisticsScraper",
    "SanskritLibraryScraper",
    "TitusScraper",
    "TemplePurohitScraper",
    "VyasaOnlineScraper",
    "GitaSupersiteScraper",
    "AdhyetaScraper",
]
