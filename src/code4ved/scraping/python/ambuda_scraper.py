"""Ambuda.org scraper implementation."""

import json
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

from ..base import BaseScraper, ScrapingError
from ..models import ScrapedContent, TextFormat


class AmbudaScraper(BaseScraper):
    """Scraper for Ambuda.org (Open Source Sanskrit Platform)."""
    
    def __init__(self, config, source_name: str = "ambuda"):
        """Initialize Ambuda scraper.
        
        Args:
            config: Scraping configuration
            source_name: Source name identifier
        """
        super().__init__(config, source_name)
        
        # Ambuda API endpoints
        self.api_base = "https://ambuda.org/api"
        self.text_api = f"{self.api_base}/texts"
        self.work_api = f"{self.api_base}/works"
        
        # Content selectors for HTML fallback
        self.content_selectors = [
            'div.text-content',
            'div.content',
            'div.main-content',
            'article',
            'main',
            'div.text'
        ]
        
        self.title_selectors = [
            'h1',
            'h2.title',
            '.title',
            '.work-title',
            '.text-title'
        ]
    
    async def scrape_url(self, url: str) -> ScrapedContent:
        """Scrape content from Ambuda.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            # Try API first
            content = await self._scrape_via_api(url)
            if content:
                return content
            
            # Fallback to HTML scraping
            return await self._scrape_via_html(url)
            
        except Exception as e:
            raise ScrapingError(f"Failed to scrape {url}: {e}")
    
    async def _scrape_via_api(self, url: str) -> Optional[ScrapedContent]:
        """Try to scrape content via Ambuda API.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object or None if API not available
        """
        try:
            # Extract work/text ID from URL
            work_id, text_id = self._extract_ids_from_url(url)
            if not work_id:
                return None
            
            # Get work metadata
            work_data = await self._get_work_metadata(work_id)
            if not work_data:
                return None
            
            # Get text content
            text_data = await self._get_text_content(work_id, text_id)
            if not text_data:
                return None
            
            # Create ScrapedContent object
            scraped_content = ScrapedContent(
                text=text_data.get('content', ''),
                title=work_data.get('title', ''),
                url=url,
                source=self.source_name,
                format=TextFormat.JSON,
                language=work_data.get('language', 'sa'),  # Sanskrit
                category=work_data.get('category'),
                author=work_data.get('author'),
                file_size=len(text_data.get('content', '')),
                encoding='utf-8',
                properties={
                    'work_id': work_id,
                    'text_id': text_id,
                    'api_data': work_data
                }
            )
            
            return scraped_content
            
        except Exception as e:
            self.logger.warning(f"API scraping failed for {url}: {e}")
            return None
    
    async def _scrape_via_html(self, url: str) -> ScrapedContent:
        """Scrape content via HTML parsing.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object
        """
        # Make request
        response = await self._make_request(url)
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract content
        content = self._extract_content(soup, url)
        
        # Extract metadata
        metadata = self._extract_metadata(soup, url)
        
        # Create ScrapedContent object
        scraped_content = ScrapedContent(
            text=content,
            title=metadata.get('title', ''),
            url=url,
            source=self.source_name,
            format=TextFormat.HTML,
            language=metadata.get('language', 'sa'),
            category=metadata.get('category'),
            author=metadata.get('author'),
            file_size=len(response.content),
            encoding=response.encoding or 'utf-8'
        )
        
        return scraped_content
    
    def _extract_ids_from_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Extract work and text IDs from URL.
        
        Args:
            url: URL to parse
            
        Returns:
            Tuple of (work_id, text_id)
        """
        path = urlparse(url).path
        
        # Ambuda URL patterns
        patterns = [
            r'/texts/([^/]+)/([^/]+)',  # /texts/work_id/text_id
            r'/works/([^/]+)',  # /works/work_id
            r'/text/([^/]+)/([^/]+)',  # /text/work_id/text_id
        ]
        
        for pattern in patterns:
            match = re.search(pattern, path)
            if match:
                if len(match.groups()) == 2:
                    return match.group(1), match.group(2)
                else:
                    return match.group(1), None
        
        return None, None
    
    async def _get_work_metadata(self, work_id: str) -> Optional[Dict[str, Any]]:
        """Get work metadata from API.
        
        Args:
            work_id: Work identifier
            
        Returns:
            Work metadata dictionary or None
        """
        try:
            url = f"{self.work_api}/{work_id}"
            response = await self._make_request(url)
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            self.logger.warning(f"Failed to get work metadata for {work_id}: {e}")
        
        return None
    
    async def _get_text_content(self, work_id: str, text_id: str) -> Optional[Dict[str, Any]]:
        """Get text content from API.
        
        Args:
            work_id: Work identifier
            text_id: Text identifier
            
        Returns:
            Text content dictionary or None
        """
        try:
            url = f"{self.text_api}/{work_id}/{text_id}"
            response = await self._make_request(url)
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            self.logger.warning(f"Failed to get text content for {work_id}/{text_id}: {e}")
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """Extract main content from HTML.
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Extracted text content
        """
        # Try different content selectors
        content_element = None
        for selector in self.content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            # Fallback: use body or main content
            content_element = soup.find('body') or soup.find('main')
        
        if not content_element:
            raise ScrapingError("Could not find content element")
        
        # Remove unwanted elements
        self._remove_unwanted_elements(content_element)
        
        # Extract text
        text = content_element.get_text(separator='\n', strip=True)
        
        # Clean text
        text = self._clean_text(text)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> dict:
        """Extract metadata from HTML.
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'title': '',
            'author': None,
            'category': None,
            'language': 'sa',  # Sanskrit
            'date': None
        }
        
        # Extract title
        for selector in self.title_selectors:
            title_element = soup.select_one(selector)
            if title_element:
                metadata['title'] = title_element.get_text(strip=True)
                break
        
        # If no title found, try to extract from URL or page title
        if not metadata['title']:
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            else:
                # Extract from URL path
                path = urlparse(url).path
                metadata['title'] = path.split('/')[-1].replace('-', ' ').title()
        
        # Extract other metadata
        metadata_selectors = {
            'author': ['.author', '.byline', '[rel="author"]', '.work-author'],
            'category': ['.category', '.breadcrumb', '.nav-path', '.work-category'],
            'date': ['.date', '.published', 'time', '.work-date'],
        }
        
        for field, selectors in metadata_selectors.items():
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    metadata[field] = element.get_text(strip=True)
                    break
        
        # Extract language from HTML lang attribute
        html_element = soup.find('html')
        if html_element and html_element.get('lang'):
            metadata['language'] = html_element.get('lang')
        
        # Determine category from URL or content
        metadata['category'] = self._determine_category(url, soup)
        
        return metadata
    
    def _determine_category(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        """Determine content category from URL and content.
        
        Args:
            url: Source URL
            soup: BeautifulSoup object
            
        Returns:
            Category string or None
        """
        # Extract from URL path
        path = urlparse(url).path.lower()
        
        # Common Sanskrit categories
        if 'veda' in path or 'vedic' in path:
            return 'Vedas'
        elif 'upanishad' in path:
            return 'Upanishads'
        elif 'purana' in path:
            return 'Puranas'
        elif 'gita' in path:
            return 'Bhagavad Gita'
        elif 'sutra' in path:
            return 'Sutras'
        elif 'mantra' in path:
            return 'Mantras'
        elif 'stotra' in path:
            return 'Stotras'
        elif 'epic' in path:
            return 'Epic Literature'
        elif 'drama' in path:
            return 'Drama'
        elif 'philosophy' in path:
            return 'Philosophy'
        elif 'grammar' in path:
            return 'Grammar'
        elif 'lexicon' in path:
            return 'Lexicon'
        
        # Try to extract from breadcrumbs or navigation
        breadcrumb = soup.select_one('.breadcrumb, .nav-path, .breadcrumbs')
        if breadcrumb:
            breadcrumb_text = breadcrumb.get_text().lower()
            for category in ['veda', 'upanishad', 'purana', 'gita', 'sutra', 'mantra', 'stotra']:
                if category in breadcrumb_text:
                    return category.title()
        
        return 'Sanskrit Literature'
    
    def _remove_unwanted_elements(self, element) -> None:
        """Remove unwanted elements from content.
        
        Args:
            element: BeautifulSoup element to clean
        """
        # Elements to remove
        unwanted_selectors = [
            'script',
            'style',
            'nav',
            'header',
            'footer',
            '.navigation',
            '.menu',
            '.sidebar',
            '.advertisement',
            '.ads',
            '.social-share',
            '.comments',
            '.related-posts',
            '.toolbar',
            '.controls'
        ]
        
        for selector in unwanted_selectors:
            for unwanted in element.select(selector):
                unwanted.decompose()
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove page numbers and headers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that look like page numbers or navigation
            if (len(line) < 3 or 
                re.match(r'^\d+$', line) or
                re.match(r'^Page \d+', line) or
                line.lower() in ['home', 'about', 'contact', 'search', 'back', 'next', 'menu']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def discover_urls(self, base_url: str, max_pages: int = 100) -> List[str]:
        """Discover URLs to scrape from Ambuda.
        
        Args:
            base_url: Base URL to start discovery
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of discovered URLs
        """
        discovered_urls = set()
        
        # Try to discover via API first
        api_urls = await self._discover_via_api()
        discovered_urls.update(api_urls)
        
        # Fallback to HTML discovery
        if len(discovered_urls) < max_pages:
            html_urls = await self._discover_via_html(base_url, max_pages - len(discovered_urls))
            discovered_urls.update(html_urls)
        
        return list(discovered_urls)[:max_pages]
    
    async def _discover_via_api(self) -> List[str]:
        """Discover URLs via API.
        
        Returns:
            List of discovered URLs
        """
        discovered_urls = []
        
        try:
            # Get list of works
            response = await self._make_request(self.work_api)
            if response.status_code == 200:
                works = response.json()
                
                for work in works:
                    work_id = work.get('id')
                    if work_id:
                        # Get texts for this work
                        texts_url = f"{self.text_api}/{work_id}"
                        try:
                            texts_response = await self._make_request(texts_url)
                            if texts_response.status_code == 200:
                                texts = texts_response.json()
                                for text in texts:
                                    text_id = text.get('id')
                                    if text_id:
                                        url = f"https://ambuda.org/texts/{work_id}/{text_id}"
                                        discovered_urls.append(url)
                        except Exception:
                            continue
                
        except Exception as e:
            self.logger.warning(f"API discovery failed: {e}")
        
        return discovered_urls
    
    async def _discover_via_html(self, base_url: str, max_pages: int) -> List[str]:
        """Discover URLs via HTML parsing.
        
        Args:
            base_url: Base URL to start discovery
            max_pages: Maximum number of pages to discover
            
        Returns:
            List of discovered URLs
        """
        discovered_urls = set()
        to_visit = [base_url]
        visited = set()
        
        while to_visit and len(discovered_urls) < max_pages:
            current_url = to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            try:
                response = await self._make_request(current_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find links to content pages
                links = soup.find_all('a', href=True)
                
                for link in links:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(current_url, href)
                    
                    # Filter for content pages
                    if self._is_content_url(absolute_url):
                        discovered_urls.add(absolute_url)
                    
                    # Add to visit queue if it's a directory or index page
                    if self._is_index_url(absolute_url) and absolute_url not in visited:
                        to_visit.append(absolute_url)
                
            except Exception as e:
                self.logger.warning(f"Failed to discover URLs from {current_url}: {e}")
                continue
        
        return list(discovered_urls)
    
    def _is_content_url(self, url: str) -> bool:
        """Check if URL points to content.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL points to content
        """
        path = urlparse(url).path.lower()
        
        # Skip non-content URLs
        skip_patterns = [
            r'\.(css|js|png|jpg|jpeg|gif|pdf|doc|docx)$',
            r'/search',
            r'/contact',
            r'/about',
            r'/index\.html?$',
            r'/home$',
            r'/login',
            r'/register'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, path):
                return False
        
        # Look for content indicators
        content_patterns = [
            r'/texts/',
            r'/text/',
            r'/works/',
            r'/work/',
            r'veda',
            r'upanishad',
            r'purana',
            r'gita'
        ]
        
        for pattern in content_patterns:
            if re.search(pattern, path):
                return True
        
        return False
    
    def _is_index_url(self, url: str) -> bool:
        """Check if URL is an index/directory page.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is an index page
        """
        path = urlparse(url).path.lower()
        
        # Index page patterns
        index_patterns = [
            r'/$',
            r'/index\.html?$',
            r'/home$',
            r'/category/',
            r'/section/',
            r'/works/',
            r'/texts/'
        ]
        
        for pattern in index_patterns:
            if re.search(pattern, path):
                return True
        
        return False
