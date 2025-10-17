"""Filesystem storage for scraped content."""

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .config import ScrapingConfig
from .models import ScrapedContent, ScrapingResult


class StorageError(Exception):
    """Exception raised for storage operations."""
    pass


class FileSystemStorage:
    """Filesystem-based storage for scraped content.
    
    Organizes content in a structured directory hierarchy:
    data/raw/{source}/{category}/{format}/
    """
    
    def __init__(self, config: ScrapingConfig):
        """Initialize storage.
        
        Args:
            config: Scraping configuration
        """
        self.config = config
        self.base_path = Path(config.storage_path)
        self.duplicate_detection = config.duplicate_detection
        
        # Create base directory if needed
        if config.create_directories:
            self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Track stored content for duplicate detection
        self._content_hashes: Set[str] = set()
        self._load_existing_hashes()
    
    def _load_existing_hashes(self) -> None:
        """Load existing content hashes for duplicate detection."""
        if not self.duplicate_detection:
            return
        
        try:
            # Load from a hash index file
            hash_file = self.base_path / ".content_hashes.json"
            if hash_file.exists():
                with open(hash_file, 'r', encoding='utf-8') as f:
                    self._content_hashes = set(json.load(f))
        except Exception:
            # If loading fails, start with empty set
            self._content_hashes = set()
    
    def _save_content_hashes(self) -> None:
        """Save content hashes to index file."""
        if not self.duplicate_detection:
            return
        
        try:
            hash_file = self.base_path / ".content_hashes.json"
            with open(hash_file, 'w', encoding='utf-8') as f:
                json.dump(list(self._content_hashes), f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save content hashes: {e}")
    
    def _get_content_hash(self, content: ScrapedContent) -> str:
        """Generate hash for content deduplication.
        
        Args:
            content: Content to hash
            
        Returns:
            SHA-256 hash of content
        """
        # Create hash from text content and URL
        hash_input = f"{content.text}|{content.url}|{content.source}"
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def _get_storage_path(self, content: ScrapedContent) -> Path:
        """Get storage path for content.
        
        Args:
            content: Content to store
            
        Returns:
            Path for storing content
        """
        # Create directory structure: {source}/{category}/{format}/
        category = content.category or "uncategorized"
        format_dir = content.format.value
        
        storage_path = self.base_path / content.source / category / format_dir
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return storage_path
    
    def _is_duplicate(self, content: ScrapedContent) -> bool:
        """Check if content is a duplicate.
        
        Args:
            content: Content to check
            
        Returns:
            True if duplicate, False otherwise
        """
        if not self.duplicate_detection:
            return False
        
        content_hash = self._get_content_hash(content)
        return content_hash in self._content_hashes
    
    def store_content(self, content: ScrapedContent) -> Path:
        """Store scraped content to filesystem.
        
        Args:
            content: Content to store
            
        Returns:
            Path where content was stored
            
        Raises:
            StorageError: If storage fails
        """
        try:
            # Check for duplicates
            if self._is_duplicate(content):
                raise StorageError(f"Duplicate content detected: {content.url}")
            
            # Get storage path
            storage_path = self._get_storage_path(content)
            
            # Generate filenames
            text_filename = content.get_filename()
            metadata_filename = content.get_metadata_filename()
            
            text_path = storage_path / text_filename
            metadata_path = storage_path / metadata_filename
            
            # Store text content
            with open(text_path, 'w', encoding=content.encoding) as f:
                f.write(content.text)
            
            # Store metadata
            metadata = content.dict()
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            # Update content hash tracking
            if self.duplicate_detection:
                content_hash = self._get_content_hash(content)
                self._content_hashes.add(content_hash)
                self._save_content_hashes()
            
            return text_path
            
        except Exception as e:
            raise StorageError(f"Failed to store content: {e}")
    
    def load_content(self, content_path: Path) -> ScrapedContent:
        """Load content from filesystem.
        
        Args:
            content_path: Path to content file
            
        Returns:
            ScrapedContent object
            
        Raises:
            StorageError: If loading fails
        """
        try:
            # Find corresponding metadata file
            metadata_path = content_path.with_suffix('.json').with_name(
                content_path.stem.replace(f".{content_path.suffix[1:]}", "_metadata.json")
            )
            
            if not metadata_path.exists():
                raise StorageError(f"Metadata file not found: {metadata_path}")
            
            # Load metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Load text content
            encoding = metadata.get('encoding', 'utf-8')
            with open(content_path, 'r', encoding=encoding) as f:
                text = f.read()
            
            # Update text in metadata
            metadata['text'] = text
            
            # Create ScrapedContent object
            return ScrapedContent(**metadata)
            
        except Exception as e:
            raise StorageError(f"Failed to load content: {e}")
    
    def list_content(self, source: Optional[str] = None, 
                    category: Optional[str] = None,
                    format_type: Optional[str] = None) -> List[Path]:
        """List stored content files.
        
        Args:
            source: Filter by source name
            category: Filter by category
            format_type: Filter by format
            
        Returns:
            List of content file paths
        """
        content_files = []
        
        # Determine search path
        if source:
            search_path = self.base_path / source
        else:
            search_path = self.base_path
        
        if not search_path.exists():
            return content_files
        
        # Walk through directory structure
        for file_path in search_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Skip metadata files
                if file_path.name.endswith('_metadata.json'):
                    continue
                
                # Apply filters
                if category and category not in file_path.parts:
                    continue
                
                if format_type and file_path.suffix != f".{format_type}":
                    continue
                
                content_files.append(file_path)
        
        return sorted(content_files)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics.
        
        Returns:
            Dictionary of storage statistics
        """
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'sources': {},
            'formats': {},
            'categories': {},
        }
        
        for content_file in self.list_content():
            try:
                # Get file size
                file_size = content_file.stat().st_size
                stats['total_files'] += 1
                stats['total_size_bytes'] += file_size
                
                # Parse path for metadata
                parts = content_file.relative_to(self.base_path).parts
                if len(parts) >= 3:
                    source, category, format_type = parts[0], parts[1], parts[2]
                    
                    # Count by source
                    if source not in stats['sources']:
                        stats['sources'][source] = 0
                    stats['sources'][source] += 1
                    
                    # Count by category
                    if category not in stats['categories']:
                        stats['categories'][category] = 0
                    stats['categories'][category] += 1
                    
                    # Count by format
                    if format_type not in stats['formats']:
                        stats['formats'][format_type] = 0
                    stats['formats'][format_type] += 1
                
            except Exception:
                # Skip files that can't be processed
                continue
        
        return stats
    
    def cleanup_orphaned_files(self) -> int:
        """Remove orphaned files (content without metadata or vice versa).
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        for content_file in self.list_content():
            # Check for corresponding metadata file
            metadata_file = content_file.with_suffix('.json').with_name(
                content_file.stem.replace(f".{content_file.suffix[1:]}", "_metadata.json")
            )
            
            if not metadata_file.exists():
                try:
                    content_file.unlink()
                    removed_count += 1
                except Exception:
                    pass
        
        # Check for orphaned metadata files
        for metadata_file in self.base_path.rglob("*_metadata.json"):
            content_file = metadata_file.with_suffix('').with_name(
                metadata_file.stem.replace("_metadata", "")
            )
            
            if not content_file.exists():
                try:
                    metadata_file.unlink()
                    removed_count += 1
                except Exception:
                    pass
        
        return removed_count
    
    def export_content(self, output_path: Path, 
                      source: Optional[str] = None,
                      format_type: Optional[str] = None) -> None:
        """Export content to a different location.
        
        Args:
            output_path: Path to export to
            source: Filter by source
            format_type: Filter by format
        """
        output_path.mkdir(parents=True, exist_ok=True)
        
        for content_file in self.list_content(source=source, format_type=format_type):
            try:
                # Create relative path in output
                relative_path = content_file.relative_to(self.base_path)
                dest_path = output_path / relative_path
                
                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(content_file, dest_path)
                
                # Copy metadata file
                metadata_file = content_file.with_suffix('.json').with_name(
                    content_file.stem.replace(f".{content_file.suffix[1:]}", "_metadata.json")
                )
                if metadata_file.exists():
                    dest_metadata = dest_path.with_suffix('.json').with_name(
                        dest_path.stem.replace(f".{dest_path.suffix[1:]}", "_metadata.json")
                    )
                    shutil.copy2(metadata_file, dest_metadata)
                
            except Exception as e:
                raise StorageError(f"Failed to export {content_file}: {e}")
    
    def get_duplicate_content(self) -> List[Dict[str, Any]]:
        """Get information about duplicate content.
        
        Returns:
            List of duplicate content information
        """
        if not self.duplicate_detection:
            return []
        
        # Group content by hash
        hash_groups = {}
        
        for content_file in self.list_content():
            try:
                content = self.load_content(content_file)
                content_hash = self._get_content_hash(content)
                
                if content_hash not in hash_groups:
                    hash_groups[content_hash] = []
                
                hash_groups[content_hash].append({
                    'path': content_file,
                    'url': content.url,
                    'title': content.title,
                    'source': content.source,
                    'scraped_at': content.scraped_at
                })
                
            except Exception:
                continue
        
        # Return groups with more than one item
        duplicates = []
        for content_hash, items in hash_groups.items():
            if len(items) > 1:
                duplicates.append({
                    'hash': content_hash,
                    'count': len(items),
                    'items': items
                })
        
        return duplicates
