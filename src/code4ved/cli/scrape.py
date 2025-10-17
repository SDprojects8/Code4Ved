"""CLI commands for web scraping operations."""

import asyncio
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from ..scraping import ScrapingOrchestrator, get_default_config
from ..scraping.config import ScrapingConfig

app = typer.Typer(name="scrape", help="Web scraping operations")
console = Console()


@app.command()
def sources(
    list_all: bool = typer.Option(False, "--all", "-a", help="List all available sources")
) -> None:
    """List available scraping sources."""
    orchestrator = ScrapingOrchestrator()
    
    if list_all:
        # Show detailed information about all sources
        table = Table(title="Available Scraping Sources")
        table.add_column("Source", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Base URL", style="blue")
        table.add_column("Rate Limit", style="yellow")
        table.add_column("Max Pages", style="magenta")
        
        for source_name in orchestrator.list_available_sources():
            source_info = orchestrator.get_source_info(source_name)
            if source_info and source_info['config']:
                config = source_info['config']
                table.add_row(
                    source_name,
                    source_info['scraper_type'],
                    config['base_url'],
                    f"{config['rate_limit']} req/sec",
                    str(config['max_pages'])
                )
        
        console.print(table)
    else:
        # Show simple list
        sources = orchestrator.list_available_sources()
        console.print(f"Available sources: {', '.join(sources)}")


@app.command()
def discover(
    source: str = typer.Argument(..., help="Source name to discover URLs from"),
    max_pages: int = typer.Option(100, "--max-pages", "-m", help="Maximum pages to discover"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file to save URLs")
) -> None:
    """Discover URLs from a source without scraping."""
    async def _discover():
        orchestrator = ScrapingOrchestrator()
        
        try:
            console.print(f"[blue]Discovering URLs from {source}...[/blue]")
            urls = await orchestrator.discover_urls(source, max_pages)
            
            console.print(f"[green]Discovered {len(urls)} URLs[/green]")
            
            if output:
                output.write_text('\n'.join(urls))
                console.print(f"[green]URLs saved to {output}[/green]")
            else:
                # Show first 10 URLs
                for i, url in enumerate(urls[:10]):
                    console.print(f"{i+1}. {url}")
                
                if len(urls) > 10:
                    console.print(f"... and {len(urls) - 10} more URLs")
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
    
    asyncio.run(_discover())


@app.command()
def scrape(
    source: str = typer.Argument(..., help="Source name to scrape"),
    urls: Optional[List[str]] = typer.Option(None, "--url", "-u", help="Specific URLs to scrape"),
    max_pages: int = typer.Option(100, "--max-pages", "-m", help="Maximum pages to scrape"),
    discover: bool = typer.Option(True, "--discover/--no-discover", help="Discover URLs automatically"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for results")
) -> None:
    """Scrape content from a specific source."""
    async def _scrape():
        # Load configuration
        config = get_default_config()
        if output_dir:
            config.storage_path = output_dir
        
        orchestrator = ScrapingOrchestrator(config)
        
        try:
            console.print(f"[blue]Starting scraping from {source}...[/blue]")
            
            results = await orchestrator.scrape_source(
                source_name=source,
                urls=urls,
                max_pages=max_pages,
                discover_urls=discover
            )
            
            # Show results summary
            successful = sum(1 for r in results if r.status.value == "completed")
            failed = len(results) - successful
            
            console.print(f"[green]Scraping completed![/green]")
            console.print(f"  Successful: {successful}")
            console.print(f"  Failed: {failed}")
            console.print(f"  Total: {len(results)}")
            
            # Show statistics
            orchestrator.print_stats()
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        finally:
            await orchestrator.close()
    
    asyncio.run(_scrape())


@app.command()
def scrape_all(
    max_pages: int = typer.Option(100, "--max-pages", "-m", help="Maximum pages per source"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for results")
) -> None:
    """Scrape content from all available sources."""
    async def _scrape_all():
        # Load configuration
        config = get_default_config()
        if output_dir:
            config.storage_path = output_dir
        
        orchestrator = ScrapingOrchestrator(config)
        
        try:
            console.print("[blue]Starting scraping from all sources...[/blue]")
            
            all_results = await orchestrator.scrape_all_sources(max_pages)
            
            # Show results summary
            total_successful = 0
            total_failed = 0
            total_results = 0
            
            for source_name, results in all_results.items():
                successful = sum(1 for r in results if r.status.value == "completed")
                failed = len(results) - successful
                
                total_successful += successful
                total_failed += failed
                total_results += len(results)
                
                console.print(f"{source_name}: {successful} successful, {failed} failed")
            
            console.print(f"[green]All scraping completed![/green]")
            console.print(f"  Total successful: {total_successful}")
            console.print(f"  Total failed: {total_failed}")
            console.print(f"  Total results: {total_results}")
            
            # Show statistics
            orchestrator.print_stats()
        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)
        finally:
            await orchestrator.close()
    
    asyncio.run(_scrape_all())


@app.command()
def status(
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Specific source to check")
) -> None:
    """Show scraping status and statistics."""
    orchestrator = ScrapingOrchestrator()
    
    try:
        if source:
            # Show specific source status
            source_info = orchestrator.get_source_info(source)
            if not source_info:
                console.print(f"[red]Unknown source: {source}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[blue]Status for {source}:[/blue]")
            console.print(f"  Type: {source_info['scraper_type']}")
            console.print(f"  Config: {source_info['config']}")
            console.print(f"  Stats: {source_info['stats']}")
        else:
            # Show overall status
            orchestrator.print_stats()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate(
    content_path: Path = typer.Argument(..., help="Path to content file to validate")
) -> None:
    """Validate scraped content."""
    orchestrator = ScrapingOrchestrator()
    
    try:
        console.print(f"[blue]Validating content: {content_path}[/blue]")
        
        result = orchestrator.validate_content(content_path)
        
        if result['valid']:
            console.print("[green]Content is valid[/green]")
        else:
            console.print("[red]Content is invalid[/red]")
        
        if result['errors']:
            console.print("[red]Errors:[/red]")
            for error in result['errors']:
                console.print(f"  - {error}")
        
        if result['warnings']:
            console.print("[yellow]Warnings:[/yellow]")
            for warning in result['warnings']:
                console.print(f"  - {warning}")
        
        if result['content_info']:
            info = result['content_info']
            console.print(f"[blue]Content Info:[/blue]")
            console.print(f"  Title: {info['title']}")
            console.print(f"  Source: {info['source']}")
            console.print(f"  Format: {info['format']}")
            console.print(f"  Language: {info['language']}")
            console.print(f"  File Size: {info['file_size']} bytes")
            console.print(f"  Scraped At: {info['scraped_at']}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def cleanup() -> None:
    """Clean up orphaned files in storage."""
    orchestrator = ScrapingOrchestrator()
    
    try:
        console.print("[blue]Cleaning up orphaned files...[/blue]")
        
        removed_count = orchestrator.cleanup_storage()
        
        console.print(f"[green]Cleanup completed! Removed {removed_count} files[/green]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def duplicates() -> None:
    """Show duplicate content information."""
    orchestrator = ScrapingOrchestrator()
    
    try:
        console.print("[blue]Checking for duplicate content...[/blue]")
        
        duplicates = orchestrator.get_duplicate_content()
        
        if not duplicates:
            console.print("[green]No duplicate content found[/green]")
        else:
            console.print(f"[yellow]Found {len(duplicates)} duplicate groups[/yellow]")
            
            for i, duplicate_group in enumerate(duplicates):
                console.print(f"\n[blue]Duplicate Group {i+1}:[/blue]")
                console.print(f"  Hash: {duplicate_group['hash']}")
                console.print(f"  Count: {duplicate_group['count']}")
                console.print(f"  Items:")
                
                for item in duplicate_group['items']:
                    console.print(f"    - {item['title']} ({item['source']})")
                    console.print(f"      URL: {item['url']}")
                    console.print(f"      Path: {item['path']}")
                    console.print(f"      Scraped: {item['scraped_at']}")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def export(
    output_path: Path = typer.Argument(..., help="Output path for exported content"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Filter by source"),
    format_type: Optional[str] = typer.Option(None, "--format", "-f", help="Filter by format")
) -> None:
    """Export scraped content to a different location."""
    orchestrator = ScrapingOrchestrator()
    
    try:
        console.print(f"[blue]Exporting content to {output_path}...[/blue]")
        
        orchestrator.export_content(output_path, source, format_type)
        
        console.print("[green]Export completed![/green]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
