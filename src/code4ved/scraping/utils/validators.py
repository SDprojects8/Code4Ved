"""Content validation utilities."""

import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from ..models import ScrapedContent, TextFormat


class ValidationError(Exception):
    """Exception raised when content validation fails."""
    pass


class ContentValidator:
    """Validator for scraped content quality and compliance."""
    
    def __init__(self, 
                 min_text_length: int = 100,
                 max_text_length: int = 1000000,
                 allowed_formats: Optional[List[TextFormat]] = None,
                 required_metadata: Optional[List[str]] = None,
                 forbidden_patterns: Optional[List[str]] = None):
        """Initialize content validator.
        
        Args:
            min_text_length: Minimum text length
            max_text_length: Maximum text length
            allowed_formats: List of allowed text formats
            required_metadata: List of required metadata fields
            forbidden_patterns: List of forbidden text patterns
        """
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.allowed_formats = allowed_formats or list(TextFormat)
        self.required_metadata = required_metadata or []
        self.forbidden_patterns = forbidden_patterns or []
        
        # Compile regex patterns for performance
        self._compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) 
            for pattern in self.forbidden_patterns
        ]
    
    def validate(self, content: ScrapedContent) -> Dict[str, Any]:
        """Validate scraped content.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation result dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'score': 1.0
        }
        
        # Validate text length
        text_length = len(content.text)
        if text_length < self.min_text_length:
            error = f"Text too short: {text_length} < {self.min_text_length}"
            result['errors'].append(error)
            result['valid'] = False
        elif text_length > self.max_text_length:
            error = f"Text too long: {text_length} > {self.max_text_length}"
            result['errors'].append(error)
            result['valid'] = False
        
        # Validate format
        if content.format not in self.allowed_formats:
            error = f"Format not allowed: {content.format}"
            result['errors'].append(error)
            result['valid'] = False
        
        # Validate required metadata
        for field in self.required_metadata:
            if not hasattr(content, field) or getattr(content, field) is None:
                error = f"Required metadata missing: {field}"
                result['errors'].append(error)
                result['valid'] = False
        
        # Validate URL format
        if not self._is_valid_url(content.url):
            error = f"Invalid URL format: {content.url}"
            result['errors'].append(error)
            result['valid'] = False
        
        # Validate title
        if not content.title or not content.title.strip():
            error = "Title is empty or missing"
            result['errors'].append(error)
            result['valid'] = False
        
        # Check for forbidden patterns
        for pattern in self._compiled_patterns:
            if pattern.search(content.text):
                warning = f"Forbidden pattern found: {pattern.pattern}"
                result['warnings'].append(warning)
                result['score'] *= 0.8  # Reduce score but don't fail
        
        # Validate encoding
        if not self._is_valid_encoding(content.text, content.encoding):
            warning = f"Encoding validation failed: {content.encoding}"
            result['warnings'].append(warning)
            result['score'] *= 0.9
        
        # Calculate quality score
        result['score'] = self._calculate_quality_score(content, result)
        
        if not result['valid']:
            raise ValidationError(f"Content validation failed: {', '.join(result['errors'])}")
        
        return result
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
        """
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False
    
    def _is_valid_encoding(self, text: str, encoding: str) -> bool:
        """Check if text can be encoded with specified encoding.
        
        Args:
            text: Text to validate
            encoding: Encoding to check
            
        Returns:
            True if encoding is valid
        """
        try:
            text.encode(encoding)
            return True
        except UnicodeEncodeError:
            return False
    
    def _calculate_quality_score(self, content: ScrapedContent, result: Dict[str, Any]) -> float:
        """Calculate content quality score.
        
        Args:
            content: Content to score
            result: Validation result
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 1.0
        
        # Penalize for warnings
        score *= (0.9 ** len(result['warnings']))
        
        # Reward for good metadata
        if content.author:
            score *= 1.1
        if content.category:
            score *= 1.05
        if content.tags:
            score *= 1.02
        
        # Reward for appropriate text length
        text_length = len(content.text)
        if self.min_text_length <= text_length <= self.max_text_length:
            # Optimal length range
            optimal_length = (self.min_text_length + self.max_text_length) / 2
            length_ratio = min(text_length, optimal_length) / max(text_length, optimal_length)
            score *= (0.8 + 0.2 * length_ratio)
        
        # Penalize for low confidence
        if hasattr(content, 'confidence_score'):
            score *= content.confidence_score
        
        return min(1.0, max(0.0, score))
    
    def validate_batch(self, contents: List[ScrapedContent]) -> Dict[str, Any]:
        """Validate a batch of contents.
        
        Args:
            contents: List of contents to validate
            
        Returns:
            Batch validation result
        """
        results = []
        valid_count = 0
        total_score = 0.0
        
        for content in contents:
            try:
                result = self.validate(content)
                results.append(result)
                if result['valid']:
                    valid_count += 1
                total_score += result['score']
            except ValidationError as e:
                results.append({
                    'valid': False,
                    'errors': [str(e)],
                    'warnings': [],
                    'score': 0.0
                })
        
        return {
            'total_contents': len(contents),
            'valid_contents': valid_count,
            'invalid_contents': len(contents) - valid_count,
            'average_score': total_score / len(contents) if contents else 0.0,
            'results': results
        }


class URLValidator:
    """Validator for URL patterns and compliance."""
    
    def __init__(self, 
                 allowed_domains: Optional[List[str]] = None,
                 forbidden_domains: Optional[List[str]] = None,
                 allowed_schemes: Optional[List[str]] = None,
                 max_url_length: int = 2048):
        """Initialize URL validator.
        
        Args:
            allowed_domains: List of allowed domains
            forbidden_domains: List of forbidden domains
            allowed_schemes: List of allowed URL schemes
            max_url_length: Maximum URL length
        """
        self.allowed_domains = allowed_domains or []
        self.forbidden_domains = forbidden_domains or []
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        self.max_url_length = max_url_length
    
    def validate(self, url: str) -> Dict[str, Any]:
        """Validate a URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"URL parsing failed: {e}")
            return result
        
        # Check scheme
        if parsed.scheme not in self.allowed_schemes:
            result['valid'] = False
            result['errors'].append(f"Scheme not allowed: {parsed.scheme}")
        
        # Check domain
        if self.allowed_domains and parsed.netloc not in self.allowed_domains:
            result['valid'] = False
            result['errors'].append(f"Domain not allowed: {parsed.netloc}")
        
        if self.forbidden_domains and parsed.netloc in self.forbidden_domains:
            result['valid'] = False
            result['errors'].append(f"Domain forbidden: {parsed.netloc}")
        
        # Check URL length
        if len(url) > self.max_url_length:
            result['valid'] = False
            result['errors'].append(f"URL too long: {len(url)} > {self.max_url_length}")
        
        # Check for suspicious patterns
        if self._is_suspicious_url(url):
            result['warnings'].append("URL contains suspicious patterns")
        
        return result
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check if URL contains suspicious patterns.
        
        Args:
            url: URL to check
            
        Returns:
            True if suspicious
        """
        suspicious_patterns = [
            r'javascript:',
            r'data:',
            r'vbscript:',
            r'file:',
            r'ftp:',
            r'<script',
            r'javascript:',
            r'%3Cscript',
            r'%3C%2Fscript%3E'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False


class MetadataValidator:
    """Validator for content metadata."""
    
    def __init__(self, 
                 required_fields: Optional[List[str]] = None,
                 field_validators: Optional[Dict[str, callable]] = None):
        """Initialize metadata validator.
        
        Args:
            required_fields: List of required metadata fields
            field_validators: Dictionary of field-specific validators
        """
        self.required_fields = required_fields or []
        self.field_validators = field_validators or {}
    
    def validate(self, content: ScrapedContent) -> Dict[str, Any]:
        """Validate content metadata.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        for field in self.required_fields:
            if not hasattr(content, field) or getattr(content, field) is None:
                result['valid'] = False
                result['errors'].append(f"Required field missing: {field}")
        
        # Validate field values
        for field, validator in self.field_validators.items():
            if hasattr(content, field):
                try:
                    validator(getattr(content, field))
                except Exception as e:
                    result['warnings'].append(f"Field validation warning for {field}: {e}")
        
        return result
