#!/usr/bin/env python3
"""
Master Test Suite for Data Trust Pipeline

This script runs comprehensive tests on all pipeline components:
- Configuration loading
- Blog scraper
- YouTube scraper
- PubMed scraper
- Unified pipeline execution

Usage:
    python3 test_all.py

Expected output:
    ✓ PASS  Configuration
    ✓ PASS  Blog Scraper
    ✓ PASS  YouTube Scraper
    ✓ PASS  PubMed Scraper
    ✓ PASS  Unified Pipeline
    
    ✓ ALL TESTS PASSED (5/5)
"""

import sys
import warnings
from pathlib import Path

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from utils.helpers import load_sources
from scraper.blog_scraper import BlogScraper
from scraper.youtube_scraper import YouTubeScraper
from scraper.pubmed_scraper import PubMedScraper
from processing.text_cleaner import TextCleaner
from processing.language_detector import LanguageDetector
from processing.topic_tagger import TopicTagger
from processing.chunker import ContentChunker
from scoring.trust_score import TrustScoreCalculator
from storage.json_writer import JSONStorageWriter


class TestRunner:
    """Test runner for pipeline components."""
    
    def __init__(self):
        """Initialize test runner."""
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_test(self, test_name: str, test_func) -> bool:
        """
        Run a single test and record result.
        
        Args:
            test_name: Name of the test
            test_func: Function to execute (should return True on success)
        
        Returns:
            True if test passed, False otherwise
        """
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                self.test_results.append((test_name, True, None))
                return True
            else:
                self.tests_failed += 1
                self.test_results.append((test_name, False, "Test returned False"))
                return False
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append((test_name, False, str(e)))
            return False
    
    def print_results(self):
        """Print formatted test results."""
        print()
        for test_name, passed, error in self.test_results:
            if passed:
                print(f"✓ PASS  {test_name}")
            else:
                print(f"✗ FAIL  {test_name}")
                if error:
                    print(f"        Error: {error}")
        
        print()
        total_tests = self.tests_passed + self.tests_failed
        
        if self.tests_failed == 0:
            print(f"✓ ALL TESTS PASSED ({self.tests_passed}/{total_tests})")
            return 0
        else:
            print(f"✗ TESTS FAILED: {self.tests_failed}/{total_tests}")
            print(f"✓ TESTS PASSED: {self.tests_passed}/{total_tests}")
            return 1


def test_configuration() -> bool:
    """Test configuration loading."""
    try:
        # Load configuration
        sources = load_sources("config/sources.yaml")
        
        # Validate structure
        required_keys = ['blogs', 'youtube', 'pubmed']
        for key in required_keys:
            if key not in sources:
                return False
            if not isinstance(sources[key], list):
                return False
        
        # Check that we have some sources
        total_sources = len(sources['blogs']) + len(sources['youtube']) + len(sources['pubmed'])
        if total_sources == 0:
            return False
        
        return True
    except Exception:
        return False


def test_blog_scraper() -> bool:
    """Test blog scraper functionality."""
    try:
        # Initialize scraper
        scraper = BlogScraper(timeout=30, max_retries=2, verify_ssl=False)
        
        # Load test URL from config
        sources = load_sources("config/sources.yaml")
        if not sources['blogs']:
            return False
        
        # Test first blog URL
        test_url = sources['blogs'][0]
        result = scraper.scrape(test_url)
        
        # Validate result structure
        required_fields = ['source_url', 'source_type', 'title', 'content']
        for field in required_fields:
            if field not in result:
                return False
        
        # Check that we got some content
        if not result['content'] or len(result['content'].strip()) == 0:
            return False
        
        # Verify source type
        if result['source_type'] != 'blog':
            return False
        
        return True
    except Exception:
        return False


def test_youtube_scraper() -> bool:
    """Test YouTube scraper functionality."""
    try:
        # Initialize scraper
        scraper = YouTubeScraper()
        
        # Load test URL from config
        sources = load_sources("config/sources.yaml")
        if not sources['youtube']:
            return False
        
        # Test first YouTube URL
        test_url = sources['youtube'][0]
        result = scraper.scrape(test_url)
        
        # Validate result structure
        required_fields = ['source_url', 'source_type', 'title', 'content']
        for field in required_fields:
            if field not in result:
                return False
        
        # Check that we got some content (transcript or description)
        if not result['content'] or len(result['content'].strip()) == 0:
            return False
        
        # Verify source type
        if result['source_type'] != 'youtube':
            return False
        
        return True
    except Exception:
        return False


def test_pubmed_scraper() -> bool:
    """Test PubMed scraper functionality."""
    try:
        # Initialize scraper
        scraper = PubMedScraper(timeout=30)
        
        # Load test URL from config
        sources = load_sources("config/sources.yaml")
        if not sources['pubmed']:
            return False
        
        # Test first PubMed URL
        test_url = sources['pubmed'][0]
        result = scraper.scrape(test_url)
        
        # Validate result structure
        required_fields = ['source_url', 'source_type', 'title', 'content']
        for field in required_fields:
            if field not in result:
                return False
        
        # Check that we got some content
        if not result['content'] or len(result['content'].strip()) == 0:
            return False
        
        # Verify source type
        if result['source_type'] != 'pubmed':
            return False
        
        return True
    except Exception:
        return False


def test_unified_pipeline() -> bool:
    """Test complete pipeline with all components."""
    try:
        # Load sources
        sources = load_sources("config/sources.yaml")
        
        # Initialize all components
        blog_scraper = BlogScraper(timeout=30, max_retries=2, verify_ssl=False)
        text_cleaner = TextCleaner()
        language_detector = LanguageDetector()
        topic_tagger = TopicTagger()
        chunker = ContentChunker(default_chunk_size=300, default_overlap=50)
        trust_calculator = TrustScoreCalculator()
        storage_writer = JSONStorageWriter()
        
        # Scrape one source (limit to first blog for speed)
        all_data = []
        
        if sources['blogs']:
            blog_data = blog_scraper.scrape(sources['blogs'][0])
            if not blog_data:
                return False
            all_data.append(blog_data)
        
        # Process each source through pipeline
        final_data = []
        for source_data in all_data:
            # Clean text
            cleaned_content = text_cleaner.clean_text(source_data['content'])
            if not cleaned_content:
                return False
            
            # Detect language
            language = language_detector.detect_language(cleaned_content)
            if not language:
                return False
            
            # Generate topic tags
            topic_tags = topic_tagger.extract_topics(cleaned_content, top_n=5)
            if not isinstance(topic_tags, list):
                return False
            
            # Chunk content
            chunks = chunker.chunk_text(cleaned_content)
            if not chunks or len(chunks) == 0:
                return False
            
            # Calculate trust score
            trust_data = {
                'source_url': source_data['source_url'],
                'author': source_data.get('author', ''),
                'published_date': source_data.get('published_date', ''),
                'source_type': source_data['source_type'],
                'content': cleaned_content
            }
            trust_score = trust_calculator.calculate_trust_score(trust_data)
            if not isinstance(trust_score, (int, float)):
                return False
            
            # Build final data structure
            processed_data = {
                'source_url': source_data['source_url'],
                'source_type': source_data['source_type'],
                'author': source_data.get('author', ''),
                'published_date': source_data.get('published_date', ''),
                'language': language,
                'region': 'global',
                'topic_tags': topic_tags,
                'trust_score': round(trust_score, 3),
                'content_chunks': chunks
            }
            
            final_data.append(processed_data)
        
        # Test storage (write to test file)
        test_output_path = "output/test_pipeline_output.json"
        storage_writer.write_json(final_data, test_output_path)
        
        # Verify file was created
        if not Path(test_output_path).exists():
            return False
        
        # Verify we processed at least one source
        if len(final_data) == 0:
            return False
        
        return True
    except Exception as e:
        # Silent fail for clean output
        return False


def main():
    """Run all tests."""
    runner = TestRunner()
    
    # Run all tests
    runner.run_test("Configuration", test_configuration)
    runner.run_test("Blog Scraper", test_blog_scraper)
    runner.run_test("YouTube Scraper", test_youtube_scraper)
    runner.run_test("PubMed Scraper", test_pubmed_scraper)
    runner.run_test("Unified Pipeline", test_unified_pipeline)
    
    # Print results
    exit_code = runner.print_results()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
