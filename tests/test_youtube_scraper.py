"""
Test script for YouTubeScraper.

This script demonstrates the YouTubeScraper functionality by scraping
a sample YouTube video and displaying the extracted information.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.youtube_scraper import YouTubeScraper


def test_single_video():
    """Test scraping a single YouTube video."""
    print("=" * 70)
    print("YouTube Scraper Test")
    print("=" * 70)
    
    # Initialize scraper
    scraper = YouTubeScraper()
    
    # Test URL - 3Blue1Brown neural network video
    test_url = "https://www.youtube.com/watch?v=aircAruvnKk"
    
    print(f"\nScraping: {test_url}")
    print("-" * 70)
    
    try:
        # Scrape the video
        result = scraper.scrape(test_url)
        
        # Display extracted information
        print("\n✓ SCRAPING SUCCESSFUL\n")
        
        print(f"Source URL:      {result['source_url']}")
        print(f"Source Type:     {result['source_type']}")
        print(f"Title:           {result['title'] or 'N/A'}")
        print(f"Channel:         {result['author'] or 'N/A'}")
        print(f"Published Date:  {result['published_date'] or 'N/A'}")
        
        # Show description (truncated)
        desc = result['description']
        if desc:
            desc_preview = desc[:150] + "..." if len(desc) > 150 else desc
            print(f"Description:     {desc_preview}")
        else:
            print(f"Description:     N/A")
        
        # Show transcript statistics
        transcript = result['content']
        if transcript:
            word_count = len(transcript.split())
            char_count = len(transcript)
            
            print(f"\nTranscript Statistics:")
            print(f"  - Words:       {word_count}")
            print(f"  - Characters:  {char_count}")
            
            # Show transcript preview
            transcript_preview = transcript[:300] + "..." if len(transcript) > 300 else transcript
            print(f"\nTranscript Preview:")
            print("-" * 70)
            print(transcript_preview)
            print("-" * 70)
        else:
            print(f"\n⚠️  Warning: No transcript available for this video")
        
        print("\n" + "=" * 70)
        print("✓ Test PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_video_id_extraction():
    """Test video ID extraction from various URL formats."""
    print("\n\n" + "=" * 70)
    print("Video ID Extraction Test")
    print("=" * 70)
    
    scraper = YouTubeScraper()
    
    test_urls = [
        "https://www.youtube.com/watch?v=aircAruvnKk",
        "https://youtu.be/aircAruvnKk",
        "https://www.youtube.com/embed/aircAruvnKk",
        "aircAruvnKk"
    ]
    
    print("\nTesting various URL formats:")
    print("-" * 70)
    
    for url in test_urls:
        try:
            video_id = scraper.extract_video_id(url)
            print(f"✓ {url[:50]:50s} → {video_id}")
        except Exception as e:
            print(f"✗ {url[:50]:50s} → Error: {e}")
    
    print("\n" + "=" * 70)
    print("✓ ID Extraction Test COMPLETED")
    print("=" * 70)


def test_multiple_videos():
    """Test scraping multiple YouTube videos."""
    print("\n\n" + "=" * 70)
    print("Multiple Videos Scraping Test")
    print("=" * 70)
    
    # Initialize scraper
    scraper = YouTubeScraper()
    
    # Test URLs - Both from 3Blue1Brown
    test_urls = [
        "https://www.youtube.com/watch?v=aircAruvnKk",  # Neural networks
        "https://www.youtube.com/watch?v=ua-CiDNNj30",  # Gradient descent
    ]
    
    print(f"\nScraping {len(test_urls)} YouTube videos...")
    print("-" * 70)
    
    try:
        results = scraper.scrape_multiple(test_urls)
        
        print(f"\n✓ Scraped {len(results)} videos\n")
        
        # Display summary for each
        for idx, result in enumerate(results, 1):
            print(f"\n[Video {idx}]")
            print(f"  URL:     {result['source_url'][:60]}...")
            print(f"  Title:   {result.get('title', 'N/A')[:60]}...")
            print(f"  Channel: {result.get('author', 'N/A')}")
            
            if result.get('content'):
                word_count = len(result['content'].split())
                print(f"  Transcript: {word_count} words")
            else:
                print(f"  Transcript: Not available")
            
            if result.get('error'):
                print(f"  Error:   {result['error']}")
        
        print("\n" + "=" * 70)
        print("✓ Batch test COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_from_config():
    """Test scraping YouTube URLs from config file."""
    print("\n\n" + "=" * 70)
    print("Configuration-Based Scraping Test")
    print("=" * 70)
    
    try:
        from utils.helpers import load_sources
        
        # Load sources from config
        sources = load_sources()
        youtube_urls = sources.get('youtube', [])
        
        if not youtube_urls:
            print("\n⚠️  No YouTube URLs found in configuration")
            return
        
        print(f"\nFound {len(youtube_urls)} YouTube URLs in config")
        print("-" * 70)
        
        # Initialize scraper
        scraper = YouTubeScraper()
        
        # Scrape first video only (to save time)
        test_url = youtube_urls[0]
        print(f"\nScraping first video: {test_url}")
        
        result = scraper.scrape(test_url)
        
        print(f"\n✓ Title: {result.get('title', 'N/A')}")
        print(f"✓ Channel: {result.get('author', 'N/A')}")
        
        if result.get('content'):
            word_count = len(result['content'].split())
            print(f"✓ Transcript: {word_count} words")
        else:
            print(f"⚠️  Transcript: Not available")
        
        print("\n" + "=" * 70)
        print("✓ Config-based test PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run all tests
    test_single_video()
    
    # Uncomment to run additional tests
    # test_video_id_extraction()
    # test_multiple_videos()
    # test_from_config()
    
    print("\n📝 Note: YouTube scraping may take time for downloading metadata.")
    print("   Transcripts may not be available for all videos.\n")
