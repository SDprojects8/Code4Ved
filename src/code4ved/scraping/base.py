"""Base scraper class with common functionality."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ScrapingConfig
from .models import ScrapedContent, ScrapingResult, ScrapingStatus, ScrapingTask, TextFormat


class ScrapingError(Exception):
    """Base exception for scraping operations."""
    pass


class RateLimitError(ScrapingError):
    """Exception raised when rate limit is exceeded."""
    pass


class RobotsTxtError(ScrapingError):
    """Exception raised when robots.txt disallows scraping."""
    pass


class ContentValidationError(ScrapingError):
    """Exception raised when content validation fails."""
    pass


class BaseScraper(ABC):
    """Abstract base class for web scrapers.
    
    Provides common functionality including rate limiting, error handling,
    retry logic, and content validation.
    """
    
    def __init__(self, config: ScrapingConfig, source_name: str):
        """Initialize the scraper.
        
        Args:
            config: Scraping configuration
            source_name: Name of the source being scraped
        """
        self.config = config
        self.source_name = source_name
        self.source_config = config.get_source_config(source_name)
        
        if not self.source_config:
            raise ValueError(f"Source configuration not found: {source_name}")
        
        # Setup logging
        self.logger = logging.getLogger(f"scraper.{source_name}")
        
        # Setup HTTP session with retry strategy
        self.session = self._create_session()
        
        # Rate limiting
        self._last_request_time = 0.0
        self._rate_limit = self.source_config.rate_limit
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'robots_txt_blocks': 0,
            'validation_failures': 0,
        }
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Configure SSL verification
        session.verify = self.config.verify_ssl
        
        # Disable SSL warnings if requested
        if not self.config.ssl_warnings:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return session
    
    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        if self._rate_limit <= 0:
            return
        
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        min_interval = 1.0 / self._rate_limit
        
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if allowed, False if disallowed
        """
        if not self.config.respect_robots or not self.source_config.robots_txt_url:
            return True
        
        try:
            # Parse robots.txt URL
            robots_url = self.source_config.robots_txt_url
            response = self.session.get(robots_url, timeout=self.config.timeout)
            
            # Handle 404 (robots.txt doesn't exist) gracefully
            if response.status_code == 404:
                self.logger.debug(f"robots.txt not found at {robots_url}, allowing access")
                return True
            
            response.raise_for_status()
            
            # Simple robots.txt parsing (can be enhanced with robotparser)
            robots_content = response.text.lower()
            
            # Check for disallow rules
            user_agent = self.config.user_agent.lower()
            lines = robots_content.split('\n')
            
            in_user_agent_section = False
            for line in lines:
                line = line.strip()
                if line.startswith('user-agent:'):
                    agent = line.split(':', 1)[1].strip()
                    in_user_agent_section = agent == '*' or user_agent in agent
                elif in_user_agent_section and line.startswith('disallow:'):
                    disallow_path = line.split(':', 1)[1].strip()
                    if disallow_path and urlparse(url).path.startswith(disallow_path):
                        self.stats['robots_txt_blocks'] += 1
                        return False
            
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.logger.debug(f"robots.txt not found at {robots_url}, allowing access")
                return True
            else:
                self.logger.warning(f"HTTP error checking robots.txt: {e}")
                return True  # Allow if robots.txt check fails
        except Exception as e:
            self.logger.warning(f"Failed to check robots.txt: {e}")
            return True  # Allow if robots.txt check fails
    
    def _validate_content(self, content: ScrapedContent) -> bool:
        """Validate scraped content.
        
        Args:
            content: Content to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not self.config.validate_content:
            return True
        
        # Check text length
        if len(content.text) < self.config.min_text_length:
            self.logger.warning(f"Content too short: {len(content.text)} < {self.config.min_text_length}")
            self.stats['validation_failures'] += 1
            return False
        
        if len(content.text) > self.config.max_text_length:
            self.logger.warning(f"Content too long: {len(content.text)} > {self.config.max_text_length}")
            self.stats['validation_failures'] += 1
            return False
        
        # Check format
        if content.format not in self.config.allowed_formats:
            self.logger.warning(f"Format not allowed: {content.format}")
            self.stats['validation_failures'] += 1
            return False
        
        # Check encoding
        if self.config.validate_encoding:
            try:
                content.text.encode(content.encoding)
            except UnicodeEncodeError:
                self.logger.warning(f"Encoding validation failed: {content.encoding}")
                self.stats['validation_failures'] += 1
                return False
        
        return True
    
    async def _make_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with rate limiting and error handling.
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            RateLimitError: If rate limit is exceeded
            ScrapingError: If request fails
        """
        # Apply rate limiting
        await self._apply_rate_limit()
        
        # Check robots.txt
        if not self._check_robots_txt(url):
            raise RobotsTxtError(f"URL disallowed by robots.txt: {url}")
        
        # Make request
        try:
            self.stats['requests_made'] += 1
            response = self.session.get(url, timeout=self.config.timeout, **kwargs)
            response.raise_for_status()
            
            self.stats['successful_requests'] += 1
            return response
            
        except requests.exceptions.Timeout:
            self.stats['failed_requests'] += 1
            raise ScrapingError(f"Request timeout: {url}")
        except requests.exceptions.ConnectionError:
            self.stats['failed_requests'] += 1
            raise ScrapingError(f"Connection error: {url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                self.stats['rate_limited_requests'] += 1
                raise RateLimitError(f"Rate limited: {url}")
            self.stats['failed_requests'] += 1
            raise ScrapingError(f"HTTP error {e.response.status_code}: {url}")
        except Exception as e:
            self.stats['failed_requests'] += 1
            raise ScrapingError(f"Unexpected error: {e}")
    
    @abstractmethod
    async def scrape_url(self, url: str) -> ScrapedContent:
        """Scrape content from a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object
            
        Raises:
            ScrapingError: If scraping fails
        """
        pass
    
    async def scrape_task(self, task: ScrapingTask) -> List[ScrapingResult]:
        """Scrape multiple URLs from a task.
        
        Args:
            task: Scraping task
            
        Returns:
            List of scraping results
        """
        results = []
        task.start()
        
        self.logger.info(f"Starting scraping task {task.id} with {len(task.urls)} URLs")
        
        for url in task.urls:
            result = ScrapingResult(
                task_id=task.id,
                url=url,
                status=ScrapingStatus.RUNNING
            )
            
            try:
                # Scrape content
                content = await self.scrape_url(url)
                
                # Validate content
                if not self._validate_content(content):
                    raise ContentValidationError("Content validation failed")
                
                # Complete result
                result.complete(content)
                task.add_result(True)
                
                self.logger.info(f"Successfully scraped: {url}")
                
            except Exception as e:
                # Handle retries
                if result.retry_count < task.max_retries:
                    result.retry()
                    self.logger.warning(f"Retrying {url} (attempt {result.retry_count + 1}): {e}")
                    continue
                else:
                    result.fail(str(e), type(e).__name__)
                    task.add_result(False)
                    self.logger.error(f"Failed to scrape {url}: {e}")
            
            results.append(result)
        
        # Complete task
        if task.failed_urls == 0:
            task.complete()
        else:
            task.fail()
        
        self.logger.info(f"Completed task {task.id}: {task.successful_urls}/{task.total_urls} successful")
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'source': self.source_name,
            'stats': self.stats.copy(),
            'rate_limit': self._rate_limit,
            'source_config': self.source_config.dict() if self.source_config else None
        }
    
    def reset_stats(self) -> None:
        """Reset scraper statistics."""
        self.stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'rate_limited_requests': 0,
            'robots_txt_blocks': 0,
            'validation_failures': 0,
        }
    
    def close(self) -> None:
        """Close the scraper and cleanup resources."""
        self.session.close()
        self.logger.info(f"Closed scraper for {self.source_name}")
