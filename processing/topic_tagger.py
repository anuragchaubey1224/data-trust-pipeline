"""
Topic Tagging Module for Data Trust Pipeline

This module provides topic extraction functionality for cleaned text content.
It uses KeyBERT to automatically extract relevant keywords and topics from text,
which helps in content categorization and semantic understanding.

Author: Data Trust Pipeline Team
"""

import logging
from typing import List, Optional

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    logging.warning("keybert library not installed. Install with: pip install keybert sentence-transformers")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TopicTagger:
    """
    A topic extraction utility for extracting keywords and topics from text.
    
    This class uses KeyBERT (BERT-based keyword extraction) to identify the most
    relevant topics and keywords from cleaned text content. It supports both
    single-word and multi-word phrases.
    
    Usage:
        >>> tagger = TopicTagger()
        >>> topics = tagger.extract_topics("Gut health is important for digestion")
        >>> print(topics)
        ['gut health', 'digestion', 'health']
    
    Attributes:
        logger: Logger instance for tracking extraction operations.
        model: KeyBERT model instance for topic extraction.
        max_words: Maximum number of words to process (default: 1500).
        min_text_length: Minimum text length for extraction (default: 50).
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", max_words: int = 1500, min_text_length: int = 50):
        """
        Initialize the TopicTagger with a KeyBERT model.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
                       Default: "all-MiniLM-L6-v2" (lightweight and fast).
            max_words: Maximum number of words to process from text.
                      Large texts will be truncated. Default: 1500.
            min_text_length: Minimum number of characters required for extraction.
                           Texts shorter than this return empty list. Default: 50.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_words = max_words
        self.min_text_length = min_text_length
        self.model = None
        
        if not KEYBERT_AVAILABLE:
            self.logger.error("keybert library not available. Topic tagging will not work.")
            self.logger.info("Install with: pip install keybert sentence-transformers")
        else:
            try:
                self.logger.info("⏳ Initializing KeyBERT model...")
                self.logger.info(f"   Model: {model_name}")
                self.logger.info("   First run: downloading 420MB model (one-time)")
                self.logger.info("   This may take 2-5 minutes on slow connections")
                
                self.model = KeyBERT(model=model_name)
                
                self.logger.info("✓ Model loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize KeyBERT model: {e}")
                self.model = None
    
    def extract_topics(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract top topic keywords from text using KeyBERT.
        
        This method identifies the most relevant keywords and key phrases from
        the input text. It supports both single words and two-word phrases
        (ngram_range=(1, 2)).
        
        For large texts (e.g., long YouTube transcripts), only the first
        1500 words are processed to ensure reasonable performance.
        
        Args:
            text: Text string to extract topics from.
            top_n: Number of top keywords to extract. Default: 5.
        
        Returns:
            List of topic keywords/phrases, ordered by relevance.
            Returns empty list if extraction fails or text is invalid.
        
        Examples:
            >>> tagger = TopicTagger()
            >>> text = "Gut health plays a crucial role in digestion and immune function."
            >>> topics = tagger.extract_topics(text, top_n=3)
            >>> print(topics)
            ['gut health', 'immune function', 'digestion']
            
            >>> tagger.extract_topics("", top_n=5)
            []
            
            >>> tagger.extract_topics("hi", top_n=5)
            []
        """
        # Check if model is available
        if not KEYBERT_AVAILABLE or self.model is None:
            self.logger.error("KeyBERT model not available")
            return []
        
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
        
        # Check minimum length
        if len(text) < self.min_text_length:
            self.logger.warning(
                f"Text too short for keyword extraction (length={len(text)}, min={self.min_text_length})"
            )
            return []
        
        # Truncate text to first N words for performance
        text = self._truncate_to_words(text, self.max_words)
        
        # Extract keywords
        try:
            self.logger.info(f"Extracting {top_n} topic tags (text length: {len(text)} chars)")
            
            # Extract keywords using KeyBERT
            # ngram_range=(1, 2) allows single words and two-word phrases
            # top_n specifies how many keywords to extract
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n,
                use_maxsum=True,  # Use Max Sum Similarity for diversity
                nr_candidates=20   # Number of candidates to consider
            )
            
            # Extract just the keyword strings (ignore scores)
            topic_tags = [keyword for keyword, score in keywords]
            
            self.logger.info(f"Extracted {len(topic_tags)} topics: {topic_tags}")
            return topic_tags
        
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return []
    
    def extract_topics_with_scores(self, text: str, top_n: int = 5) -> List[tuple]:
        """
        Extract topics with confidence scores.
        
        Similar to extract_topics(), but returns tuples of (keyword, score)
        where score indicates the relevance of the keyword to the document.
        
        Args:
            text: Text string to extract topics from.
            top_n: Number of top keywords to extract. Default: 5.
        
        Returns:
            List of tuples (keyword, score), ordered by relevance.
            Returns empty list if extraction fails or text is invalid.
        
        Example:
            >>> tagger = TopicTagger()
            >>> text = "The microbiome affects gut health and digestion."
            >>> topics = tagger.extract_topics_with_scores(text, top_n=3)
            >>> print(topics)
            [('gut health', 0.68), ('microbiome', 0.54), ('digestion', 0.49)]
        """
        # Check if model is available
        if not KEYBERT_AVAILABLE or self.model is None:
            self.logger.error("KeyBERT model not available")
            return []
        
        # Validate input
        if not text or not isinstance(text, str):
            self.logger.warning("Invalid input text")
            return []
        
        text = text.strip()
        
        if not text or len(text) < self.min_text_length:
            self.logger.warning("Text empty or too short for extraction")
            return []
        
        # Truncate text
        text = self._truncate_to_words(text, self.max_words)
        
        # Extract keywords with scores
        try:
            self.logger.info(f"Extracting {top_n} topics with scores")
            
            keywords = self.model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                stop_words='english',
                top_n=top_n,
                use_maxsum=True,
                nr_candidates=20
            )
            
            self.logger.info(f"Extracted {len(keywords)} topics with scores")
            return keywords
        
        except Exception as e:
            self.logger.error(f"Topic extraction with scores failed: {e}")
            return []
    
    def _truncate_to_words(self, text: str, max_words: int) -> str:
        """
        Truncate text to a maximum number of words.
        
        This is important for performance when processing very long texts
        like YouTube transcripts or lengthy articles.
        
        Args:
            text: Text to truncate.
            max_words: Maximum number of words to keep.
        
        Returns:
            Truncated text string.
        """
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        self.logger.info(f"Truncating text from {len(words)} to {max_words} words")
        return ' '.join(words[:max_words])
    
    def batch_extract_topics(self, texts: List[str], top_n: int = 5) -> List[List[str]]:
        """
        Extract topics from multiple texts in batch.
        
        This method processes multiple texts and returns a list of topic lists,
        one for each input text. Useful for processing multiple scraped articles
        or documents at once.
        
        Args:
            texts: List of text strings to process.
            top_n: Number of topics to extract per text. Default: 5.
        
        Returns:
            List of topic lists, one per input text.
        
        Example:
            >>> tagger = TopicTagger()
            >>> texts = [
            ...     "Gut health is important for digestion",
            ...     "Machine learning uses neural networks"
            ... ]
            >>> batch_results = tagger.batch_extract_topics(texts, top_n=3)
            >>> print(batch_results)
            [['gut health', 'digestion', 'health'],
             ['machine learning', 'neural networks', 'learning']]
        """
        if not texts:
            self.logger.warning("Empty texts list provided")
            return []
        
        self.logger.info(f"Extracting topics for batch of {len(texts)} texts")
        
        results = []
        for i, text in enumerate(texts):
            self.logger.debug(f"Processing text {i+1}/{len(texts)}")
            topics = self.extract_topics(text, top_n=top_n)
            results.append(topics)
        
        self.logger.info(f"Batch extraction complete: {len(results)} results")
        return results
