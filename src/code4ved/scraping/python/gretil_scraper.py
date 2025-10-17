"""GRETIL (Göttingen Register of Electronic Texts) scraper implementation."""

import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests

from ..base import BaseScraper, ScrapingError
from ..models import ScrapedContent, TextFormat


class GretilScraper(BaseScraper):
    """Scraper for GRETIL (gretil.sub.uni-goettingen.de)."""
    
    def __init__(self, config, source_name: str = "gretil"):
        """Initialize GRETIL scraper.
        
        Args:
            config: Scraping configuration
            source_name: Source name identifier
        """
        super().__init__(config, source_name)
        
        # GRETIL-specific selectors
        self.content_selectors = [
            'pre',
            'div.text',
            'div.content',
            'div.main',
            'body'
        ]
        
        self.title_selectors = [
            'title',
            'h1',
            'h2',
            '.title'
        ]
        
        # GRETIL file extensions
        self.text_extensions = ['.txt', '.html', '.htm', '.xml']
        self.pdf_extensions = ['.pdf']
    
    async def scrape_url(self, url: str) -> ScrapedContent:
        """Scrape content from GRETIL.
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            # Make request
            response = await self._make_request(url)
            
            # Determine content format
            content_format = self._determine_format(url, response)
            
            if content_format == TextFormat.PDF:
                # Handle PDF content
                content = await self._extract_pdf_content(response)
            else:
                # Handle text content
                content = await self._extract_text_content(response, url)
            
            # Extract metadata
            metadata = self._extract_metadata(response, url)
            
            # Create ScrapedContent object
            scraped_content = ScrapedContent(
                text=content,
                title=metadata.get('title', ''),
                url=url,
                source=self.source_name,
                format=content_format,
                language=metadata.get('language', 'en'),
                category=metadata.get('category'),
                author=metadata.get('author'),
                file_size=len(response.content),
                encoding=response.encoding or 'utf-8'
            )
            
            return scraped_content
            
        except Exception as e:
            raise ScrapingError(f"Failed to scrape {url}: {e}")
    
    def _determine_format(self, url: str, response: requests.Response) -> TextFormat:
        """Determine content format from URL and response.
        
        Args:
            url: Source URL
            response: HTTP response
            
        Returns:
            TextFormat enum value
        """
        # Check URL extension
        path = urlparse(url).path.lower()
        
        if any(path.endswith(ext) for ext in self.pdf_extensions):
            return TextFormat.PDF
        elif any(path.endswith(ext) for ext in self.text_extensions):
            return TextFormat.PLAINTEXT
        elif 'xml' in path:
            return TextFormat.XML
        else:
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type:
                return TextFormat.PDF
            elif 'xml' in content_type:
                return TextFormat.XML
            elif 'html' in content_type:
                return TextFormat.HTML
            else:
                return TextFormat.PLAINTEXT
    
    async def _extract_text_content(self, response: requests.Response, url: str) -> str:
        """Extract text content from response.
        
        Args:
            response: HTTP response
            url: Source URL
            
        Returns:
            Extracted text content
        """
        content_type = response.headers.get('content-type', '').lower()
        
        if 'html' in content_type:
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._extract_from_html(soup, url)
        elif 'xml' in content_type:
            # Parse XML content
            soup = BeautifulSoup(response.content, 'xml')
            return self._extract_from_xml(soup, url)
        else:
            # Plain text content
            return self._extract_from_plain_text(response.text, url)
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str) -> str:
        """Extract content from HTML.
        
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
            # Fallback to body
            content_element = soup.find('body') or soup.find('html')
        
        if not content_element:
            raise ScrapingError("Could not find content element in HTML")
        
        # Remove unwanted elements
        self._remove_unwanted_elements(content_element)
        
        # Extract text
        text = content_element.get_text(separator='\n', strip=True)
        
        # Clean text
        return self._clean_text(text)
    
    def _extract_from_xml(self, soup: BeautifulSoup, url: str) -> str:
        """Extract content from XML.
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Extracted text content
        """
        # For XML, we typically want the text content
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean XML-specific artifacts
        text = re.sub(r'<[^>]+>', '', text)  # Remove any remaining tags
        text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)  # Remove entities
        
        return self._clean_text(text)
    
    def _extract_from_plain_text(self, text: str, url: str) -> str:
        """Extract content from plain text.
        
        Args:
            text: Raw text content
            url: Source URL
            
        Returns:
            Cleaned text content
        """
        return self._clean_text(text)
    
    async def _extract_pdf_content(self, response: requests.Response) -> str:
        """Extract content from PDF response.
        
        Args:
            response: HTTP response containing PDF
            
        Returns:
            Extracted text content
        """
        # This would typically use PyPDF2 or pdfminer
        # For now, return a placeholder
        # In a real implementation, you'd use the PDFExtractor class
        return f"[PDF content from {len(response.content)} bytes - requires PDF extraction]"
    
    def _extract_metadata(self, response: requests.Response, url: str) -> dict:
        """Extract metadata from response and URL.
        
        Args:
            response: HTTP response
            url: Source URL
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'title': '',
            'author': None,
            'category': None,
            'language': 'en',
            'date': None
        }
        
        # Extract title from URL or content
        path = urlparse(url).path
        filename = path.split('/')[-1]
        
        # Remove file extension for title
        title = filename
        for ext in self.text_extensions + self.pdf_extensions:
            if title.endswith(ext):
                title = title[:-len(ext)]
                break
        
        # Clean title
        title = title.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        title = re.sub(r'\s+', ' ', title).strip()
        metadata['title'] = title or 'GRETIL Text'
        
        # Try to extract from HTML if available
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type:
            try:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title from HTML
                for selector in self.title_selectors:
                    title_element = soup.select_one(selector)
                    if title_element:
                        html_title = title_element.get_text(strip=True)
                        if html_title and len(html_title) > len(metadata['title']):
                            metadata['title'] = html_title
                        break
                
                # Extract language
                html_element = soup.find('html')
                if html_element and html_element.get('lang'):
                    metadata['language'] = html_element.get('lang')
                
            except Exception:
                pass
        
        # Determine category from URL path
        metadata['category'] = self._determine_category(url)
        
        # Extract author from filename patterns
        metadata['author'] = self._extract_author_from_filename(filename)
        
        return metadata
    
    def _determine_category(self, url: str) -> Optional[str]:
        """Determine content category from URL.
        
        Args:
            url: Source URL
            
        Returns:
            Category string or None
        """
        path = urlparse(url).path.lower()
        
        # GRETIL categories based on directory structure
        if '/veda/' in path or '/vedic/' in path:
            return 'Vedas'
        elif '/upanishad/' in path:
            return 'Upanishads'
        elif '/purana/' in path:
            return 'Puranas'
        elif '/gita/' in path:
            return 'Bhagavad Gita'
        elif '/sutra/' in path:
            return 'Sutras'
        elif '/mantra/' in path:
            return 'Mantras'
        elif '/stotra/' in path:
            return 'Stotras'
        elif '/epic/' in path:
            return 'Epic Literature'
        elif '/drama/' in path:
            return 'Drama'
        elif '/philosophy/' in path:
            return 'Philosophy'
        elif '/grammar/' in path:
            return 'Grammar'
        elif '/lexicon/' in path:
            return 'Lexicon'
        
        return 'Sanskrit Literature'
    
    def _extract_author_from_filename(self, filename: str) -> Optional[str]:
        """Extract author information from filename.
        
        Args:
            filename: Filename to analyze
            
        Returns:
            Author name or None
        """
        # Common patterns in GRETIL filenames
        patterns = [
            r'^([a-zA-Z]+)_',  # Author_work pattern
            r'_([a-zA-Z]+)_',  # work_Author_ pattern
            r'([a-zA-Z]+)\.',  # Author.work pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                author = match.group(1)
                # Filter out common non-author words
                if author.lower() not in ['text', 'work', 'book', 'chapter', 'part']:
                    return author.title()
        
        return None
    
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
            '.comments'
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
                line.lower() in ['home', 'about', 'contact', 'search', 'back', 'next']):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def discover_urls(self, base_url: str, max_pages: int = 100) -> List[str]:
        """Discover URLs to scrape from GRETIL.
        
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
            r'\.(css|js|png|jpg|jpeg|gif)$',
            r'/search',
            r'/contact',
            r'/about',
            r'/index\.html?$',
            r'/home$'
        ]
        
        for pattern in skip_patterns:
            if re.search(pattern, path):
                return False
        
        # Look for content indicators
        content_patterns = [
            r'\.(txt|html|htm|xml|pdf)$',
            r'/text/',
            r'/content/',
            r'/work/',
            r'/author/'
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
            r'/author/',
            r'/work/'
        ]
        
        for pattern in index_patterns:
            if re.search(pattern, path):
                return True
        
        return False
