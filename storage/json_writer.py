"""
JSON Storage Writer for Data Trust Pipeline

This module provides JSON storage functionality for saving processed content
to structured JSON files following a standardized schema.

"""

import json
import logging
from typing import Dict, List, Any
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class JSONStorageWriter:
    """
    A JSON storage utility for saving processed content data.
    
    This class normalizes pipeline output data to a standardized schema
    and writes it to JSON files for storage and further analysis.
    
    Required Schema Fields:
    - source_url: URL of the content source
    - source_type: Type of source (blog, youtube, pubmed)
    - author: Author name/credentials
    - published_date: Publication date
    - language: Language code (e.g., 'en', 'es')
    - region: Geographic region (default: 'global')
    - topic_tags: List of extracted topic keywords
    - trust_score: Trust credibility score (0.0-1.0)
    - content_chunks: List of text chunks
    
    Usage:
        >>> writer = JSONStorageWriter()
        >>> data = [{"source_url": "...", "content": "...", ...}]
        >>> writer.write_json(data, "output/data.json")
        INFO: Stored 1 sources successfully
    
    Attributes:
        logger: Logger instance for tracking storage operations.
    """
    
    def __init__(self):
        """Initialize the JSONStorageWriter."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("JSONStorageWriter initialized")
    
    def normalize_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize pipeline data to the required JSON schema.
        
        Ensures all required fields are present and properly formatted.
        Applies default values for missing fields and type conversions.
        
        Schema Requirements:
        - source_url: string
        - source_type: string
        - author: string
        - published_date: string
        - language: string (2-letter code)
        - region: string (default: "global")
        - topic_tags: list of strings
        - trust_score: float (0.0-1.0)
        - content_chunks: list of strings
        
        Args:
            data: Dictionary containing processed content data.
        
        Returns:
            Dictionary following the standardized schema.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> input_data = {
            ...     "source_url": "https://example.com",
            ...     "content": "text",
            ...     "language": "en"
            ... }
            >>> normalized = writer.normalize_schema(input_data)
            >>> normalized['region']
            'global'
        """
        self.logger.debug(f"Normalizing schema for: {data.get('source_url', 'unknown')}")
        
        # Initialize normalized data with required fields
        normalized = {
            'source_url': '',
            'source_type': '',
            'author': '',
            'published_date': '',
            'language': '',
            'region': 'global',
            'topic_tags': [],
            'trust_score': 0.0,
            'content_chunks': []
        }
        
        # Map source_url
        normalized['source_url'] = str(data.get('source_url', ''))
        
        # Map source_type
        normalized['source_type'] = str(data.get('source_type', ''))
        
        # Map author
        author = data.get('author', '')
        normalized['author'] = str(author) if author else ''
        
        # Map published_date
        pub_date = data.get('published_date', '')
        normalized['published_date'] = str(pub_date) if pub_date else ''
        
        # Map language
        language = data.get('language', '')
        normalized['language'] = str(language) if language else ''
        
        # Map region (default to 'global' if missing)
        region = data.get('region', 'global')
        normalized['region'] = str(region) if region else 'global'
        
        # Map topic_tags (ensure it's a list)
        topic_tags = data.get('topic_tags', [])
        if isinstance(topic_tags, list):
            normalized['topic_tags'] = [str(tag) for tag in topic_tags]
        elif isinstance(topic_tags, str):
            # If it's a single string, wrap in list
            normalized['topic_tags'] = [topic_tags] if topic_tags else []
        else:
            normalized['topic_tags'] = []
        
        # Map trust_score (ensure it's a float between 0 and 1)
        trust_score = data.get('trust_score', 0.0)
        try:
            trust_score = float(trust_score)
            # Clip to valid range
            trust_score = max(0.0, min(1.0, trust_score))
            normalized['trust_score'] = round(trust_score, 3)
        except (TypeError, ValueError):
            self.logger.warning(f"Invalid trust_score value: {trust_score}, using 0.0")
            normalized['trust_score'] = 0.0
        
        # Map content_chunks (ensure it's a list)
        content_chunks = data.get('content_chunks', [])
        if isinstance(content_chunks, list):
            normalized['content_chunks'] = [str(chunk) for chunk in content_chunks]
        elif isinstance(content_chunks, str):
            # If it's a single string, wrap in list
            normalized['content_chunks'] = [content_chunks] if content_chunks else []
        else:
            # Fallback: try to use 'content' field if available
            content = data.get('content', '')
            if content:
                normalized['content_chunks'] = [str(content)]
            else:
                normalized['content_chunks'] = []
        
        self.logger.debug(f"Schema normalized successfully for: {normalized['source_url']}")
        
        return normalized
    
    def write_json(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Write processed data to a JSON file.
        
        Normalizes all data objects to the required schema and writes them
        to a JSON file as an array. Creates parent directories if needed.
        
        Args:
            data: List of dictionaries containing processed content data.
            output_path: Path to output JSON file (e.g., 'output/data.json').
        
        Raises:
            ValueError: If data is not a list.
            IOError: If file writing fails.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> data = [
            ...     {
            ...         "source_url": "https://example.com",
            ...         "source_type": "blog",
            ...         "language": "en",
            ...         "trust_score": 0.85
            ...     }
            ... ]
            >>> writer.write_json(data, "output/data.json")
        """
        if not isinstance(data, list):
            raise ValueError("Data must be a list of dictionaries")
        
        self.logger.info(f"Preparing dataset for storage ({len(data)} sources)")
        
        # Normalize all data objects
        normalized_data = []
        for i, item in enumerate(data):
            try:
                normalized = self.normalize_schema(item)
                normalized_data.append(normalized)
            except Exception as e:
                self.logger.error(f"Error normalizing item {i}: {e}")
                # Continue processing other items
                continue
        
        if not normalized_data:
            self.logger.warning("No valid data to write")
            return
        
        # Create output directory if it doesn't exist
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON file
        try:
            self.logger.info(f"Writing JSON file to: {output_path}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Stored {len(normalized_data)} sources successfully")
            
        except IOError as e:
            self.logger.error(f"Failed to write JSON file: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error writing JSON: {e}")
            raise
    
    def append_json(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Append processed data to an existing JSON file.
        
        If the file exists, loads existing data, appends new data, and writes back.
        If the file doesn't exist, creates a new file.
        
        Args:
            data: List of dictionaries containing processed content data.
            output_path: Path to output JSON file.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> new_data = [{"source_url": "...", ...}]
            >>> writer.append_json(new_data, "output/data.json")
        """
        output_file = Path(output_path)
        
        # Load existing data if file exists
        existing_data = []
        if output_file.exists():
            try:
                self.logger.info(f"Loading existing data from: {output_path}")
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                if not isinstance(existing_data, list):
                    self.logger.warning("Existing file is not a list, starting fresh")
                    existing_data = []
                else:
                    self.logger.info(f"Loaded {len(existing_data)} existing sources")
            
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse existing JSON: {e}")
                self.logger.warning("Starting with empty dataset")
                existing_data = []
            except Exception as e:
                self.logger.error(f"Error reading existing file: {e}")
                existing_data = []
        
        # Normalize new data
        self.logger.info(f"Preparing {len(data)} new sources for append")
        normalized_new = []
        for i, item in enumerate(data):
            try:
                normalized = self.normalize_schema(item)
                normalized_new.append(normalized)
            except Exception as e:
                self.logger.error(f"Error normalizing item {i}: {e}")
                continue
        
        # Combine existing and new data
        combined_data = existing_data + normalized_new
        
        # Write combined data
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Writing combined JSON file to: {output_path}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(
                f"Appended {len(normalized_new)} sources. "
                f"Total: {len(combined_data)} sources"
            )
        
        except Exception as e:
            self.logger.error(f"Failed to write JSON file: {e}")
            raise
    
    def read_json(self, input_path: str) -> List[Dict[str, Any]]:
        """
        Read and return data from a JSON file.
        
        Args:
            input_path: Path to input JSON file.
        
        Returns:
            List of dictionaries containing stored data.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file is not valid JSON.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> data = writer.read_json("output/data.json")
            >>> len(data)
            5
        """
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        self.logger.info(f"Reading JSON file from: {input_path}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                self.logger.warning("JSON file does not contain a list")
                return []
            
            self.logger.info(f"Loaded {len(data)} sources from file")
            return data
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            raise
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """
        Validate that a data object conforms to the required schema.
        
        Checks that all required fields are present and have correct types.
        
        Args:
            data: Dictionary to validate.
        
        Returns:
            True if schema is valid, False otherwise.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> valid_data = {
            ...     "source_url": "https://example.com",
            ...     "source_type": "blog",
            ...     "language": "en",
            ...     "topic_tags": ["health"],
            ...     "trust_score": 0.8,
            ...     "content_chunks": ["text"]
            ... }
            >>> writer.validate_schema(valid_data)
            True
        """
        required_fields = [
            'source_url',
            'source_type',
            'author',
            'published_date',
            'language',
            'region',
            'topic_tags',
            'trust_score',
            'content_chunks'
        ]
        
        # Check all required fields are present
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate types
        if not isinstance(data.get('topic_tags'), list):
            self.logger.warning("topic_tags must be a list")
            return False
        
        if not isinstance(data.get('content_chunks'), list):
            self.logger.warning("content_chunks must be a list")
            return False
        
        try:
            trust_score = float(data.get('trust_score', 0))
            if not (0.0 <= trust_score <= 1.0):
                self.logger.warning(f"trust_score must be between 0 and 1, got {trust_score}")
                return False
        except (TypeError, ValueError):
            self.logger.warning("trust_score must be a number")
            return False
        
        return True
    
    def get_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about stored data.
        
        Args:
            data: List of stored data objects.
        
        Returns:
            Dictionary containing statistics.
        
        Example:
            >>> writer = JSONStorageWriter()
            >>> data = writer.read_json("output/data.json")
            >>> stats = writer.get_statistics(data)
            >>> print(stats['total_sources'])
            10
        """
        if not data:
            return {
                'total_sources': 0,
                'source_types': {},
                'languages': {},
                'avg_trust_score': 0.0,
                'avg_chunks_per_source': 0.0
            }
        
        source_types = {}
        languages = {}
        trust_scores = []
        chunk_counts = []
        
        for item in data:
            # Count source types
            source_type = item.get('source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Count languages
            language = item.get('language', 'unknown')
            languages[language] = languages.get(language, 0) + 1
            
            # Collect trust scores
            try:
                trust_scores.append(float(item.get('trust_score', 0)))
            except (TypeError, ValueError):
                pass
            
            # Count chunks
            chunks = item.get('content_chunks', [])
            if isinstance(chunks, list):
                chunk_counts.append(len(chunks))
        
        stats = {
            'total_sources': len(data),
            'source_types': source_types,
            'languages': languages,
            'avg_trust_score': sum(trust_scores) / len(trust_scores) if trust_scores else 0.0,
            'avg_chunks_per_source': sum(chunk_counts) / len(chunk_counts) if chunk_counts else 0.0
        }
        
        return stats
