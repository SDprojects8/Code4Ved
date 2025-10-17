#!/usr/bin/env python3
"""Example script demonstrating the web scraping module."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from code4ved.scraping import ScrapingOrchestrator, get_default_config
from code4ved.scraping.config import ScrapingConfig


async def main():
    """Main example function."""
    print("Code4Ved Web Scraping Module Example")
    print("=" * 40)
    
    # Create configuration
    config = get_default_config()
    print(f"Configuration loaded with {len(config.sources)} sources")
    
    # Create orchestrator
    orchestrator = ScrapingOrchestrator(config)
    print(f"Orchestrator created with {len(orchestrator.list_available_sources())} scrapers")
    
    # List available sources
    print("\nAvailable sources:")
    for source in orchestrator.list_available_sources():
        print(f"  - {source}")
    
    # Example: Discover URLs from a source
    print("\nDiscovering URLs from vedicheritage...")
    try:
        urls = await orchestrator.discover_urls("vedicheritage", max_pages=5)
        print(f"Discovered {len(urls)} URLs")
        for i, url in enumerate(urls[:3]):  # Show first 3
            print(f"  {i+1}. {url}")
        if len(urls) > 3:
            print(f"  ... and {len(urls) - 3} more")
    except Exception as e:
        print(f"Error discovering URLs: {e}")
    
    # Example: Scrape a single source
    print("\nScraping from vedicheritage (limited to 2 pages)...")
    try:
        results = await orchestrator.scrape_source("vedicheritage", max_pages=2)
        print(f"Scraping completed: {len(results)} results")
        
        successful = sum(1 for r in results if r.status.value == "completed")
        failed = len(results) - successful
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        
        # Show details of successful results
        for result in results:
            if result.status.value == "completed" and result.content:
                print(f"\n  Content: {result.content.title}")
                print(f"    URL: {result.content.url}")
                print(f"    Source: {result.content.source}")
                print(f"    Format: {result.content.format}")
                print(f"    Text length: {len(result.content.text)} characters")
                print(f"    Scraped at: {result.content.scraped_at}")
    except Exception as e:
        print(f"Error scraping: {e}")
    
    # Show statistics
    print("\nFinal Statistics:")
    stats = orchestrator.get_stats()
    print(f"  Total URLs processed: {stats['total_urls']}")
    print(f"  Successful: {stats['successful_urls']}")
    print(f"  Failed: {stats['failed_urls']}")
    
    # Show storage statistics
    storage_stats = stats.get('storage', {})
    if storage_stats:
        print(f"  Files stored: {storage_stats.get('total_files', 0)}")
        print(f"  Total size: {storage_stats.get('total_size_bytes', 0)} bytes")
    
    # Cleanup
    await orchestrator.close()
    print("\nExample completed!")


if __name__ == "__main__":
    asyncio.run(main())
