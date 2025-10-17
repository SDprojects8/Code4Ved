"""Text cleaning utilities for scraped content."""

import re
import unicodedata
from typing import List, Optional, Set, Tuple


class TextCleaner:
    """Utility class for cleaning and normalizing text content."""
    
    def __init__(self, 
                 remove_extra_whitespace: bool = True,
                 normalize_unicode: bool = True,
                 remove_control_chars: bool = True,
                 preserve_line_breaks: bool = False,
                 min_line_length: int = 10):
        """Initialize text cleaner.
        
        Args:
            remove_extra_whitespace: Remove extra whitespace
            normalize_unicode: Normalize Unicode characters
            remove_control_chars: Remove control characters
            preserve_line_breaks: Preserve line breaks
            min_line_length: Minimum line length to keep
        """
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_unicode = normalize_unicode
        self.remove_control_chars = remove_control_chars
        self.preserve_line_breaks = preserve_line_breaks
        self.min_line_length = min_line_length
        
        # Common HTML entities
        self.html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' ',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
        }
        
        # Common control characters to remove
        self.control_chars = set(range(0, 32)) - {9, 10, 13}  # Keep tab, newline, carriage return
    
    def clean(self, text: str) -> str:
        """Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = self._decode_html_entities(text)
        
        # Normalize Unicode
        if self.normalize_unicode:
            text = self._normalize_unicode(text)
        
        # Remove control characters
        if self.remove_control_chars:
            text = self._remove_control_chars(text)
        
        # Clean whitespace
        if self.remove_extra_whitespace:
            text = self._clean_whitespace(text)
        
        # Remove short lines
        text = self._remove_short_lines(text)
        
        return text.strip()
    
    def _decode_html_entities(self, text: str) -> str:
        """Decode HTML entities in text.
        
        Args:
            text: Text with HTML entities
            
        Returns:
            Text with decoded entities
        """
        for entity, char in self.html_entities.items():
            text = text.replace(entity, char)
        
        # Handle numeric entities
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Normalize to NFC (Canonical Decomposition, followed by Canonical Composition)
        text = unicodedata.normalize('NFC', text)
        
        # Replace common Unicode variants
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '--',  # em dash
            '\u2018': "'",  # left single quotation mark
            '\u2019': "'",  # right single quotation mark
            '\u201c': '"',  # left double quotation mark
            '\u201d': '"',  # right double quotation mark
            '\u2026': '...',  # horizontal ellipsis
            '\u00a0': ' ',  # non-breaking space
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        return text
    
    def _remove_control_chars(self, text: str) -> str:
        """Remove control characters from text.
        
        Args:
            text: Text to clean
            
        Returns:
            Text without control characters
        """
        if self.preserve_line_breaks:
            # Keep newlines and carriage returns
            allowed_chars = {9, 10, 13}  # tab, newline, carriage return
            control_chars = set(range(0, 32)) - allowed_chars
        else:
            control_chars = self.control_chars
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) not in control_chars)
        
        return text
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean whitespace in text.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with cleaned whitespace
        """
        if self.preserve_line_breaks:
            # Preserve line breaks but clean other whitespace
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Clean whitespace within each line
                cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
                if cleaned_line:  # Only keep non-empty lines
                    cleaned_lines.append(cleaned_line)
            
            return '\n'.join(cleaned_lines)
        else:
            # Remove all extra whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
    
    def _remove_short_lines(self, text: str) -> str:
        """Remove lines that are too short.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with short lines removed
        """
        if not self.preserve_line_breaks:
            return text
        
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            if len(line.strip()) >= self.min_line_length:
                filtered_lines.append(line)
            elif line.strip():  # Keep non-empty short lines if they're not too short
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def extract_metadata(self, text: str) -> dict:
        """Extract metadata from text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of extracted metadata
        """
        metadata = {
            'word_count': len(text.split()),
            'char_count': len(text),
            'line_count': len(text.split('\n')),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'has_numbers': bool(re.search(r'\d', text)),
            'has_punctuation': bool(re.search(r'[.!?]', text)),
            'language_indicators': self._detect_language_indicators(text),
        }
        
        return metadata
    
    def _detect_language_indicators(self, text: str) -> List[str]:
        """Detect language indicators in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected language indicators
        """
        indicators = []
        
        # Sanskrit indicators
        sanskrit_patterns = [
            r'[अ-ह]',  # Devanagari script
            r'[a-zA-Z]*[āīūṛṝḷḹēōṃḥ]',  # IAST transliteration
            r'[a-zA-Z]*[āīūṛṝḷḹēōṃḥ]',  # Extended IAST
        ]
        
        for pattern in sanskrit_patterns:
            if re.search(pattern, text):
                indicators.append('sanskrit')
                break
        
        # English indicators
        english_patterns = [
            r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b',
            r'\b[a-zA-Z]{3,}\b',  # Common English words
        ]
        
        english_matches = sum(1 for pattern in english_patterns if re.search(pattern, text, re.IGNORECASE))
        if english_matches > 0:
            indicators.append('english')
        
        # Hindi indicators
        hindi_patterns = [
            r'[क-ह]',  # Hindi Devanagari
            r'[ा-ौ]',  # Hindi matras
        ]
        
        for pattern in hindi_patterns:
            if re.search(pattern, text):
                indicators.append('hindi')
                break
        
        return indicators
    
    def clean_html(self, html: str) -> str:
        """Clean HTML content and extract text.
        
        Args:
            html: HTML content
            
        Returns:
            Cleaned text content
        """
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        html = re.sub(r'<[^>]+>', '', html)
        
        # Clean the resulting text
        return self.clean(html)
    
    def clean_pdf_text(self, text: str) -> str:
        """Clean text extracted from PDF.
        
        Args:
            text: PDF text content
            
        Returns:
            Cleaned text
        """
        # Remove page numbers and headers/footers
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+ of \d+$', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Clean the text
        return self.clean(text)
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def extract_keywords(self, text: str, min_length: int = 3, max_words: int = 50) -> List[str]:
        """Extract keywords from text.
        
        Args:
            text: Text to analyze
            min_length: Minimum word length
            max_words: Maximum number of keywords
            
        Returns:
            List of keywords
        """
        # Clean text
        cleaned_text = self.clean(text)
        
        # Split into words
        words = re.findall(r'\b[a-zA-Z]+\b', cleaned_text.lower())
        
        # Filter by length
        words = [word for word in words if len(word) >= min_length]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_words]]
