# Code4Ved Web Scraping Module

A comprehensive web scraping module for extracting Vedic texts from multiple Sanskrit repositories with ethical scraping practices.

## Features

- **Multi-Source Support**: Extract texts from 3 high-reliability Sanskrit repositories
- **Ethical Scraping**: Rate limiting, robots.txt compliance, and respectful user agents
- **Multi-Format Support**: HTML, PDF, plain text, XML, and JSON content extraction
- **Content Validation**: Quality checks and duplicate detection
- **Structured Storage**: Organized filesystem storage with metadata
- **Rich CLI**: Command-line interface with progress bars and statistics
- **Extensible Architecture**: Easy to add new scrapers and sources

## Supported Sources

1. **Vedic Heritage Portal** (vedicheritage.gov.in)
   - Government of India repository
   - HTML and PDF formats
   - Rate limit: 1 req/sec

2. **GRETIL** (gretil.sub.uni-goettingen.de)
   - Academic texts from University of Göttingen
   - HTML, plain text, and XML formats
   - Rate limit: 0.5 req/sec

3. **Ambuda** (ambuda.org)
   - Open source Sanskrit platform
   - HTML and JSON formats (API-first)
   - Rate limit: 1 req/sec

## Installation

The scraping module is part of the Code4Ved package. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

### Using the CLI

```bash
# List available sources
c4v scrape sources --all

# Discover URLs from a source
c4v scrape discover vedicheritage --max-pages 10

# Scrape from a specific source
c4v scrape scrape vedicheritage --max-pages 5

# Scrape from all sources
c4v scrape scrape-all --max-pages 10

# Show statistics
c4v scrape status

# Validate content
c4v scrape validate data/raw/vedicheritage/some_file.html

# Clean up orphaned files
c4v scrape cleanup
```

### Using the Python API

```python
import asyncio
from code4ved.scraping import ScrapingOrchestrator, get_default_config

async def main():
    # Create orchestrator
    orchestrator = ScrapingOrchestrator(get_default_config())
    
    # Scrape from a source
    results = await orchestrator.scrape_source("vedicheritage", max_pages=10)
    
    # Show results
    for result in results:
        if result.status.value == "completed":
            print(f"Scraped: {result.content.title}")
    
    # Cleanup
    await orchestrator.close()

asyncio.run(main())
```

## Configuration

The scraping module uses YAML configuration files. The default configuration is in `config/scraping.yaml`:

```yaml
# General settings
user_agent: "Code4Ved/1.0"
timeout: 30
max_retries: 3
respect_robots: true

# Rate limiting
default_rate_limit: 1.0
burst_size: 5

# Content filtering
min_text_length: 100
max_text_length: 1000000
allowed_formats: [html, pdf, plaintext, xml, json]

# Storage settings
storage_path: "data/raw"
create_directories: true
duplicate_detection: true
```

## Architecture

### Core Components

- **BaseScraper**: Abstract base class with common functionality
- **ScrapedContent**: Data model for scraped content
- **ScrapingTask**: Task management and progress tracking
- **FileSystemStorage**: Organized content storage
- **ScrapingOrchestrator**: Multi-scraper coordination

### Scrapers

- **VedicHeritageScraper**: BeautifulSoup-based HTML scraping
- **GretilScraper**: Academic text extraction with format detection
- **AmbudaScraper**: API-first approach with HTML fallback
- **PDFExtractor**: PyPDF2 and pdfminer.six integration

### Utilities

- **RateLimiter**: Token bucket and adaptive rate limiting
- **RobotsTxtParser**: robots.txt compliance checking
- **ContentValidator**: Quality validation and scoring
- **TextCleaner**: Text normalization and cleaning

## Storage Structure

Content is stored in an organized directory structure:

```
data/raw/
├── vedicheritage/
│   ├── Vedas/
│   │   ├── html/
│   │   │   ├── Rigveda_20250101_120000.html
│   │   │   └── Rigveda_20250101_120000_metadata.json
│   │   └── pdf/
│   └── Upanishads/
├── gretil/
│   ├── Sanskrit Literature/
│   │   └── plaintext/
└── ambuda/
    └── Sanskrit Literature/
        └── json/
```

## Error Handling

The module includes comprehensive error handling:

- **Rate Limiting**: Automatic retry with exponential backoff
- **Robots.txt Compliance**: Respects website crawling policies
- **Content Validation**: Quality checks and format validation
- **Network Errors**: Timeout and connection error handling
- **Storage Errors**: Duplicate detection and file system errors

## Performance

- **Concurrent Processing**: Multiple scrapers can run simultaneously
- **Rate Limiting**: Respects website resources and policies
- **Memory Efficient**: Streaming processing for large files
- **Progress Tracking**: Real-time progress bars and statistics

## Extending the Module

### Adding a New Scraper

1. Create a new scraper class inheriting from `BaseScraper`
2. Implement the `scrape_url` method
3. Add the scraper to the orchestrator
4. Update configuration with source metadata

```python
from code4ved.scraping.base import BaseScraper
from code4ved.scraping.models import ScrapedContent, TextFormat

class MyScraper(BaseScraper):
    async def scrape_url(self, url: str) -> ScrapedContent:
        # Implement scraping logic
        pass
```

### Adding a New Source

1. Add source configuration to `config/scraping.yaml`
2. Create scraper instance in orchestrator
3. Test with discovery and scraping commands

## Testing

Run the test suite:

```bash
pytest tests/test_scraping/
```

## Contributing

1. Follow the existing code style and patterns
2. Add tests for new functionality
3. Update documentation
4. Ensure ethical scraping practices

## License

This module is part of the Code4Ved project and follows the same MIT license.

## Support

For issues and questions:
- Check the documentation in `docs/scraping/`
- Review the example scripts in `examples/`
- Open an issue in the project repository
