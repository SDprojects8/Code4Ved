"""Tests for scraping models."""

import pytest
from datetime import datetime

from src.code4ved.scraping.models import (
    ScrapedContent,
    ScrapingTask,
    ScrapingResult,
    TextFormat,
    SourceMetadata,
    ScrapingStatus
)


class TestScrapedContent:
    """Test ScrapedContent model."""
    
    def test_create_scraped_content(self):
        """Test creating ScrapedContent."""
        content = ScrapedContent(
            text="Test content",
            title="Test Title",
            url="https://example.com",
            source="test_source",
            format=TextFormat.HTML
        )
        
        assert content.text == "Test content"
        assert content.title == "Test Title"
        assert content.url == "https://example.com"
        assert content.source == "test_source"
        assert content.format == TextFormat.HTML
        assert content.language == "en"  # default
        assert content.file_size == 0  # default
    
    def test_get_filename(self):
        """Test filename generation."""
        content = ScrapedContent(
            text="Test content",
            title="Test Title",
            url="https://example.com",
            source="test_source",
            format=TextFormat.HTML
        )
        
        filename = content.get_filename()
        assert filename.startswith("Test_Title_")
        assert filename.endswith(".html")
    
    def test_get_metadata_filename(self):
        """Test metadata filename generation."""
        content = ScrapedContent(
            text="Test content",
            title="Test Title",
            url="https://example.com",
            source="test_source",
            format=TextFormat.HTML
        )
        
        metadata_filename = content.get_metadata_filename()
        assert metadata_filename.startswith("Test_Title_")
        assert metadata_filename.endswith("_metadata.json")


class TestScrapingTask:
    """Test ScrapingTask model."""
    
    def test_create_scraping_task(self):
        """Test creating ScrapingTask."""
        task = ScrapingTask(
            id="test_task",
            source="test_source",
            urls=["https://example.com"]
        )
        
        assert task.id == "test_task"
        assert task.source == "test_source"
        assert task.urls == ["https://example.com"]
        assert task.status == ScrapingStatus.PENDING
        assert task.max_retries == 3  # default
        assert task.timeout == 30  # default
    
    def test_start_task(self):
        """Test starting a task."""
        task = ScrapingTask(
            id="test_task",
            source="test_source",
            urls=["https://example.com"]
        )
        
        task.start()
        
        assert task.status == ScrapingStatus.RUNNING
        assert task.started_at is not None
    
    def test_complete_task(self):
        """Test completing a task."""
        task = ScrapingTask(
            id="test_task",
            source="test_source",
            urls=["https://example.com"]
        )
        
        task.complete()
        
        assert task.status == ScrapingStatus.COMPLETED
        assert task.completed_at is not None
    
    def test_add_result(self):
        """Test adding results."""
        task = ScrapingTask(
            id="test_task",
            source="test_source",
            urls=["https://example.com", "https://example2.com"]
        )
        
        task.add_result(True)
        task.add_result(False)
        
        assert task.processed_urls == 2
        assert task.successful_urls == 1
        assert task.failed_urls == 1
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        task = ScrapingTask(
            id="test_task",
            source="test_source",
            urls=["https://example.com", "https://example2.com"]
        )
        
        assert task.progress_percentage == 0.0
        
        task.add_result(True)
        assert task.progress_percentage == 50.0
        
        task.add_result(False)
        assert task.progress_percentage == 100.0


class TestScrapingResult:
    """Test ScrapingResult model."""
    
    def test_create_scraping_result(self):
        """Test creating ScrapingResult."""
        result = ScrapingResult(
            task_id="test_task",
            url="https://example.com",
            status=ScrapingStatus.RUNNING
        )
        
        assert result.task_id == "test_task"
        assert result.url == "https://example.com"
        assert result.status == ScrapingStatus.RUNNING
        assert result.retry_count == 0  # default
    
    def test_complete_result(self):
        """Test completing a result."""
        result = ScrapingResult(
            task_id="test_task",
            url="https://example.com",
            status=ScrapingStatus.RUNNING
        )
        
        content = ScrapedContent(
            text="Test content",
            title="Test Title",
            url="https://example.com",
            source="test_source",
            format=TextFormat.HTML
        )
        
        result.complete(content)
        
        assert result.status == ScrapingStatus.COMPLETED
        assert result.completed_at is not None
        assert result.content == content
        assert result.processing_time > 0
    
    def test_fail_result(self):
        """Test failing a result."""
        result = ScrapingResult(
            task_id="test_task",
            url="https://example.com",
            status=ScrapingStatus.RUNNING
        )
        
        result.fail("Test error", "TestError")
        
        assert result.status == ScrapingStatus.FAILED
        assert result.completed_at is not None
        assert result.error_message == "Test error"
        assert result.error_type == "TestError"
        assert result.processing_time > 0
    
    def test_retry_result(self):
        """Test retrying a result."""
        result = ScrapingResult(
            task_id="test_task",
            url="https://example.com",
            status=ScrapingStatus.FAILED
        )
        
        result.retry()
        
        assert result.status == ScrapingStatus.RETRYING
        assert result.retry_count == 1
        assert result.error_message is None
        assert result.error_type is None


class TestSourceMetadata:
    """Test SourceMetadata model."""
    
    def test_create_source_metadata(self):
        """Test creating SourceMetadata."""
        metadata = SourceMetadata(
            name="test_source",
            base_url="https://example.com"
        )
        
        assert metadata.name == "test_source"
        assert metadata.base_url == "https://example.com"
        assert metadata.language == "en"  # default
        assert metadata.encoding == "utf-8"  # default
        assert metadata.rate_limit == 1.0  # default
        assert metadata.max_pages == 1000  # default
    
    def test_validate_base_url(self):
        """Test base URL validation."""
        # Valid URL
        metadata = SourceMetadata(
            name="test_source",
            base_url="https://example.com"
        )
        assert metadata.base_url == "https://example.com"
        
        # Invalid URL should raise validation error
        with pytest.raises(ValueError):
            SourceMetadata(
                name="test_source",
                base_url="invalid-url"
            )
    
    def test_validate_rate_limit(self):
        """Test rate limit validation."""
        # Valid rate limit
        metadata = SourceMetadata(
            name="test_source",
            base_url="https://example.com",
            rate_limit=2.0
        )
        assert metadata.rate_limit == 2.0
        
        # Invalid rate limit should raise validation error
        with pytest.raises(ValueError):
            SourceMetadata(
                name="test_source",
                base_url="https://example.com",
                rate_limit=0
            )
