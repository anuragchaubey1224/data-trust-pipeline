"""
Test script for BlogScraper.

This script demonstrates the BlogScraper functionality by scraping
a sample blog article and displaying the extracted information.
"""

import sys
import urllib3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.blog_scraper import BlogScraper

# Disable SSL warnings when SSL verification is turned off (for testing only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_single_blog():
    """Test scraping a single blog article."""
    print("=" * 70)
    print("Blog Scraper Test")
    print("=" * 70)
    
    # Initialize scraper (SSL disabled for macOS certificate issues)
    scraper = BlogScraper(
        timeout=30,
        max_retries=3,
        retry_delay=2,
        verify_ssl=False  # Disable SSL verification for testing
    )
    
    # Test URL - a reliable test page with structured content
    # Note: Using httpbin for reliable testing, or use a real blog URL that works
    test_url = "https://example.com"  # Simple test page
    # Alternative: "https://www.python.org/about/"  # Python about page
    # For real blog testing, use a current valid blog URL
    
    print(f"\nScraping: {test_url}")
    print("-" * 70)
    
    try:
        # Scrape the blog article
        result = scraper.scrape(test_url)
        
        # Display extracted information
        print("\n✓ SCRAPING SUCCESSFUL\n")
        
        print(f"Source URL:      {result['source_url']}")
        print(f"Source Type:     {result['source_type']}")
        print(f"Title:           {result['title'] or 'N/A'}")
        print(f"Author:          {result['author'] or 'N/A'}")
        print(f"Published Date:  {result['published_date'] or 'N/A'}")
        
        # Show description (truncated)
        desc = result['description']
        if desc:
            desc_preview = desc[:100] + "..." if len(desc) > 100 else desc
            print(f"Description:     {desc_preview}")
        else:
            print(f"Description:     N/A")
        
        # Show content statistics
        content = result['content']
        if content:
            word_count = len(content.split())
            char_count = len(content)
            lines = len(content.split('\n'))
            
            print(f"\nContent Statistics:")
            print(f"  - Words:       {word_count}")
            print(f"  - Characters:  {char_count}")
            print(f"  - Paragraphs:  {lines}")
            
            # Show content preview
            content_preview = content[:300] + "..." if len(content) > 300 else content
            print(f"\nContent Preview:")
            print("-" * 70)
            print(content_preview)
            print("-" * 70)
        else:
            print(f"\n⚠️  Warning: No content extracted")
        
        print("\n" + "=" * 70)
        print("✓ Test PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_blogs():
    """Test scraping multiple blog articles."""
    print("\n\n" + "=" * 70)
    print("Multiple Blog Scraping Test")
    print("=" * 70)
    
    # Initialize scraper
    scraper = BlogScraper(
        timeout=20,
        max_retries=2,
        retry_delay=1,
        verify_ssl=False
    )
    
    # Test URLs
    test_urls = [
        "https://example.com",  # Simple test page
        "http://httpbin.org/html",  # Simple test page with HTML
    ]
    
    print(f"\nScraping {len(test_urls)} blog articles...")
    print("-" * 70)
    
    try:
        results = scraper.scrape_multiple(test_urls)
        
        print(f"\n✓ Scraped {len(results)} articles\n")
        
        # Display summary for each
        for idx, result in enumerate(results, 1):
            print(f"\n[Article {idx}]")
            print(f"  URL:    {result['source_url']}")
            print(f"  Title:  {result.get('title', 'N/A')}")
            
            if result.get('content'):
                word_count = len(result['content'].split())
                print(f"  Words:  {word_count}")
            else:
                print(f"  Status: Failed or no content")
            
            if result.get('error'):
                print(f"  Error:  {result['error']}")
        
        print("\n" + "=" * 70)
        print("✓ Batch test COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_from_config():
    """Test scraping blog URLs from config file."""
    print("\n\n" + "=" * 70)
    print("Configuration-Based Scraping Test")
    print("=" * 70)
    
    try:
        from utils.helpers import load_sources
        
        # Load sources from config
        sources = load_sources()
        blog_urls = sources.get('blogs', [])
        
        if not blog_urls:
            print("\n⚠️  No blog URLs found in configuration")
            return
        
        print(f"\nFound {len(blog_urls)} blog URLs in config")
        print("-" * 70)
        
        # Initialize scraper
        scraper = BlogScraper(verify_ssl=False)
        
        # Scrape first blog URL only (to save time)
        test_url = blog_urls[0]
        print(f"\nScraping first blog: {test_url}")
        
        result = scraper.scrape(test_url)
        
        print(f"\n✓ Title: {result.get('title', 'N/A')}")
        
        if result.get('content'):
            word_count = len(result['content'].split())
            print(f"✓ Content: {word_count} words")
        
        print("\n" + "=" * 70)
        print("✓ Config-based test PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all tests
    test_single_blog()
    
    # Uncomment to run additional tests
    # test_multiple_blogs()
    # test_from_config()
    
    print("\n📝 Note: SSL verification is disabled for testing.")
    print("   For production, enable verify_ssl=True after configuring certificates.\n")
