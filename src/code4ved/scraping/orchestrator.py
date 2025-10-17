"""Orchestration layer for multi-language scraper coordination."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from .base import BaseScraper
from .config import ScrapingConfig, get_default_config
from .models import ScrapedContent, ScrapingResult, ScrapingStatus, ScrapingTask
from .storage import FileSystemStorage
from .python import (
    VedicHeritageScraper, GretilScraper, AmbudaScraper,
    SanskritDocumentsScraper, VedPuranScraper, VeducationScraper,
    IgncaScraper, SanskritEbooksScraper, SanskritLinguisticsScraper,
    SanskritLibraryScraper, TitusScraper, TemplePurohitScraper,
    VyasaOnlineScraper, GitaSupersiteScraper, AdhyetaScraper
)


class ScrapingOrchestrator:
    """Orchestrates multiple scrapers and manages scraping operations."""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        """Initialize orchestrator.
        
        Args:
            config: Scraping configuration
        """
        self.config = config or get_default_config()
        self.storage = FileSystemStorage(self.config)
        self.console = Console()
        
        # Setup logging
        self.logger = logging.getLogger("orchestrator")
        
        # Initialize scrapers
        self.scrapers: Dict[str, BaseScraper] = {}
        self._initialize_scrapers()
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'total_urls': 0,
            'successful_urls': 0,
            'failed_urls': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _initialize_scrapers(self) -> None:
        """Initialize available scrapers."""
        # Original scrapers
        try:
            self.scrapers['vedicheritage'] = VedicHeritageScraper(self.config)
            self.logger.info("Initialized Vedic Heritage scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Vedic Heritage scraper: {e}")
        
        try:
            self.scrapers['gretil'] = GretilScraper(self.config)
            self.logger.info("Initialized GRETIL scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize GRETIL scraper: {e}")
        
        try:
            self.scrapers['ambuda'] = AmbudaScraper(self.config)
            self.logger.info("Initialized Ambuda scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Ambuda scraper: {e}")
        
        # New scrapers
        try:
            self.scrapers['sanskritdocuments'] = SanskritDocumentsScraper(self.config)
            self.logger.info("Initialized Sanskrit Documents scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Sanskrit Documents scraper: {e}")
        
        try:
            self.scrapers['vedpuran'] = VedPuranScraper(self.config)
            self.logger.info("Initialized VedPuran scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize VedPuran scraper: {e}")
        
        try:
            self.scrapers['veducation'] = VeducationScraper(self.config)
            self.logger.info("Initialized Veducation scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Veducation scraper: {e}")
        
        try:
            self.scrapers['ignca'] = IgncaScraper(self.config)
            self.logger.info("Initialized IGNCA scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize IGNCA scraper: {e}")
        
        try:
            self.scrapers['sanskritebooks'] = SanskritEbooksScraper(self.config)
            self.logger.info("Initialized Sanskrit E-books scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Sanskrit E-books scraper: {e}")
        
        try:
            self.scrapers['sanskritlinguistics'] = SanskritLinguisticsScraper(self.config)
            self.logger.info("Initialized Sanskrit Linguistics scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Sanskrit Linguistics scraper: {e}")
        
        try:
            self.scrapers['sanskritlibrary'] = SanskritLibraryScraper(self.config)
            self.logger.info("Initialized Sanskrit Library scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Sanskrit Library scraper: {e}")
        
        try:
            self.scrapers['titus'] = TitusScraper(self.config)
            self.logger.info("Initialized TITUS scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize TITUS scraper: {e}")
        
        try:
            self.scrapers['templepurohit'] = TemplePurohitScraper(self.config)
            self.logger.info("Initialized Temple Purohit scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Temple Purohit scraper: {e}")
        
        try:
            self.scrapers['vyasaonline'] = VyasaOnlineScraper(self.config)
            self.logger.info("Initialized Vyasa Online scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Vyasa Online scraper: {e}")
        
        try:
            self.scrapers['gitasupersite'] = GitaSupersiteScraper(self.config)
            self.logger.info("Initialized Gita Supersite scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Gita Supersite scraper: {e}")
        
        try:
            self.scrapers['adhyeta'] = AdhyetaScraper(self.config)
            self.logger.info("Initialized Adhyeta scraper")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Adhyeta scraper: {e}")
    
    async def scrape_source(self, source_name: str, 
                           urls: Optional[List[str]] = None,
                           max_pages: int = 100,
                           discover_urls: bool = True) -> List[ScrapingResult]:
        """Scrape content from a specific source.
        
        Args:
            source_name: Name of the source to scrape
            urls: List of URLs to scrape (if None, will discover URLs)
            max_pages: Maximum number of pages to scrape
            discover_urls: Whether to discover URLs automatically
            
        Returns:
            List of scraping results
        """
        if source_name not in self.scrapers:
            raise ValueError(f"Unknown source: {source_name}")
        
        scraper = self.scrapers[source_name]
        
        # Discover URLs if not provided
        if not urls and discover_urls:
            self.console.print(f"[blue]Discovering URLs from {source_name}...[/blue]")
            base_url = self.config.get_source_config(source_name).base_url
            urls = await scraper.discover_urls(base_url, max_pages)
            self.console.print(f"[green]Discovered {len(urls)} URLs[/green]")
        
        if not urls:
            self.console.print(f"[yellow]No URLs to scrape for {source_name}[/yellow]")
            return []
        
        # Create scraping task
        task = ScrapingTask(
            id=f"{source_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source=source_name,
            urls=urls[:max_pages],
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
            rate_limit=self.config.get_source_config(source_name).rate_limit
        )
        
        # Update statistics
        self.stats['total_tasks'] += 1
        self.stats['total_urls'] += len(task.urls)
        self.stats['start_time'] = datetime.now()
        
        # Execute scraping task
        self.console.print(f"[blue]Starting scraping task for {source_name}...[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task_progress = progress.add_task(f"Scraping {source_name}", total=len(task.urls))
            
            results = await scraper.scrape_task(task)
            
            # Update progress
            progress.update(task_progress, completed=len(results))
        
        # Store results
        await self._store_results(results)
        
        # Update statistics
        self._update_stats(results)
        
        self.console.print(f"[green]Completed scraping {source_name}: {len(results)} results[/green]")
        
        return results
    
    async def scrape_all_sources(self, max_pages_per_source: int = 100) -> Dict[str, List[ScrapingResult]]:
        """Scrape content from all available sources.
        
        Args:
            max_pages_per_source: Maximum pages per source
            
        Returns:
            Dictionary mapping source names to results
        """
        all_results = {}
        
        self.console.print("[blue]Starting scraping from all sources...[/blue]")
        
        # Create tasks for all sources
        tasks = []
        for source_name in self.scrapers.keys():
            task = asyncio.create_task(
                self.scrape_source(source_name, max_pages=max_pages_per_source)
            )
            tasks.append((source_name, task))
        
        # Execute all tasks concurrently
        for source_name, task in tasks:
            try:
                results = await task
                all_results[source_name] = results
            except Exception as e:
                self.logger.error(f"Failed to scrape {source_name}: {e}")
                all_results[source_name] = []
        
        self.console.print("[green]Completed scraping from all sources[/green]")
        
        return all_results
    
    async def _store_results(self, results: List[ScrapingResult]) -> None:
        """Store scraping results.
        
        Args:
            results: List of scraping results
        """
        for result in results:
            if result.content and result.status == ScrapingStatus.COMPLETED:
                try:
                    self.storage.store_content(result.content)
                except Exception as e:
                    self.logger.error(f"Failed to store content from {result.url}: {e}")
    
    def _update_stats(self, results: List[ScrapingResult]) -> None:
        """Update statistics.
        
        Args:
            results: List of scraping results
        """
        for result in results:
            if result.status == ScrapingStatus.COMPLETED:
                self.stats['successful_urls'] += 1
            else:
                self.stats['failed_urls'] += 1
        
        self.stats['end_time'] = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.stats.copy()
        
        # Add scraper-specific stats
        stats['scrapers'] = {}
        for name, scraper in self.scrapers.items():
            stats['scrapers'][name] = scraper.get_stats()
        
        # Add storage stats
        stats['storage'] = self.storage.get_storage_stats()
        
        # Calculate duration
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['duration_seconds'] = duration.total_seconds()
        else:
            stats['duration_seconds'] = 0
        
        return stats
    
    def print_stats(self) -> None:
        """Print statistics in a formatted table."""
        stats = self.get_stats()
        
        # Create main stats table
        table = Table(title="Scraping Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Tasks", str(stats['total_tasks']))
        table.add_row("Completed Tasks", str(stats['completed_tasks']))
        table.add_row("Failed Tasks", str(stats['failed_tasks']))
        table.add_row("Total URLs", str(stats['total_urls']))
        table.add_row("Successful URLs", str(stats['successful_urls']))
        table.add_row("Failed URLs", str(stats['failed_urls']))
        table.add_row("Duration (seconds)", f"{stats['duration_seconds']:.2f}")
        
        self.console.print(table)
        
        # Create scraper stats table
        if stats['scrapers']:
            scraper_table = Table(title="Scraper Statistics")
            scraper_table.add_column("Scraper", style="cyan")
            scraper_table.add_column("Requests Made", style="green")
            scraper_table.add_column("Successful", style="green")
            scraper_table.add_column("Failed", style="red")
            scraper_table.add_column("Rate Limited", style="yellow")
            
            for name, scraper_stats in stats['scrapers'].items():
                scraper_table.add_row(
                    name,
                    str(scraper_stats['stats']['requests_made']),
                    str(scraper_stats['stats']['successful_requests']),
                    str(scraper_stats['stats']['failed_requests']),
                    str(scraper_stats['stats']['rate_limited_requests'])
                )
            
            self.console.print(scraper_table)
        
        # Create storage stats table
        if stats['storage']:
            storage_table = Table(title="Storage Statistics")
            storage_table.add_column("Metric", style="cyan")
            storage_table.add_column("Value", style="green")
            
            storage_table.add_row("Total Files", str(stats['storage']['total_files']))
            storage_table.add_row("Total Size (bytes)", str(stats['storage']['total_size_bytes']))
            storage_table.add_row("Sources", str(len(stats['storage']['sources'])))
            storage_table.add_row("Formats", str(len(stats['storage']['formats'])))
            storage_table.add_row("Categories", str(len(stats['storage']['categories'])))
            
            self.console.print(storage_table)
    
    def list_available_sources(self) -> List[str]:
        """List available scraper sources.
        
        Returns:
            List of available source names
        """
        return list(self.scrapers.keys())
    
    def get_source_info(self, source_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Source information dictionary or None
        """
        if source_name not in self.scrapers:
            return None
        
        scraper = self.scrapers[source_name]
        source_config = self.config.get_source_config(source_name)
        
        return {
            'name': source_name,
            'scraper_type': type(scraper).__name__,
            'config': source_config.dict() if source_config else None,
            'stats': scraper.get_stats()
        }
    
    async def discover_urls(self, source_name: str, max_pages: int = 100) -> List[str]:
        """Discover URLs from a specific source.
        
        Args:
            source_name: Name of the source
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of discovered URLs
        """
        if source_name not in self.scrapers:
            raise ValueError(f"Unknown source: {source_name}")
        
        scraper = self.scrapers[source_name]
        base_url = self.config.get_source_config(source_name).base_url
        
        return await scraper.discover_urls(base_url, max_pages)
    
    def validate_content(self, content_path: Path) -> Dict[str, Any]:
        """Validate stored content.
        
        Args:
            content_path: Path to content file
            
        Returns:
            Validation result dictionary
        """
        try:
            content = self.storage.load_content(content_path)
            
            # Basic validation
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'content_info': {
                    'title': content.title,
                    'source': content.source,
                    'format': content.format,
                    'language': content.language,
                    'file_size': content.file_size,
                    'scraped_at': content.scraped_at
                }
            }
            
            # Check content quality
            if len(content.text) < self.config.min_text_length:
                validation_result['warnings'].append(f"Content too short: {len(content.text)} < {self.config.min_text_length}")
            
            if len(content.text) > self.config.max_text_length:
                validation_result['warnings'].append(f"Content too long: {len(content.text)} > {self.config.max_text_length}")
            
            if not content.title:
                validation_result['warnings'].append("Title is empty")
            
            if not content.url:
                validation_result['errors'].append("URL is empty")
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Failed to load content: {e}"],
                'warnings': [],
                'content_info': None
            }
    
    def cleanup_storage(self) -> int:
        """Clean up orphaned files in storage.
        
        Returns:
            Number of files removed
        """
        return self.storage.cleanup_orphaned_files()
    
    def export_content(self, output_path: Path, 
                      source: Optional[str] = None,
                      format_type: Optional[str] = None) -> None:
        """Export content to a different location.
        
        Args:
            output_path: Path to export to
            source: Filter by source
            format_type: Filter by format
        """
        self.storage.export_content(output_path, source, format_type)
    
    def get_duplicate_content(self) -> List[Dict[str, Any]]:
        """Get information about duplicate content.
        
        Returns:
            List of duplicate content information
        """
        return self.storage.get_duplicate_content()
    
    async def close(self) -> None:
        """Close orchestrator and cleanup resources."""
        for scraper in self.scrapers.values():
            scraper.close()
        
        self.logger.info("Orchestrator closed")
