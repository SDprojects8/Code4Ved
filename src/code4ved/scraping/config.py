"""Configuration management for web scraping module."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator

from .models import SourceMetadata, TextFormat


class ScrapingConfig(BaseModel):
    """Configuration for web scraping operations."""
    
    # General settings
    user_agent: str = Field(default="Code4Ved/1.0", description="User agent string")
    timeout: int = Field(default=30, ge=1, description="Default timeout in seconds")
    max_retries: int = Field(default=3, ge=0, description="Default max retries")
    respect_robots: bool = Field(default=True, description="Respect robots.txt")
    
    # Rate limiting
    default_rate_limit: float = Field(default=1.0, ge=0.1, description="Default rate limit (req/sec)")
    burst_size: int = Field(default=5, ge=1, description="Rate limiter burst size")
    
    # Content filtering
    min_text_length: int = Field(default=100, ge=0, description="Minimum text length")
    max_text_length: int = Field(default=1000000, ge=1, description="Maximum text length")
    allowed_formats: List[TextFormat] = Field(
        default_factory=lambda: list(TextFormat),
        description="Allowed text formats"
    )
    
    # Storage settings
    storage_path: Path = Field(default=Path("data/raw"), description="Storage base path")
    create_directories: bool = Field(default=True, description="Create storage directories")
    duplicate_detection: bool = Field(default=True, description="Enable duplicate detection")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    log_file: Optional[Path] = Field(None, description="Log file path")
    
    # Source configurations
    sources: Dict[str, SourceMetadata] = Field(
        default_factory=dict,
        description="Source repository configurations"
    )
    
    # Performance settings
    max_concurrent_requests: int = Field(default=5, ge=1, description="Max concurrent requests")
    request_queue_size: int = Field(default=100, ge=1, description="Request queue size")
    
    # Validation settings
    validate_content: bool = Field(default=True, description="Validate scraped content")
    validate_encoding: bool = Field(default=True, description="Validate text encoding")
    
    # SSL settings
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    ssl_warnings: bool = Field(default=True, description="Show SSL warnings")
    
    @validator('storage_path')
    def validate_storage_path(cls, v):
        """Validate and create storage path if needed."""
        if isinstance(v, str):
            v = Path(v)
        return v
    
    @validator('log_file')
    def validate_log_file(cls, v):
        """Validate log file path."""
        if v and isinstance(v, str):
            v = Path(v)
        return v
    
    @classmethod
    def from_file(cls, config_path: Path) -> "ScrapingConfig":
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            ScrapingConfig instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Extract sources from the YAML structure
        sources_data = config_data.pop('sources', {})
        
        # Create config instance with remaining data
        config = cls(**config_data)
        
        # Parse and add sources
        for source_name, source_config in sources_data.items():
            # Convert format strings to TextFormat enums
            if 'supported_formats' in source_config:
                formats = []
                for fmt in source_config['supported_formats']:
                    try:
                        formats.append(TextFormat(fmt.upper()))
                    except ValueError:
                        # Skip invalid formats
                        continue
                source_config['supported_formats'] = formats
            
            # Create SourceMetadata object
            source_metadata = SourceMetadata(**source_config)
            config.add_source(source_metadata)
        
        return config
    
    @classmethod
    def from_env(cls) -> "ScrapingConfig":
        """Load configuration from environment variables.
        
        Returns:
            ScrapingConfig instance
        """
        config_data = {}
        
        # Map environment variables to config fields
        env_mapping = {
            'C4V_USER_AGENT': 'user_agent',
            'C4V_TIMEOUT': 'timeout',
            'C4V_MAX_RETRIES': 'max_retries',
            'C4V_RESPECT_ROBOTS': 'respect_robots',
            'C4V_RATE_LIMIT': 'default_rate_limit',
            'C4V_MIN_TEXT_LENGTH': 'min_text_length',
            'C4V_MAX_TEXT_LENGTH': 'max_text_length',
            'C4V_STORAGE_PATH': 'storage_path',
            'C4V_LOG_LEVEL': 'log_level',
            'C4V_LOG_FILE': 'log_file',
            'C4V_MAX_CONCURRENT': 'max_concurrent_requests',
            'C4V_VERIFY_SSL': 'verify_ssl',
            'C4V_SSL_WARNINGS': 'ssl_warnings',
        }
        
        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Type conversion based on field type
                if config_field in ['timeout', 'max_retries', 'min_text_length', 'max_text_length', 'max_concurrent_requests']:
                    config_data[config_field] = int(value)
                elif config_field in ['default_rate_limit']:
                    config_data[config_field] = float(value)
                elif config_field in ['respect_robots', 'create_directories', 'duplicate_detection', 'validate_content', 'validate_encoding', 'verify_ssl', 'ssl_warnings']:
                    config_data[config_field] = value.lower() in ('true', '1', 'yes', 'on')
                elif config_field in ['storage_path', 'log_file']:
                    config_data[config_field] = Path(value)
                else:
                    config_data[config_field] = value
        
        return cls(**config_data)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file.
        
        Args:
            config_path: Path to save configuration file
        """
        config_data = self.dict()
        
        # Convert Path objects to strings for YAML serialization
        for key, value in config_data.items():
            if isinstance(value, Path):
                config_data[key] = str(value)
            elif isinstance(value, dict) and 'sources' in key:
                # Handle sources dictionary
                for source_name, source_config in value.items():
                    if isinstance(source_config, dict):
                        for source_key, source_value in source_config.items():
                            if isinstance(source_value, Path):
                                config_data[key][source_name][source_key] = str(source_value)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def get_source_config(self, source_name: str) -> Optional[SourceMetadata]:
        """Get configuration for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            SourceMetadata if found, None otherwise
        """
        return self.sources.get(source_name)
    
    def add_source(self, source: SourceMetadata) -> None:
        """Add a source configuration.
        
        Args:
            source: Source metadata to add
        """
        self.sources[source.name] = source
    
    def remove_source(self, source_name: str) -> bool:
        """Remove a source configuration.
        
        Args:
            source_name: Name of the source to remove
            
        Returns:
            True if removed, False if not found
        """
        if source_name in self.sources:
            del self.sources[source_name]
            return True
        return False


def get_default_config() -> ScrapingConfig:
    """Get default configuration from YAML file.
    
    Returns:
        ScrapingConfig with source configurations from YAML file
    """
    # Try to load from YAML file first
    config_path = Path("config/scraping.yaml")
    if config_path.exists():
        try:
            return ScrapingConfig.from_file(config_path)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Falling back to built-in configuration")
    
    # Fallback to built-in configuration
    config = ScrapingConfig()
    
    # Add default source configurations
    sources = {
        "vedicheritage": SourceMetadata(
            name="vedicheritage",
            base_url="https://vedicheritage.gov.in",
            description="Government of India Vedic Heritage Portal",
            language="en",
            encoding="utf-8",
            robots_txt_url="https://vedicheritage.gov.in/robots.txt",
            rate_limit=1.0,
            max_pages=1000,
            supported_formats=[TextFormat.HTML, TextFormat.PDF]
        ),
        "gretil": SourceMetadata(
            name="gretil",
            base_url="http://gretil.sub.uni-goettingen.de",
            description="Göttingen Register of Electronic Texts",
            language="en",
            encoding="utf-8",
            robots_txt_url="http://gretil.sub.uni-goettingen.de/robots.txt",
            rate_limit=0.5,  # More conservative for academic site
            max_pages=500,
            supported_formats=[TextFormat.HTML, TextFormat.PLAINTEXT, TextFormat.XML]
        ),
        "ambuda": SourceMetadata(
            name="ambuda",
            base_url="https://ambuda.org",
            description="Open Source Sanskrit Platform",
            language="en",
            encoding="utf-8",
            robots_txt_url="https://ambuda.org/robots.txt",
            rate_limit=1.0,
            max_pages=2000,
            supported_formats=[TextFormat.HTML, TextFormat.JSON]
        )
    }
    
    for source in sources.values():
        config.add_source(source)
    
    return config
