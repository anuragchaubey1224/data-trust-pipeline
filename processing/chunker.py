"""
Content Chunking Module for Data Trust Pipeline

This module provides text chunking functionality for splitting long content
into overlapping chunks. This is essential for processing long documents
while maintaining context continuity between chunks.

Author: Data Trust Pipeline Team
"""

import logging
from typing import List


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ContentChunker:
    """
    A content chunking utility for splitting long text into overlapping chunks.
    
    This class splits text into fixed-size chunks with overlapping windows to
    maintain context continuity. This is useful for processing long documents
    in downstream NLP tasks while preserving semantic relationships.
    
    Usage:
        >>> chunker = ContentChunker()
        >>> text = "This is a long article " * 100
        >>> chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
        >>> print(f"Created {len(chunks)} chunks")
        Created 4 chunks
    
    Attributes:
        logger: Logger instance for tracking chunking operations.
        default_chunk_size: Default number of words per chunk (300).
        default_overlap: Default number of overlapping words (50).
    """
    
    def __init__(self, default_chunk_size: int = 300, default_overlap: int = 50):
        """
        Initialize the ContentChunker.
        
        Args:
            default_chunk_size: Default number of words per chunk. Default: 300.
            default_overlap: Default number of overlapping words. Default: 50.
        
        Raises:
            ValueError: If default_overlap >= default_chunk_size.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate parameters
        if default_overlap >= default_chunk_size:
            raise ValueError(
                f"Overlap ({default_overlap}) must be less than chunk_size ({default_chunk_size})"
            )
        
        self.default_chunk_size = default_chunk_size
        self.default_overlap = default_overlap
        
        self.logger.info(
            f"ContentChunker initialized (chunk_size={default_chunk_size}, overlap={default_overlap})"
        )
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks of fixed word count.
        
        This method divides long text into manageable chunks while maintaining
        context through overlapping windows. The overlap ensures that semantic
        relationships at chunk boundaries are preserved.
        
        Algorithm:
        1. Split text into word list
        2. Extract chunks of chunk_size words
        3. Move forward by (chunk_size - overlap) words
        4. Continue until all text is processed
        
        Args:
            text: Text string to split into chunks.
            chunk_size: Number of words per chunk. If None, uses default (300).
            overlap: Number of overlapping words. If None, uses default (50).
        
        Returns:
            List of text chunks as strings. Empty list if text is empty.
        
        Examples:
            >>> chunker = ContentChunker()
            >>> text = "word " * 500
            >>> chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
            >>> len(chunks)
            3
            
            >>> chunker.chunk_text("Short text")
            ['Short text']
            
            >>> chunker.chunk_text("")
            []
        """
        # Use defaults if not specified
        if chunk_size is None:
            chunk_size = self.default_chunk_size
        if overlap is None:
            overlap = self.default_overlap
        
        # Validate parameters
        if overlap >= chunk_size:
            self.logger.warning(
                f"Overlap ({overlap}) >= chunk_size ({chunk_size}). "
                f"Adjusting overlap to {chunk_size - 1}"
            )
            overlap = chunk_size - 1
        
        if overlap < 0:
            self.logger.warning(f"Negative overlap ({overlap}). Setting overlap to 0")
            overlap = 0
        
        # Validate input
        if text is None:
            self.logger.warning("Input text is None")
            return []
        
        if not isinstance(text, str):
            self.logger.warning(f"Converting non-string input to string: {type(text)}")
            text = str(text)
        
        # Remove extra whitespace
        text = text.strip()
        
        # Check if text is empty
        if not text:
            self.logger.warning("Input text is empty")
            return []
        
        # Split text into words
        words = text.split()
        total_words = len(words)
        
        self.logger.info(
            f"Creating content chunks (text: {total_words} words, "
            f"chunk_size: {chunk_size}, overlap: {overlap})"
        )
        
        # If text is shorter than chunk_size, return as single chunk
        if total_words <= chunk_size:
            self.logger.info(f"Text too short for chunking ({total_words} words). Returning single chunk")
            return [text]
        
        # Create chunks
        chunks = []
        start_idx = 0
        step_size = chunk_size - overlap
        
        while start_idx < total_words:
            # Extract chunk
            end_idx = min(start_idx + chunk_size, total_words)
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Move to next chunk
            start_idx += step_size
            
            # Break if we've reached the end
            if end_idx >= total_words:
                break
        
        self.logger.info(f"Generated {len(chunks)} chunks")
        
        return chunks
    
    def chunk_text_with_metadata(
        self, 
        text: str, 
        chunk_size: int = None, 
        overlap: int = None
    ) -> List[dict]:
        """
        Split text into chunks and return with metadata.
        
        Similar to chunk_text(), but returns chunk information including
        word counts, positions, and overlap indicators.
        
        Args:
            text: Text string to split into chunks.
            chunk_size: Number of words per chunk. If None, uses default.
            overlap: Number of overlapping words. If None, uses default.
        
        Returns:
            List of dictionaries containing:
            - 'chunk_id': Chunk index (1-based)
            - 'text': Chunk text
            - 'word_count': Number of words in chunk
            - 'start_word': Starting word position in original text
            - 'end_word': Ending word position in original text
        
        Example:
            >>> chunker = ContentChunker()
            >>> text = "word " * 400
            >>> chunks = chunker.chunk_text_with_metadata(text, chunk_size=200, overlap=50)
            >>> chunks[0]
            {
                'chunk_id': 1,
                'text': 'word word word...',
                'word_count': 200,
                'start_word': 0,
                'end_word': 199
            }
        """
        # Use defaults if not specified
        if chunk_size is None:
            chunk_size = self.default_chunk_size
        if overlap is None:
            overlap = self.default_overlap
        
        # Get basic chunks
        chunk_texts = self.chunk_text(text, chunk_size, overlap)
        
        if not chunk_texts:
            return []
        
        # Add metadata
        words = text.split()
        chunks_with_metadata = []
        start_idx = 0
        step_size = chunk_size - overlap
        
        for i, chunk_text in enumerate(chunk_texts, 1):
            chunk_words = chunk_text.split()
            end_idx = start_idx + len(chunk_words) - 1
            
            chunk_info = {
                'chunk_id': i,
                'text': chunk_text,
                'word_count': len(chunk_words),
                'start_word': start_idx,
                'end_word': end_idx
            }
            
            chunks_with_metadata.append(chunk_info)
            start_idx += step_size
        
        self.logger.info(f"Generated {len(chunks_with_metadata)} chunks with metadata")
        
        return chunks_with_metadata
    
    def get_chunk_statistics(self, chunks: List[str]) -> dict:
        """
        Calculate statistics for a list of chunks.
        
        Args:
            chunks: List of chunk strings.
        
        Returns:
            Dictionary containing:
            - 'total_chunks': Number of chunks
            - 'total_words': Total words across all chunks
            - 'avg_words_per_chunk': Average words per chunk
            - 'min_words': Minimum words in a chunk
            - 'max_words': Maximum words in a chunk
        
        Example:
            >>> chunker = ContentChunker()
            >>> chunks = ["word " * 300, "word " * 300, "word " * 150]
            >>> stats = chunker.get_chunk_statistics(chunks)
            >>> stats['total_chunks']
            3
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_words': 0,
                'avg_words_per_chunk': 0,
                'min_words': 0,
                'max_words': 0
            }
        
        word_counts = [len(chunk.split()) for chunk in chunks]
        total_words = sum(word_counts)
        
        stats = {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'avg_words_per_chunk': total_words / len(chunks),
            'min_words': min(word_counts),
            'max_words': max(word_counts)
        }
        
        return stats
    
    def batch_chunk_texts(
        self, 
        texts: List[str], 
        chunk_size: int = None, 
        overlap: int = None
    ) -> List[List[str]]:
        """
        Chunk multiple texts in batch.
        
        This method processes multiple texts and returns a list of chunk lists,
        one for each input text. Useful for processing multiple scraped articles
        or documents at once.
        
        Args:
            texts: List of text strings to chunk.
            chunk_size: Number of words per chunk. If None, uses default.
            overlap: Number of overlapping words. If None, uses default.
        
        Returns:
            List of chunk lists, one per input text.
        
        Example:
            >>> chunker = ContentChunker()
            >>> texts = ["Long text 1 " * 400, "Long text 2 " * 500]
            >>> batch_results = chunker.batch_chunk_texts(texts, chunk_size=300, overlap=50)
            >>> len(batch_results)
            2
        """
        if not texts:
            self.logger.warning("Empty texts list provided")
            return []
        
        self.logger.info(f"Chunking batch of {len(texts)} texts")
        
        results = []
        for i, text in enumerate(texts):
            self.logger.debug(f"Processing text {i+1}/{len(texts)}")
            chunks = self.chunk_text(text, chunk_size, overlap)
            results.append(chunks)
        
        total_chunks = sum(len(chunks) for chunks in results)
        self.logger.info(f"Batch chunking complete: {total_chunks} total chunks from {len(texts)} texts")
        
        return results
