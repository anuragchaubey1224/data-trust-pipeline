#!/usr/bin/env python3
"""
Data Pipeline Orchestrator

This module provides a DataPipeline class that orchestrates the complete
end-to-end data scraping, processing, scoring, and storage pipeline.

Usage:
    python pipeline/run_pipeline.py

The pipeline executes the following steps:
    1. Load sources from config/sources.yaml
    2. Scrape content from each source (blog, YouTube, PubMed)
    3. Clean and normalize text
    4. Detect language
    5. Generate topic tags
    6. Chunk content into smaller pieces
    7. Calculate trust score
    8. Store final results in output/scraped_data.json

Author: Senior Data Engineer
Date: March 2026
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import scrapers
from scraper.blog_scraper import BlogScraper
from scraper.youtube_scraper import YouTubeScraper
from scraper.pubmed_scraper import PubMedScraper

# Import processing modules
from processing.text_cleaner import TextCleaner
from processing.language_detector import LanguageDetector
from processing.topic_tagger import TopicTagger
from processing.chunker import ContentChunker

# Import scoring module
from scoring.trust_score import TrustScoreCalculator

# Import storage module
from storage.json_writer import JSONStorageWriter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DataPipeline:
    """
    Data pipeline orchestrator for end-to-end content processing.
    
    This class coordinates all pipeline stages from scraping through storage,
    processing each source through multiple transformation steps and producing
    a final JSON dataset with normalized schemas.
    
    Attributes:
        blog_scraper: BlogScraper instance for blog content
        youtube_scraper: YouTubeScraper instance for YouTube videos
        pubmed_scraper: PubMedScraper instance for research articles
        text_cleaner: TextCleaner instance for text normalization
        language_detector: LanguageDetector instance for language identification
        topic_tagger: TopicTagger instance for keyword extraction
        content_chunker: ContentChunker instance for text splitting
        trust_calculator: TrustScoreCalculator instance for credibility scoring
        storage_writer: JSONStorageWriter instance for data persistence
        logger: Logger instance for pipeline events
    """
    
    def __init__(self):
        """
        Initialize the DataPipeline with all required modules.
        
        Instantiates all scraper, processor, scorer, and storage components
        needed for the complete pipeline execution.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("Initializing DataPipeline...")
        
        # Initialize scrapers
        self.logger.info("Initializing scrapers...")
        self.blog_scraper = BlogScraper(timeout=30, max_retries=3)
        self.youtube_scraper = YouTubeScraper()
        self.pubmed_scraper = PubMedScraper(timeout=30)
        
        # Initialize processing modules
        self.logger.info("Initializing processing modules...")
        self.text_cleaner = TextCleaner()
        self.language_detector = LanguageDetector()
        self.topic_tagger = TopicTagger()
        self.content_chunker = ContentChunker(default_chunk_size=300, default_overlap=50)
        
        # Initialize scoring module
        self.logger.info("Initializing trust score calculator...")
        self.trust_calculator = TrustScoreCalculator()
        
        # Initialize storage module
        self.logger.info("Initializing storage writer...")
        self.storage_writer = JSONStorageWriter()
        
        self.logger.info("DataPipeline initialization complete")
    
    def load_sources(self, config_path: str = "config/sources.yaml") -> Dict[str, List[str]]:
        """
        Load source URLs from YAML configuration file.
        
        Reads the sources configuration file and returns URLs organized by
        source type (blogs, youtube, pubmed).
        
        Args:
            config_path: Path to YAML configuration file (default: config/sources.yaml)
        
        Returns:
            Dictionary with keys:
                - 'blogs': List of blog URLs
                - 'youtube': List of YouTube video URLs
                - 'pubmed': List of PubMed article URLs
        
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        
        Example:
            >>> pipeline = DataPipeline()
            >>> sources = pipeline.load_sources()
            >>> print(f"Found {len(sources['blogs'])} blog URLs")
        """
        self.logger.info(f"Loading sources from: {config_path}")
        
        try:
            # Check if file exists
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            # Load YAML
            with open(config_file, 'r') as f:
                sources = yaml.safe_load(f)
            
            # Validate structure
            if not isinstance(sources, dict):
                raise ValueError("Invalid YAML structure: expected dictionary")
            
            # Extract source lists (empty list if not present)
            result = {
                'blogs': sources.get('blogs', []),
                'youtube': sources.get('youtube', []),
                'pubmed': sources.get('pubmed', [])
            }
            
            # Log summary
            total = sum(len(urls) for urls in result.values())
            self.logger.info(
                f"Loaded {total} sources: "
                f"{len(result['blogs'])} blogs, "
                f"{len(result['youtube'])} YouTube videos, "
                f"{len(result['pubmed'])} PubMed articles"
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error loading sources: {e}")
            raise
    
    def scrape_sources(self, sources: Dict[str, List[str]]) -> List[Dict]:
        """
        Scrape content from all sources using appropriate scrapers.
        
        Iterates through all source URLs and calls the appropriate scraper
        based on source type. Handles errors gracefully and continues
        processing remaining sources.
        
        Args:
            sources: Dictionary containing lists of URLs by type
        
        Returns:
            List of scraped data dictionaries, each containing:
                - source_url
                - source_type
                - title
                - author
                - published_date
                - description
                - content
        
        Example:
            >>> pipeline = DataPipeline()
            >>> sources = pipeline.load_sources()
            >>> scraped_data = pipeline.scrape_sources(sources)
            >>> print(f"Scraped {len(scraped_data)} sources")
        """
        self.logger.info("Starting source scraping...")
        scraped_data = []
        
        # Scrape blog sources
        self.logger.info(f"Scraping {len(sources['blogs'])} blog sources...")
        for url in sources['blogs']:
            try:
                self.logger.info(f"Scraping blog: {url}")
                result = self.blog_scraper.scrape(url)
                scraped_data.append(result)
                self.logger.info(f"✓ Successfully scraped blog: {url}")
            except Exception as e:
                self.logger.error(f"✗ Failed to scrape blog {url}: {e}")
                # Continue with next source
        
        # Scrape YouTube sources
        self.logger.info(f"Scraping {len(sources['youtube'])} YouTube sources...")
        for url in sources['youtube']:
            try:
                self.logger.info(f"Scraping YouTube: {url}")
                result = self.youtube_scraper.scrape(url)
                scraped_data.append(result)
                self.logger.info(f"✓ Successfully scraped YouTube: {url}")
            except Exception as e:
                self.logger.error(f"✗ Failed to scrape YouTube {url}: {e}")
                # Continue with next source
        
        # Scrape PubMed sources
        self.logger.info(f"Scraping {len(sources['pubmed'])} PubMed sources...")
        for url in sources['pubmed']:
            try:
                self.logger.info(f"Scraping PubMed: {url}")
                result = self.pubmed_scraper.scrape(url)
                scraped_data.append(result)
                self.logger.info(f"✓ Successfully scraped PubMed: {url}")
            except Exception as e:
                self.logger.error(f"✗ Failed to scrape PubMed {url}: {e}")
                # Continue with next source
        
        self.logger.info(
            f"Scraping complete: {len(scraped_data)}/{sum(len(urls) for urls in sources.values())} "
            f"sources scraped successfully"
        )
        
        return scraped_data
    
    def process_source(self, data: Dict) -> Optional[Dict]:
        """
        Process a scraped source through all transformation steps.
        
        Applies the following processing pipeline:
            1. Clean text (remove HTML, normalize whitespace)
            2. Detect language
            3. Extract topic tags
            4. Chunk content into smaller pieces
        
        Args:
            data: Scraped data dictionary containing 'content' field
        
        Returns:
            Processed data dictionary with added fields:
                - language: Detected language code
                - topic_tags: List of extracted keywords
                - content_chunks: List of text chunks
            Returns None if processing fails
        
        Example:
            >>> pipeline = DataPipeline()
            >>> scraped = {"content": "Raw article text...", ...}
            >>> processed = pipeline.process_source(scraped)
            >>> print(processed['language'])
        """
        source_url = data.get('source_url', 'unknown')
        self.logger.info(f"Processing source: {source_url}")
        
        try:
            # Extract content
            content = data.get('content', '')
            
            if not content or len(content.strip()) < 10:
                self.logger.warning(f"Skipping source with insufficient content: {source_url}")
                return None
            
            # Step 1: Clean text
            self.logger.info(f"  Step 1/4: Cleaning text...")
            cleaned_text = self.text_cleaner.clean_text(content)
            
            if not cleaned_text or len(cleaned_text.strip()) < 10:
                self.logger.warning(f"Content too short after cleaning: {source_url}")
                return None
            
            # Step 2: Detect language
            self.logger.info(f"  Step 2/4: Detecting language...")
            language = self.language_detector.detect_language(cleaned_text)
            
            # Step 3: Extract topic tags
            self.logger.info(f"  Step 3/4: Extracting topic tags...")
            topic_tags = self.topic_tagger.extract_topics(cleaned_text, top_n=5)
            
            # Step 4: Chunk content
            self.logger.info(f"  Step 4/4: Chunking content...")
            content_chunks = self.content_chunker.chunk_text(cleaned_text)
            
            # Build processed data object
            processed_data = {
                'source_url': data.get('source_url', ''),
                'source_type': data.get('source_type', ''),
                'author': data.get('author', ''),
                'published_date': data.get('published_date', ''),
                'language': language,
                'region': 'global',  # Default region
                'topic_tags': topic_tags,
                'content_chunks': content_chunks,
                # Keep original cleaned content for trust scoring
                '_cleaned_content': cleaned_text
            }
            
            self.logger.info(
                f"✓ Processing complete: {source_url} "
                f"(language={language}, topics={len(topic_tags)}, chunks={len(content_chunks)})"
            )
            
            return processed_data
        
        except Exception as e:
            self.logger.error(f"✗ Error processing source {source_url}: {e}")
            return None
    
    def score_source(self, data: Dict) -> Dict:
        """
        Calculate trust score for a processed source.
        
        Uses the TrustScoreCalculator to compute a weighted credibility score
        based on author, citations, domain authority, recency, and disclaimers.
        
        Args:
            data: Processed data dictionary
        
        Returns:
            Data dictionary with added 'trust_score' field (float 0.0-1.0)
        
        Example:
            >>> pipeline = DataPipeline()
            >>> processed = {...}
            >>> scored = pipeline.score_source(processed)
            >>> print(f"Trust score: {scored['trust_score']}")
        """
        source_url = data.get('source_url', 'unknown')
        self.logger.info(f"Calculating trust score: {source_url}")
        
        try:
            # Prepare data for trust calculator
            score_input = {
                'source_url': data.get('source_url', ''),
                'source_type': data.get('source_type', ''),
                'author': data.get('author', ''),
                'published_date': data.get('published_date', ''),
                'content': data.get('_cleaned_content', '')
            }
            
            # Calculate trust score
            trust_score = self.trust_calculator.calculate_trust_score(score_input)
            
            # Add score to data
            data['trust_score'] = trust_score
            
            # Remove temporary cleaned content field
            if '_cleaned_content' in data:
                del data['_cleaned_content']
            
            self.logger.info(f"✓ Trust score calculated: {source_url} (score={trust_score:.3f})")
            
            return data
        
        except Exception as e:
            self.logger.error(f"✗ Error calculating trust score for {source_url}: {e}")
            # Set default score on error
            data['trust_score'] = 0.0
            if '_cleaned_content' in data:
                del data['_cleaned_content']
            return data
    
    def _split_output_by_type(self, data: List[Dict]):
        """
        Split unified data into separate files by source type.
        
        Creates three additional output files:
            - output/blogs.json (blog sources)
            - output/youtube.json (YouTube sources)
            - output/pubmed.json (PubMed sources)
        
        Args:
            data: List of processed data dictionaries
        """
        try:
            # Split by source type
            blogs = [item for item in data if item.get('source_type') == 'blog']
            youtube = [item for item in data if item.get('source_type') == 'youtube']
            pubmed = [item for item in data if item.get('source_type') == 'pubmed']
            
            # Write separate files
            if blogs:
                self.storage_writer.write_json(blogs, 'output/blogs.json')
                self.logger.info(f"✓ Created output/blogs.json ({len(blogs)} sources)")
            
            if youtube:
                self.storage_writer.write_json(youtube, 'output/youtube.json')
                self.logger.info(f"✓ Created output/youtube.json ({len(youtube)} sources)")
            
            if pubmed:
                self.storage_writer.write_json(pubmed, 'output/pubmed.json')
                self.logger.info(f"✓ Created output/pubmed.json ({len(pubmed)} sources)")
            
        except Exception as e:
            self.logger.error(f"Error splitting output by type: {e}")
            # Don't fail the pipeline if splitting fails
    
    def run(self, config_path: str = "config/sources.yaml", output_path: str = "output/scraped_data.json"):
        """
        Execute the complete data pipeline end-to-end.
        
        Main pipeline orchestration method that coordinates all stages:
            1. Load sources from configuration
            2. Scrape content from each source
            3. Process each source (clean, detect language, tag topics, chunk)
            4. Calculate trust scores
            5. Collect successful results
            6. Write final dataset to JSON
        
        Args:
            config_path: Path to sources configuration file (default: config/sources.yaml)
            output_path: Path to output JSON file (default: output/scraped_data.json)
        
        Example:
            >>> pipeline = DataPipeline()
            >>> pipeline.run()
        """
        self.logger.info("=" * 80)
        self.logger.info("DATA PIPELINE EXECUTION STARTED")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Stage 1: Load sources
            self.logger.info("\n[STAGE 1/5] Loading sources from configuration...")
            sources = self.load_sources(config_path)
            
            # Stage 2: Scrape sources
            self.logger.info("\n[STAGE 2/5] Scraping content from sources...")
            scraped_data = self.scrape_sources(sources)
            
            if not scraped_data:
                self.logger.error("No sources were successfully scraped. Pipeline aborted.")
                return
            
            # Stage 3: Process sources
            self.logger.info("\n[STAGE 3/5] Processing scraped content...")
            processed_data = []
            
            for i, source in enumerate(scraped_data, 1):
                self.logger.info(f"Processing source {i}/{len(scraped_data)}...")
                processed = self.process_source(source)
                
                if processed:
                    processed_data.append(processed)
            
            if not processed_data:
                self.logger.error("No sources were successfully processed. Pipeline aborted.")
                return
            
            self.logger.info(
                f"Processing complete: {len(processed_data)}/{len(scraped_data)} "
                f"sources processed successfully"
            )
            
            # Stage 4: Calculate trust scores
            self.logger.info("\n[STAGE 4/5] Calculating trust scores...")
            scored_data = []
            
            for i, source in enumerate(processed_data, 1):
                self.logger.info(f"Scoring source {i}/{len(processed_data)}...")
                scored = self.score_source(source)
                scored_data.append(scored)
            
            self.logger.info(f"Trust scoring complete: {len(scored_data)} sources scored")
            
            # Stage 5: Write to JSON
            self.logger.info("\n[STAGE 5/5] Writing final dataset to JSON...")
            self.storage_writer.write_json(scored_data, output_path)
            
            # Split output by source type
            self.logger.info("\n[STAGE 5/5] Splitting output by source type...")
            self._split_output_by_type(scored_data)
            
            # Calculate execution time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Print success summary
            self.logger.info("=" * 80)
            self.logger.info("PIPELINE EXECUTION COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"Total sources processed: {len(scored_data)}")
            self.logger.info(f"Output files created:")
            self.logger.info(f"  • {output_path} (unified)")
            self.logger.info(f"  • output/blogs.json")
            self.logger.info(f"  • output/youtube.json")
            self.logger.info(f"  • output/pubmed.json")
            self.logger.info(f"Execution time: {duration:.2f} seconds")
            self.logger.info("=" * 80)
            
            # Generate statistics
            stats = self.storage_writer.get_statistics(scored_data)
            self.logger.info("\nDataset Statistics:")
            self.logger.info(f"  Source types: {stats['source_types']}")
            self.logger.info(f"  Languages: {stats['languages']}")
            self.logger.info(f"  Average trust score: {stats['avg_trust_score']:.3f}")
            self.logger.info(f"  Average chunks per source: {stats['avg_chunks_per_source']:.1f}")
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            raise


def main():
    """
    Main entry point for the pipeline.
    
    Creates a DataPipeline instance and executes the complete pipeline.
    """
    try:
        # Create pipeline instance
        pipeline = DataPipeline()
        
        # Run the pipeline
        pipeline.run()
        
    except KeyboardInterrupt:
        logging.info("\nPipeline interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        logging.error(f"Pipeline failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
