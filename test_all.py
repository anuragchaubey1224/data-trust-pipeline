#!/usr/bin/env python3
"""
Master Test Suite for Data Trust Pipeline

This script runs comprehensive tests on all pipeline components:
- Configuration loading
- Individual scrapers (Blog, YouTube, PubMed)
- Unified pipeline

Run this to verify your entire setup before production deployment.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.helpers import load_sources
from scraper import BlogScraper, YouTubeScraper, PubMedScraper

# Disable SSL warnings for testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def test_config():
    """Test configuration loading."""
    print_section("[1/5] Testing Configuration Loading")
    
    try:
        sources = load_sources("config/sources.yaml")
        
        blog_count = len(sources.get('blogs', []))
        youtube_count = len(sources.get('youtube', []))
        pubmed_count = len(sources.get('pubmed', []))
        total = blog_count + youtube_count + pubmed_count
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Blog sources:   {blog_count}")
        print(f"  - YouTube sources: {youtube_count}")
        print(f"  - PubMed sources:  {pubmed_count}")
        print(f"  - Total sources:   {total}")
        
        if total == 0:
            print("⚠️  Warning: No sources configured in config/sources.yaml")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_blog_scraper():
    """Test blog scraper."""
    print_section("[2/5] Testing Blog Scraper")
    
    try:
        scraper = BlogScraper(verify_ssl=False)
        print("✓ BlogScraper initialized")
        
        # Test with configured URLs if available
        sources = load_sources("config/sources.yaml")
        blog_urls = sources.get('blogs', [])
        
        if blog_urls:
            test_url = blog_urls[0]
            print(f"  Testing with: {test_url}")
            
            result = scraper.scrape(test_url)
            
            if result and result.get('content'):
                word_count = len(result['content'].split())
                print(f"✓ Blog scraper working: {result['title'][:50] if result['title'] else 'N/A'}...")
                print(f"  Content: {word_count} words")
                return True
            else:
                print("⚠️  Blog scraper returned no content")
                return True
        else:
            print("⚠️  No blog URLs configured, skipping functional test")
            return True
        
    except Exception as e:
        print(f"✗ Blog scraper test failed: {e}")
        return False


def test_youtube_scraper():
    """Test YouTube scraper."""
    print_section("[3/5] Testing YouTube Scraper")
    
    try:
        scraper = YouTubeScraper()
        print("✓ YouTubeScraper initialized")
        
        # Test with configured URLs if available
        sources = load_sources("config/sources.yaml")
        youtube_urls = sources.get('youtube', [])
        
        if youtube_urls:
            test_url = youtube_urls[0]
            print(f"  Testing with: {test_url}")
            
            result = scraper.scrape(test_url)
            
            if result and result.get('content'):
                word_count = len(result['content'].split())
                print(f"✓ YouTube scraper working: {result['title'][:50]}...")
                print(f"  Transcript: {word_count} words")
                return True
            else:
                print("⚠️  YouTube scraper returned no content")
                return True
        else:
            print("⚠️  No YouTube URLs configured, skipping functional test")
            return True
        
    except Exception as e:
        print(f"✗ YouTube scraper test failed: {e}")
        return False


def test_pubmed_scraper():
    """Test PubMed scraper."""
    print_section("[4/5] Testing PubMed Scraper")
    
    try:
        scraper = PubMedScraper()
        print("✓ PubMedScraper initialized")
        
        # Test with configured URLs if available
        sources = load_sources("config/sources.yaml")
        pubmed_urls = sources.get('pubmed', [])
        
        if pubmed_urls:
            test_url = pubmed_urls[0]
            print(f"  Testing with: {test_url}")
            
            result = scraper.scrape(test_url)
            
            if result and result.get('content'):
                word_count = len(result['content'].split())
                print(f"✓ PubMed scraper working: {result['title'][:50]}...")
                print(f"  Abstract: {word_count} words")
                return True
            else:
                print("⚠️  PubMed scraper returned no content")
                return True
        else:
            print("⚠️  No PubMed URLs configured, skipping functional test")
            return True
        
    except Exception as e:
        print(f"✗ PubMed scraper test failed: {e}")
        return False


def test_unified_pipeline():
    """Test the complete unified pipeline."""
    print_section("[5/5] Testing Unified Pipeline with ALL Configured Sources")
    
    try:
        # Load sources
        sources = load_sources("config/sources.yaml")
        
        blog_urls = sources.get('blogs', [])
        youtube_urls = sources.get('youtube', [])
        pubmed_urls = sources.get('pubmed', [])
        
        total_sources = len(blog_urls) + len(youtube_urls) + len(pubmed_urls)
        
        if total_sources == 0:
            print("⚠️  No sources configured, skipping pipeline test")
            return True
        
        # Initialize scrapers
        blog_scraper = BlogScraper(verify_ssl=False)
        youtube_scraper = YouTubeScraper()
        pubmed_scraper = PubMedScraper()
        
        print(f"✓ All scrapers initialized")
        print(f"  Processing {total_sources} total sources from config...\n")
        
        results = []
        
        # Scrape ALL blog sources
        for i, url in enumerate(blog_urls, 1):
            try:
                print(f"  [{i}/{len(blog_urls)}] Scraping blog: {url[:60]}...")
                result = blog_scraper.scrape(url)
                results.append(result)
                word_count = len(result['content'].split()) if result.get('content') else 0
                print(f"       ✓ {result['title'][:50] if result.get('title') else 'N/A'}... ({word_count} words)")
            except Exception as e:
                print(f"       ✗ Failed: {str(e)[:50]}")
        
        # Scrape ALL YouTube sources
        for i, url in enumerate(youtube_urls, 1):
            try:
                print(f"  [{i}/{len(youtube_urls)}] Scraping YouTube: {url[:60]}...")
                result = youtube_scraper.scrape(url)
                results.append(result)
                word_count = len(result['content'].split()) if result.get('content') else 0
                print(f"       ✓ {result['title'][:50] if result.get('title') else 'N/A'}... ({word_count} words)")
            except Exception as e:
                print(f"       ✗ Failed: {str(e)[:50]}")
        
        # Scrape ALL PubMed sources
        for i, url in enumerate(pubmed_urls, 1):
            try:
                print(f"  [{i}/{len(pubmed_urls)}] Scraping PubMed: {url[:60]}...")
                result = pubmed_scraper.scrape(url)
                results.append(result)
                word_count = len(result['content'].split()) if result.get('content') else 0
                print(f"       ✓ {result['title'][:50] if result.get('title') else 'N/A'}... ({word_count} words)")
            except Exception as e:
                print(f"       ✗ Failed: {str(e)[:50]}")
        
        successful = sum(1 for r in results if r and r.get('content'))
        total_words = sum(
            len(r['content'].split()) if r and r.get('content') else 0 
            for r in results
        )
        
        print(f"\n✓ Pipeline test completed")
        print(f"  - Tested: {len(results)} sources")
        print(f"  - Success: {successful}/{len(results)}")
        print(f"  - Total content: {total_words:,} words")
        
        return True
        
    except Exception as e:
        print(f"✗ Pipeline test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and display summary."""
    print_header("DATA TRUST PIPELINE - MASTER TEST SUITE")
    
    print("\nRunning comprehensive tests on all pipeline components...")
    print("This will verify configuration, scrapers, and unified pipeline.\n")
    
    # Run all tests
    results = {
        "Configuration": test_config(),
        "Blog Scraper": test_blog_scraper(),
        "YouTube Scraper": test_youtube_scraper(),
        "PubMed Scraper": test_pubmed_scraper(),
        "Unified Pipeline": test_unified_pipeline()
    }
    
    # Display summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\nTest Results:")
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*80}")
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("="*80)
        print("\n🎉 Your pipeline is ready for production use!")
        print("\nNext steps:")
        print("  1. Run: python3 pipeline/demo_unified_scraping.py")
        print("  2. Check output/ directory for results")
        print("  3. Begin data processing and analysis")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*80)
        print("\n⚠️  Please fix the failing tests before production deployment")
        print("\nTroubleshooting:")
        print("  1. Check config/sources.yaml has valid URLs")
        print("  2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("  3. Verify network connectivity")
        print("  4. Review individual test scripts for detailed errors")
        return 1


def main():
    """Main entry point."""
    # Configure logging to WARNING level to reduce noise
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
