"""
Text Cleaning Module for Data Trust Pipeline

This module provides text cleaning and normalization functionality for scraped content.
It prepares raw text for downstream NLP processing such as language detection,
topic tagging, and text chunking.

"""

import re
import logging
import unicodedata
from typing import Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TextCleaner:
    """
    A comprehensive text cleaning utility for normalizing scraped content.
    
    This class provides methods to clean and normalize text by removing HTML tags,
    normalizing whitespace and unicode characters, and preparing text for NLP tasks.
    
    Usage:
        >>> cleaner = TextCleaner()
        >>> raw_text = "  Hello    world\\n\\n<p>This is text</p>  "
        >>> cleaned = cleaner.clean_text(raw_text)
        >>> print(cleaned)
        'Hello world This is text'
    
    Attributes:
        logger: Logger instance for tracking cleaning operations.
    """
    
    def __init__(self):
        """Initialize the TextCleaner with a configured logger."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("TextCleaner initialized")
    
    def clean_text(self, text: str) -> str:
        """
        Main entry point for text cleaning pipeline.
        
        Applies a series of cleaning operations in the following order:
        1. Normalize unicode characters
        2. Remove HTML tags
        3. Normalize whitespace
        4. Remove extra newlines
        5. Strip leading and trailing spaces
        
        Args:
            text: Raw text string to be cleaned.
        
        Returns:
            Cleaned and normalized text string.
        
        Raises:
            ValueError: If input text is None.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> messy = "\\n\\n  Hello    world \\n\\n <p>This is text</p> "
            >>> clean = cleaner.clean_text(messy)
            >>> print(clean)
            'Hello world This is text'
        """
        if text is None:
            raise ValueError("Input text cannot be None")
        
        if not isinstance(text, str):
            self.logger.warning(f"Converting non-string input to string: {type(text)}")
            text = str(text)
        
        if not text.strip():
            self.logger.warning("Input text is empty or whitespace only")
            return ""
        
        self.logger.info("Cleaning text (length: %d characters)", len(text))
        
        # Apply cleaning pipeline
        text = self.normalize_unicode(text)
        text = self.remove_html_tags(text)
        text = self._remove_extra_newlines(text)  # Remove newlines before whitespace norm
        text = self.normalize_whitespace(text)
        text = text.strip()
        
        self.logger.info("Text cleaning complete (final length: %d characters)", len(text))
        
        return text
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normalize unicode characters to their standard form.
        
        Converts unicode characters to NFKD (Compatibility Decomposition) form,
        which is useful for consistent text processing and comparison.
        
        Args:
            text: Text string with potentially non-standard unicode.
        
        Returns:
            Text with normalized unicode characters.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> text_with_unicode = "café"  # May contain combining characters
            >>> normalized = cleaner.normalize_unicode(text_with_unicode)
        """
        if not text:
            return text
        
        self.logger.debug("Normalizing unicode characters")
        
        # Normalize to NFKD form (Compatibility Decomposition)
        normalized = unicodedata.normalize('NFKD', text)
        
        # Encode to ASCII, ignoring characters that can't be represented
        # Then decode back to string
        # This removes accents and special unicode characters
        try:
            # Try to keep unicode characters if possible
            normalized = unicodedata.normalize('NFKC', normalized)
        except Exception as e:
            self.logger.warning(f"Unicode normalization warning: {e}")
        
        return normalized
    
    def remove_html_tags(self, text: str) -> str:
        """
        Remove HTML tags and entities from text.
        
        Removes common HTML tags like <p>, <div>, <br>, <span>, etc.
        Also handles HTML entities like &nbsp;, &amp;, etc.
        
        Args:
            text: Text string potentially containing HTML markup.
        
        Returns:
            Text with HTML tags and entities removed.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> html_text = "<p>Hello <strong>world</strong></p>"
            >>> clean = cleaner.remove_html_tags(html_text)
            >>> print(clean)
            'Hello world'
        """
        if not text:
            return text
        
        self.logger.debug("Removing HTML remnants")
        
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove script and style tags with their content
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Replace common HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&apos;': "'",
            '&mdash;': '—',
            '&ndash;': '–',
            '&rsquo;': "'",
            '&lsquo;': "'",
            '&rdquo;': '"',
            '&ldquo;': '"',
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Remove any remaining HTML entities (numeric or named)
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'&#\d+;', ' ', text)
        
        return text
    
    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace by replacing multiple spaces with a single space.
        
        Converts tabs, multiple spaces, and other whitespace characters
        into single spaces for consistent formatting.
        
        Args:
            text: Text string with irregular whitespace.
        
        Returns:
            Text with normalized whitespace.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> text = "Hello    world\\t\\ttest"
            >>> normalized = cleaner.normalize_whitespace(text)
            >>> print(normalized)
            'Hello world test'
        """
        if not text:
            return text
        
        self.logger.debug("Normalizing whitespace")
        
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        return text
    
    def _remove_extra_newlines(self, text: str) -> str:
        """
        Remove excessive newlines and blank lines.
        
        Replaces multiple consecutive newlines with a single space for inline content,
        or preserves paragraph breaks. For basic cleaning, converts all newlines to spaces.
        
        Args:
            text: Text string with potentially excessive newlines.
        
        Returns:
            Text with normalized newlines.
        
        Note:
            This is a private method used internally by clean_text().
        """
        if not text:
            return text
        
        # Replace Windows-style line endings with Unix-style
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # For simple text cleaning, replace all newlines with spaces
        # This is appropriate for content that was originally inline but had HTML/formatting
        text = text.replace('\n', ' ')
        
        return text
    
    def clean_batch(self, texts: list[str]) -> list[str]:
        """
        Clean a batch of text strings.
        
        Convenience method for cleaning multiple texts efficiently.
        
        Args:
            texts: List of text strings to be cleaned.
        
        Returns:
            List of cleaned text strings.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> texts = ["  text 1  ", "<p>text 2</p>"]
            >>> cleaned = cleaner.clean_batch(texts)
            >>> print(cleaned)
            ['text 1', 'text 2']
        """
        self.logger.info(f"Cleaning batch of {len(texts)} texts")
        
        cleaned_texts = []
        for i, text in enumerate(texts):
            try:
                cleaned = self.clean_text(text)
                cleaned_texts.append(cleaned)
            except Exception as e:
                self.logger.error(f"Error cleaning text {i}: {e}")
                cleaned_texts.append("")  # Append empty string on error
        
        return cleaned_texts
    
    def get_text_stats(self, text: str) -> dict:
        """
        Get statistics about the text before and after cleaning.
        
        Args:
            text: Original text string.
        
        Returns:
            Dictionary containing statistics about the cleaning process.
        
        Example:
            >>> cleaner = TextCleaner()
            >>> stats = cleaner.get_text_stats("  Hello   world  ")
            >>> print(stats)
            {'original_length': 17, 'cleaned_length': 11, 'reduction_pct': 35.29}
        """
        if not text:
            return {
                'original_length': 0,
                'cleaned_length': 0,
                'reduction_pct': 0.0
            }
        
        original_length = len(text)
        cleaned_text = self.clean_text(text)
        cleaned_length = len(cleaned_text)
        
        reduction_pct = ((original_length - cleaned_length) / original_length * 100) if original_length > 0 else 0.0
        
        return {
            'original_length': original_length,
            'cleaned_length': cleaned_length,
            'reduction_pct': round(reduction_pct, 2),
            'html_tags_found': bool(re.search(r'<[^>]+>', text)),
            'excessive_whitespace': bool(re.search(r'  +|\t', text)),
            'excessive_newlines': bool(re.search(r'\n\s*\n\s*\n+', text)),
        }


if __name__ == "__main__":
    # Quick test
    cleaner = TextCleaner()
    
    test_text = "\n\n  Hello    world \n\n <p>This is text</p> "
    print("Original:", repr(test_text))
    
    cleaned = cleaner.clean_text(test_text)
    print("Cleaned:", repr(cleaned))
    
    stats = cleaner.get_text_stats(test_text)
    print("Stats:", stats)
