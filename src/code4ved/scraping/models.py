"""Data models for web scraping operations."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator


class TextFormat(str, Enum):
    """Supported text formats for scraping."""
    HTML = "html"
    PDF = "pdf"
    PLAINTEXT = "plaintext"
    XML = "xml"
    JSON = "json"


class ScrapingStatus(str, Enum):
    """Scraping operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class SourceMetadata(BaseModel):
    """Metadata about the source repository."""
    
    name: str = Field(..., description="Repository name")
    base_url: str = Field(..., description="Base URL of the repository")
    description: Optional[str] = Field(None, description="Repository description")
    language: str = Field(default="en", description="Primary language")
    encoding: str = Field(default="utf-8", description="Text encoding")
    robots_txt_url: Optional[str] = Field(None, description="URL to robots.txt")
    rate_limit: float = Field(default=1.0, description="Requests per second")
    max_pages: int = Field(default=1000, description="Maximum pages to scrape")
    supported_formats: List[TextFormat] = Field(
        default_factory=lambda: [TextFormat.HTML, TextFormat.PLAINTEXT],
        description="Supported text formats"
    )
    
    @validator('base_url')
    def validate_base_url(cls, v):
        """Validate base URL format."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid base URL format")
        return v.rstrip('/')
    
    @validator('rate_limit')
    def validate_rate_limit(cls, v):
        """Validate rate limit is positive."""
        if v <= 0:
            raise ValueError("Rate limit must be positive")
        return v


class ScrapedContent(BaseModel):
    """Represents scraped content with metadata."""
    
    # Core content
    text: str = Field(..., description="Extracted text content")
    title: str = Field(..., description="Content title")
    url: str = Field(..., description="Source URL")
    
    # Metadata
    source: str = Field(..., description="Source repository name")
    format: TextFormat = Field(..., description="Content format")
    language: str = Field(default="en", description="Content language")
    category: Optional[str] = Field(None, description="Content category")
    author: Optional[str] = Field(None, description="Content author")
    
    # Technical metadata
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    file_size: int = Field(default=0, description="Content size in bytes")
    encoding: str = Field(default="utf-8", description="Text encoding")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDFs)")
    
    # Processing metadata
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    retry_count: int = Field(default=0, description="Number of retries")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Content quality score")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Content tags")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    @validator('text')
    def validate_text_not_empty(cls, v):
        """Validate text content is not empty."""
        if not v or not v.strip():
            raise ValueError("Text content cannot be empty")
        return v.strip()
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        return v
    
    def get_filename(self) -> str:
        """Generate filename for storage."""
        # Clean title for filename
        clean_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_title = clean_title.replace(' ', '_')
        
        # Add timestamp to avoid conflicts
        timestamp = self.scraped_at.strftime("%Y%m%d_%H%M%S")
        
        return f"{clean_title}_{timestamp}.{self.format.value}"
    
    def get_metadata_filename(self) -> str:
        """Generate metadata filename for storage."""
        base_filename = self.get_filename()
        return base_filename.replace(f".{self.format.value}", "_metadata.json")


class ScrapingTask(BaseModel):
    """Represents a scraping task configuration."""
    
    id: str = Field(..., description="Unique task identifier")
    source: str = Field(..., description="Source repository name")
    urls: List[str] = Field(..., description="URLs to scrape")
    
    # Configuration
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    timeout: int = Field(default=30, ge=1, description="Request timeout in seconds")
    rate_limit: float = Field(default=1.0, ge=0.1, description="Requests per second")
    respect_robots: bool = Field(default=True, description="Respect robots.txt")
    
    # Filters
    min_text_length: int = Field(default=100, ge=0, description="Minimum text length")
    max_text_length: int = Field(default=1000000, ge=1, description="Maximum text length")
    allowed_formats: List[TextFormat] = Field(
        default_factory=lambda: list(TextFormat),
        description="Allowed text formats"
    )
    
    # Status tracking
    status: ScrapingStatus = Field(default=ScrapingStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    total_urls: int = Field(default=0, description="Total URLs to process")
    processed_urls: int = Field(default=0, description="URLs processed")
    successful_urls: int = Field(default=0, description="Successfully scraped URLs")
    failed_urls: int = Field(default=0, description="Failed URLs")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")
    
    @validator('urls')
    def validate_urls_not_empty(cls, v):
        """Validate URLs list is not empty."""
        if not v:
            raise ValueError("URLs list cannot be empty")
        return v
    
    def start(self) -> None:
        """Mark task as started."""
        self.status = ScrapingStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark task as completed."""
        self.status = ScrapingStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def fail(self) -> None:
        """Mark task as failed."""
        self.status = ScrapingStatus.FAILED
        self.completed_at = datetime.utcnow()
    
    def add_result(self, success: bool) -> None:
        """Add a processing result."""
        self.processed_urls += 1
        if success:
            self.successful_urls += 1
        else:
            self.failed_urls += 1
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_urls == 0:
            return 0.0
        return (self.processed_urls / self.total_urls) * 100


class ScrapingResult(BaseModel):
    """Represents the result of a scraping operation."""
    
    task_id: str = Field(..., description="Associated task ID")
    url: str = Field(..., description="Scraped URL")
    status: ScrapingStatus = Field(..., description="Operation status")
    
    # Content
    content: Optional[ScrapedContent] = Field(None, description="Scraped content")
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    processing_time: float = Field(default=0.0, description="Processing time in seconds")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_type: Optional[str] = Field(None, description="Error type if failed")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")
    
    def complete(self, content: Optional[ScrapedContent] = None) -> None:
        """Mark result as completed."""
        self.status = ScrapingStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.processing_time = (self.completed_at - self.started_at).total_seconds()
        if content:
            self.content = content
    
    def fail(self, error_message: str, error_type: str = "UnknownError") -> None:
        """Mark result as failed."""
        self.status = ScrapingStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.processing_time = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error_message
        self.error_type = error_type
    
    def retry(self) -> None:
        """Mark result for retry."""
        self.status = ScrapingStatus.RETRYING
        self.retry_count += 1
        self.error_message = None
        self.error_type = None
