"""PDF text extraction utilities."""

import io
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFPageInterpreter
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

from ..base import ScrapingError
from ..models import ScrapedContent, TextFormat


class PDFExtractionError(ScrapingError):
    """Exception raised for PDF extraction errors."""
    pass


class PDFExtractor:
    """PDF text extraction utility class."""
    
    def __init__(self, 
                 prefer_pdfminer: bool = True,
                 layout_params: Optional[Dict[str, Any]] = None):
        """Initialize PDF extractor.
        
        Args:
            prefer_pdfminer: Prefer pdfminer over PyPDF2
            layout_params: Parameters for pdfminer layout analysis
        """
        self.prefer_pdfminer = prefer_pdfminer
        self.layout_params = layout_params or {
            'char_margin': 2.0,
            'line_margin': 0.5,
            'word_margin': 0.1,
            'boxes_flow': 0.5,
            'detect_vertical': False
        }
        
        # Check available libraries
        self.pdfminer_available = PDFMINER_AVAILABLE
        self.pypdf2_available = PYPDF2_AVAILABLE
        
        if not self.pdfminer_available and not self.pypdf2_available:
            raise PDFExtractionError("No PDF extraction library available. Install PyPDF2 or pdfminer.six")
    
    def extract_from_bytes(self, pdf_bytes: bytes, 
                          source_url: str = "",
                          source_name: str = "pdf") -> ScrapedContent:
        """Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file content as bytes
            source_url: Source URL
            source_name: Source name
            
        Returns:
            ScrapedContent object
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            # Try pdfminer first if preferred and available
            if self.prefer_pdfminer and self.pdfminer_available:
                text, metadata = self._extract_with_pdfminer(pdf_bytes)
            elif self.pypdf2_available:
                text, metadata = self._extract_with_pypdf2(pdf_bytes)
            else:
                raise PDFExtractionError("No PDF extraction library available")
            
            # Clean extracted text
            text = self._clean_text(text)
            
            # Create ScrapedContent object
            scraped_content = ScrapedContent(
                text=text,
                title=metadata.get('title', 'PDF Document'),
                url=source_url,
                source=source_name,
                format=TextFormat.PDF,
                language=metadata.get('language', 'en'),
                file_size=len(pdf_bytes),
                encoding='utf-8',
                page_count=metadata.get('page_count', 0),
                properties=metadata
            )
            
            return scraped_content
            
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF content: {e}")
    
    def extract_from_file(self, file_path: Path, 
                         source_url: str = "",
                         source_name: str = "pdf") -> ScrapedContent:
        """Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            source_url: Source URL
            source_name: Source name
            
        Returns:
            ScrapedContent object
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            
            return self.extract_from_bytes(pdf_bytes, source_url, source_name)
            
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract PDF from file {file_path}: {e}")
    
    def _extract_with_pdfminer(self, pdf_bytes: bytes) -> tuple[str, Dict[str, Any]]:
        """Extract text using pdfminer.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if not self.pdfminer_available:
            raise PDFExtractionError("pdfminer not available")
        
        try:
            # Create layout parameters
            laparams = LAParams(**self.layout_params)
            
            # Extract text
            text = extract_text(io.BytesIO(pdf_bytes), laparams=laparams)
            
            # Extract metadata
            metadata = self._extract_metadata_with_pdfminer(pdf_bytes)
            
            return text, metadata
            
        except Exception as e:
            raise PDFExtractionError(f"pdfminer extraction failed: {e}")
    
    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> tuple[str, Dict[str, Any]]:
        """Extract text using PyPDF2.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if not self.pypdf2_available:
            raise PDFExtractionError("PyPDF2 not available")
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_parts = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            text = '\n'.join(text_parts)
            
            # Extract metadata
            metadata = self._extract_metadata_with_pypdf2(pdf_reader)
            
            return text, metadata
            
        except Exception as e:
            raise PDFExtractionError(f"PyPDF2 extraction failed: {e}")
    
    def _extract_metadata_with_pdfminer(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Extract metadata using pdfminer.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'creator': '',
            'producer': '',
            'creation_date': '',
            'modification_date': '',
            'page_count': 0
        }
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Get page count
            metadata['page_count'] = len(pdf_reader.pages)
            
            # Get document info
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                metadata.update({
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'creation_date': str(info.get('/CreationDate', '')),
                    'modification_date': str(info.get('/ModDate', ''))
                })
            
        except Exception:
            # If metadata extraction fails, return basic info
            pass
        
        return metadata
    
    def _extract_metadata_with_pypdf2(self, pdf_reader) -> Dict[str, Any]:
        """Extract metadata using PyPDF2.
        
        Args:
            pdf_reader: PyPDF2 PdfReader object
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'title': '',
            'author': '',
            'subject': '',
            'creator': '',
            'producer': '',
            'creation_date': '',
            'modification_date': '',
            'page_count': len(pdf_reader.pages)
        }
        
        try:
            # Get document info
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                metadata.update({
                    'title': info.get('/Title', ''),
                    'author': info.get('/Author', ''),
                    'subject': info.get('/Subject', ''),
                    'creator': info.get('/Creator', ''),
                    'producer': info.get('/Producer', ''),
                    'creation_date': str(info.get('/CreationDate', '')),
                    'modification_date': str(info.get('/ModDate', ''))
                })
            
        except Exception:
            # If metadata extraction fails, return basic info
            pass
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted PDF text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Remove multiple consecutive newlines
        import re
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Remove page numbers and headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                cleaned_lines.append('')
                continue
            
            # Skip lines that look like page numbers
            if re.match(r'^\d+$', line):
                continue
            
            # Skip lines that look like headers/footers
            if (len(line) < 3 or 
                re.match(r'^Page \d+', line) or
                re.match(r'^\d+ of \d+$', line) or
                line.lower() in ['page', 'of', 'chapter', 'section']):
                continue
            
            cleaned_lines.append(line)
        
        # Join lines and clean up
        text = '\n'.join(cleaned_lines)
        
        # Remove extra whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_pages(self, pdf_bytes: bytes, 
                     page_numbers: Optional[List[int]] = None) -> Dict[int, str]:
        """Extract text from specific pages.
        
        Args:
            pdf_bytes: PDF file content as bytes
            page_numbers: List of page numbers to extract (0-indexed)
            
        Returns:
            Dictionary mapping page numbers to text content
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            if self.prefer_pdfminer and self.pdfminer_available:
                return self._extract_pages_with_pdfminer(pdf_bytes, page_numbers)
            elif self.pypdf2_available:
                return self._extract_pages_with_pypdf2(pdf_bytes, page_numbers)
            else:
                raise PDFExtractionError("No PDF extraction library available")
                
        except Exception as e:
            raise PDFExtractionError(f"Failed to extract pages: {e}")
    
    def _extract_pages_with_pdfminer(self, pdf_bytes: bytes, 
                                   page_numbers: Optional[List[int]] = None) -> Dict[int, str]:
        """Extract specific pages using pdfminer.
        
        Args:
            pdf_bytes: PDF file content as bytes
            page_numbers: List of page numbers to extract
            
        Returns:
            Dictionary mapping page numbers to text content
        """
        if not self.pdfminer_available:
            raise PDFExtractionError("pdfminer not available")
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            resource_manager = PDFResourceManager()
            
            # Get all pages if no specific pages requested
            if page_numbers is None:
                page_numbers = list(range(len(list(PDFPage.get_pages(pdf_file)))))
                pdf_file.seek(0)  # Reset file pointer
            
            page_texts = {}
            
            for page_num in page_numbers:
                try:
                    # Create text converter for this page
                    output_string = io.StringIO()
                    converter = TextConverter(resource_manager, output_string, laparams=LAParams(**self.layout_params))
                    page_interpreter = PDFPageInterpreter(resource_manager, converter)
                    
                    # Extract text from specific page
                    for page in PDFPage.get_pages(pdf_file, pagenos=[page_num]):
                        page_interpreter.process_page(page)
                        break
                    
                    # Get extracted text
                    text = output_string.getvalue()
                    page_texts[page_num] = self._clean_text(text)
                    
                    # Clean up
                    converter.close()
                    output_string.close()
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract page {page_num}: {e}")
                    page_texts[page_num] = ""
            
            return page_texts
            
        except Exception as e:
            raise PDFExtractionError(f"pdfminer page extraction failed: {e}")
    
    def _extract_pages_with_pypdf2(self, pdf_bytes: bytes, 
                                 page_numbers: Optional[List[int]] = None) -> Dict[int, str]:
        """Extract specific pages using PyPDF2.
        
        Args:
            pdf_bytes: PDF file content as bytes
            page_numbers: List of page numbers to extract
            
        Returns:
            Dictionary mapping page numbers to text content
        """
        if not self.pypdf2_available:
            raise PDFExtractionError("PyPDF2 not available")
        
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Get all pages if no specific pages requested
            if page_numbers is None:
                page_numbers = list(range(len(pdf_reader.pages)))
            
            page_texts = {}
            
            for page_num in page_numbers:
                try:
                    if 0 <= page_num < len(pdf_reader.pages):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        page_texts[page_num] = self._clean_text(text)
                    else:
                        page_texts[page_num] = ""
                        
                except Exception as e:
                    self.logger.warning(f"Failed to extract page {page_num}: {e}")
                    page_texts[page_num] = ""
            
            return page_texts
            
        except Exception as e:
            raise PDFExtractionError(f"PyPDF2 page extraction failed: {e}")
    
    def get_page_count(self, pdf_bytes: bytes) -> int:
        """Get the number of pages in the PDF.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Number of pages
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            if self.pypdf2_available:
                pdf_file = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                return len(pdf_reader.pages)
            elif self.pdfminer_available:
                pdf_file = io.BytesIO(pdf_bytes)
                return len(list(PDFPage.get_pages(pdf_file)))
            else:
                raise PDFExtractionError("No PDF extraction library available")
                
        except Exception as e:
            raise PDFExtractionError(f"Failed to get page count: {e}")
    
    def is_pdf(self, data: bytes) -> bool:
        """Check if data is a valid PDF.
        
        Args:
            data: Data to check
            
        Returns:
            True if data is a valid PDF
        """
        return data.startswith(b'%PDF-')
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about available extraction methods.
        
        Returns:
            Dictionary of extraction information
        """
        return {
            'pdfminer_available': self.pdfminer_available,
            'pypdf2_available': self.pypdf2_available,
            'prefer_pdfminer': self.prefer_pdfminer,
            'layout_params': self.layout_params
        }
