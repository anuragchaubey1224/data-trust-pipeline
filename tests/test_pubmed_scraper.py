"""
Test script for PubMedScraper (API version).

This script demonstrates the PubMedScraper functionality by scraping
a sample PubMed article using the NCBI E-utilities API.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.pubmed_scraper import PubMedScraper


def test_single_article():
    """Test scraping a single PubMed article via API."""
    print("=" * 80)
    print("PubMed Scraper Test (E-utilities API)")
    print("=" * 80)
    
    # Initialize scraper
    scraper = PubMedScraper(timeout=30)
    
    # Test URL - PubMed article on gut microbiome
    test_url = "https://pubmed.ncbi.nlm.nih.gov/31452104/"
    
    print(f"\nScraping: {test_url}")
    print("-" * 80)
    
    try:
        # Scrape the PubMed article
        result = scraper.scrape(test_url)
        
        # Display extracted information
        print("\n✓ SCRAPING SUCCESSFUL\n")
        
        print(f"Source URL:      {result['source_url']}")
        print(f"Source Type:     {result['source_type']}")
        print(f"Title:           {result['title'] or 'N/A'}")
        print(f"Authors:         {result['author'] or 'N/A'}")
        print(f"Published:       {result['published_date'] or 'N/A'}")
        
        # Show journal (description field)
        journal = result['description']
        if journal:
            journal_preview = journal[:100] + "..." if len(journal) > 100 else journal
            print(f"Journal:         {journal_preview}")
        else:
            print(f"Journal:         N/A")
        
        # Show abstract statistics
        abstract = result['content']
        if abstract:
            word_count = len(abstract.split())
            char_count = len(abstract)
            paragraphs = abstract.count('\n\n') + 1
            
            print(f"\nAbstract Statistics:")
            print(f"  - Words:       {word_count}")
            print(f"  - Characters:  {char_count}")
            print(f"  - Paragraphs:  {paragraphs}")
            
            # Show abstract preview
            abstract_preview = abstract[:400] + "..." if len(abstract) > 400 else abstract
            print(f"\nAbstract Preview:")
            print("-" * 80)
            print(abstract_preview)
            print("-" * 80)
        else:
            print(f"\n⚠️  Warning: No abstract extracted")
        
        print("\n" + "=" * 80)
        print("✓ Test PASSED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_multiple_articles():
    """Test scraping multiple PubMed articles via API."""
    print("\n\n" + "=" * 80)
    print("Multiple PubMed Articles Scraping Test (E-utilities API)")
    print("=" * 80)
    
    # Initialize scraper
    scraper = PubMedScraper(timeout=30)
    
    # Test URLs - various PubMed articles
    test_urls = [
        "https://pubmed.ncbi.nlm.nih.gov/31452104/",  # Gut microbiome
        "https://pubmed.ncbi.nlm.nih.gov/32887691/",  # Machine learning in medicine
        "https://pubmed.ncbi.nlm.nih.gov/33692374/",  # COVID-19 research
    ]
    
    results = []
    
    print(f"\nScraping {len(test_urls)} PubMed articles...")
    print("-" * 80)
    
    for idx, url in enumerate(test_urls, 1):
        print(f"\n[{idx}/{len(test_urls)}] Processing: {url}")
        
        try:
            result = scraper.scrape(url)
            results.append(result)
            
            # Show brief info
            title = result['title']
            title_preview = (title[:50] + "...") if title and len(title) > 50 else (title or "N/A")
            
            abstract = result['content']
            word_count = len(abstract.split()) if abstract else 0
            
            print(f"  ✓ Title: {title_preview}")
            print(f"  ✓ Authors: {result['author'] or 'N/A'}")
            print(f"  ✓ Abstract: {word_count} words")
            
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            results.append(None)
    
    # Summary
    print("\n" + "=" * 80)
    print("SCRAPING SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r and r['content'])
    failed = len(results) - successful
    
    print(f"\nTotal articles:       {len(test_urls)}")
    print(f"Successfully scraped: {successful}")
    print(f"Failed:               {failed}")
    
    # Display successfully scraped articles
    if successful > 0:
        print("\n" + "-" * 80)
        print("SUCCESSFULLY SCRAPED ARTICLES:")
        print("-" * 80)
        
        for idx, result in enumerate(results, 1):
            if result and result['content']:
                print(f"\n[Article {idx}]")
                print(f"  URL:        {result['source_url']}")
                
                title = result['title']
                title_display = (title[:60] + "...") if title and len(title) > 60 else (title or "N/A")
                print(f"  Title:      {title_display}")
                
                print(f"  Authors:    {result['author'] or 'N/A'}")
                print(f"  Published:  {result['published_date'] or 'N/A'}")
                
                abstract = result['content']
                word_count = len(abstract.split()) if abstract else 0
                print(f"  Abstract:   {word_count} words")
                
                # Preview
                if abstract:
                    preview = abstract[:180] + "..." if len(abstract) > 180 else abstract
                    print(f"  Preview:    {preview}")
    
    print("\n" + "=" * 80)
    print("✓ Test COMPLETED")
    print("=" * 80)


def main():
    """Run all tests."""
    # Test single article
    test_single_article()
    
    # Test multiple articles
    test_multiple_articles()


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()
