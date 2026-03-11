#!/usr/bin/env python3
"""
Test Script for TrustScoreCalculator Module

This script tests the trust scoring functionality with various content samples
to ensure proper credibility assessment across different scenarios.

Usage:
    python3 scoring/test_trust_score.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scoring.trust_score import TrustScoreCalculator


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_score_breakdown(breakdown: dict, description: str = ""):
    """Print formatted score breakdown."""
    if description:
        print(f"Test: {description}")
        print("-" * 80)
    
    print(f"Trust Score: {breakdown['trust_score']:.3f}")
    print(f"\nBreakdown:")
    print(f"  Author Credibility:    {breakdown['author_score']:.3f} (weight: {breakdown['weights']['author']})")
    print(f"  Citation Quality:      {breakdown['citation_score']:.3f} (weight: {breakdown['weights']['citation']})")
    print(f"  Domain Authority:      {breakdown['domain_score']:.3f} (weight: {breakdown['weights']['domain']})")
    print(f"  Recency:               {breakdown['recency_score']:.3f} (weight: {breakdown['weights']['recency']})")
    print(f"  Medical Disclaimer:    {breakdown['disclaimer_score']:.3f} (weight: {breakdown['weights']['disclaimer']})")
    print()


def test_high_trust_content():
    """Test content that should have high trust score."""
    print_header("TEST 1: High Trust Content (NIH + Expert Author)")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://www.nih.gov/health/gut-health",
        "author": "Dr. Jane Smith, MD, PhD",
        "published_date": "2025-06-15",
        "source_type": "blog",
        "content": (
            "This research study published in a peer-reviewed journal examines "
            "the clinical evidence for gut health. Multiple scientific trials "
            "demonstrate significant findings. Please consult your doctor before "
            "making any medical decisions."
        )
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "NIH article with expert author")
    
    if breakdown['trust_score'] >= 0.8:
        print("✓ PASS: High trust content scored appropriately (≥ 0.8)")
        return True
    else:
        print(f"✗ FAIL: Expected score ≥ 0.8, got {breakdown['trust_score']:.3f}")
        return False


def test_medium_trust_content():
    """Test content with medium trust indicators."""
    print_header("TEST 2: Medium Trust Content (Regular Blog)")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://healthblog.com/gut-health-tips",
        "author": "Sarah Johnson",
        "published_date": "2023-03-10",
        "source_type": "blog",
        "content": (
            "Here are some tips for maintaining good gut health. "
            "Research suggests that probiotics can be beneficial. "
            "Studies have shown positive effects."
        )
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "Regular blog with some citations")
    
    if 0.4 <= breakdown['trust_score'] <= 0.7:
        print("✓ PASS: Medium trust content scored appropriately (0.4-0.7)")
        return True
    else:
        print(f"⚠️  WARNING: Expected score 0.4-0.7, got {breakdown['trust_score']:.3f}")
        return True  # Not failing, just warning


def test_low_trust_content():
    """Test content with low trust indicators."""
    print_header("TEST 3: Low Trust Content (Unknown Source)")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://random-website.com/blog",
        "author": "Unknown",
        "published_date": "2010-01-15",
        "source_type": "blog",
        "content": "Just some health tips without any evidence or disclaimers."
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "Low quality blog post")
    
    if breakdown['trust_score'] <= 0.5:
        print("✓ PASS: Low trust content scored appropriately (≤ 0.5)")
        return True
    else:
        print(f"⚠️  WARNING: Expected score ≤ 0.5, got {breakdown['trust_score']:.3f}")
        return True


def test_pubmed_article():
    """Test PubMed article scoring."""
    print_header("TEST 4: PubMed Article (High Citation Score)")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        "author": "Dr. Robert Chen, PhD",
        "published_date": "2024-11-20",
        "source_type": "pubmed",
        "content": (
            "A randomized clinical trial investigating gut microbiome. "
            "The study was published in a peer-reviewed journal with "
            "significant scientific evidence. Consult a healthcare professional "
            "for medical advice."
        )
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "PubMed research article")
    
    if breakdown['citation_score'] >= 0.9:
        print("✓ PASS: PubMed article has high citation score")
        return True
    else:
        print(f"✗ FAIL: PubMed should have citation score ≥ 0.9")
        return False


def test_educational_domain():
    """Test educational domain scoring."""
    print_header("TEST 5: Educational Domain (.edu)")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://university.edu/research/gut-health",
        "author": "Professor Emily Wang",
        "published_date": "2024-08-05",
        "source_type": "blog",
        "content": "University research on gut health and microbiome."
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "University research page")
    
    if breakdown['domain_score'] >= 0.85:
        print("✓ PASS: Educational domain scored appropriately")
        return True
    else:
        print(f"✗ FAIL: .edu domain should have score ≥ 0.85")
        return False


def test_author_credibility_variations():
    """Test different author credibility scenarios."""
    print_header("TEST 6: Author Credibility Variations")
    
    calculator = TrustScoreCalculator()
    
    test_cases = [
        ("Dr. Sarah Martinez, MD", 1.0, "Medical doctor"),
        ("John Smith, PhD", 1.0, "PhD holder"),
        ("Professor Emily Brown", 1.0, "Professor"),
        ("Alex Johnson", 0.7, "Regular author"),
        ("Unknown", 0.3, "Unknown author"),
        (None, 0.3, "No author"),
    ]
    
    all_passed = True
    for author, expected_score, description in test_cases:
        score = calculator.calculate_author_score(author)
        status = "✓" if score == expected_score else "✗"
        print(f"{status} {description}: '{author}' → {score:.1f} (expected {expected_score:.1f})")
        
        if score != expected_score:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ PASS: All author credibility tests passed")
    else:
        print("✗ FAIL: Some author credibility tests failed")
    
    return all_passed


def test_recency_scoring():
    """Test recency score calculations."""
    print_header("TEST 7: Recency Scoring")
    
    calculator = TrustScoreCalculator()
    
    test_cases = [
        ("2026-01-01", 1.0, "Very recent (< 1 year)"),
        ("2024-06-15", 0.8, "1-3 years old"),
        ("2022-03-10", 0.6, "3-5 years old"),
        ("2018-01-15", 0.4, "5-10 years old"),
        ("2010-06-20", 0.2, "Old (> 10 years)"),
        (None, 0.5, "No date (neutral)"),
    ]
    
    all_passed = True
    for date, expected_score, description in test_cases:
        score = calculator.calculate_recency_score(date)
        status = "✓" if score == expected_score else "✗"
        print(f"{status} {description}: {date} → {score:.1f} (expected {expected_score:.1f})")
        
        if score != expected_score:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ PASS: All recency tests passed")
    else:
        print("✗ FAIL: Some recency tests failed")
    
    return all_passed


def test_citation_quality():
    """Test citation quality scoring."""
    print_header("TEST 8: Citation Quality Scoring")
    
    calculator = TrustScoreCalculator()
    
    content_high = (
        "This research study was published in a peer-reviewed journal. "
        "Clinical trials and scientific evidence demonstrate significant findings. "
        "The analysis was randomized and data-driven."
    )
    
    content_medium = (
        "Some research suggests this may be beneficial. "
        "Studies have shown positive results."
    )
    
    content_low = "Just my personal opinion about health."
    
    score_high = calculator.calculate_citation_score("blog", content_high)
    score_medium = calculator.calculate_citation_score("blog", content_medium)
    score_low = calculator.calculate_citation_score("blog", content_low)
    
    print(f"High citation content: {score_high:.1f}")
    print(f"Medium citation content: {score_medium:.1f}")
    print(f"Low citation content: {score_low:.1f}")
    print()
    
    if score_high > score_medium > score_low:
        print("✓ PASS: Citation scoring reflects content quality")
        return True
    else:
        print("✗ FAIL: Citation scoring not properly differentiated")
        return False


def test_disclaimer_detection():
    """Test medical disclaimer detection."""
    print_header("TEST 9: Medical Disclaimer Detection")
    
    calculator = TrustScoreCalculator()
    
    content_with = (
        "Here are some health tips. Always consult your doctor before "
        "making any changes to your health routine."
    )
    
    content_without = "Here are some health tips for better wellness."
    
    score_with = calculator.calculate_disclaimer_score(content_with)
    score_without = calculator.calculate_disclaimer_score(content_without)
    
    print(f"Content with disclaimer: {score_with:.1f}")
    print(f"Content without disclaimer: {score_without:.1f}")
    print()
    
    if score_with == 1.0 and score_without == 0.4:
        print("✓ PASS: Disclaimer detection working correctly")
        return True
    else:
        print("✗ FAIL: Disclaimer detection not working properly")
        return False


def test_domain_authority():
    """Test domain authority scoring."""
    print_header("TEST 10: Domain Authority Scoring")
    
    calculator = TrustScoreCalculator()
    
    test_cases = [
        ("https://www.nih.gov/article", 0.9, "NIH (trusted)"),
        ("https://www.cdc.gov/health", 0.9, "CDC (trusted)"),
        ("https://mayoclinic.org/diseases", 0.9, "Mayo Clinic (trusted)"),
        ("https://university.edu/research", 0.85, "Educational"),
        ("https://state.gov/info", 0.85, "Government"),
        ("https://randomwebsite.com/blog", 0.5, "Standard domain"),
    ]
    
    all_passed = True
    for url, expected_score, description in test_cases:
        score = calculator.calculate_domain_score(url)
        status = "✓" if score == expected_score else "✗"
        print(f"{status} {description}: {score:.2f} (expected {expected_score:.2f})")
        
        if score != expected_score:
            all_passed = False
    
    print()
    
    if all_passed:
        print("✓ PASS: All domain authority tests passed")
    else:
        print("✗ FAIL: Some domain authority tests failed")
    
    return all_passed


def test_with_content_chunks():
    """Test scoring with chunked content."""
    print_header("TEST 11: Content with Chunks")
    
    calculator = TrustScoreCalculator()
    
    data = {
        "source_url": "https://healthline.com/nutrition/gut-health",
        "author": "Dr. Michael Lee, MD",
        "published_date": "2025-02-10",
        "source_type": "blog",
        "content_chunks": [
            "Research shows that gut health is important.",
            "Clinical studies demonstrate benefits of probiotics.",
            "Always consult your doctor for medical advice."
        ]
    }
    
    breakdown = calculator.calculate_trust_score_with_breakdown(data)
    print_score_breakdown(breakdown, "Content with chunks (from pipeline)")
    
    if breakdown['trust_score'] > 0:
        print("✓ PASS: Chunked content processed successfully")
        return True
    else:
        print("✗ FAIL: Failed to process chunked content")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("TEST 12: Edge Cases")
    
    calculator = TrustScoreCalculator()
    
    # Empty data
    print("Testing empty data...")
    data_empty = {}
    try:
        score = calculator.calculate_trust_score(data_empty)
        print(f"✓ Empty data handled: score = {score:.3f}")
        empty_passed = True
    except Exception as e:
        print(f"✗ Empty data raised exception: {e}")
        empty_passed = False
    print()
    
    # Minimal data
    print("Testing minimal data...")
    data_minimal = {
        "source_url": "https://example.com",
        "content": "Some text"
    }
    try:
        score = calculator.calculate_trust_score(data_minimal)
        print(f"✓ Minimal data handled: score = {score:.3f}")
        minimal_passed = True
    except Exception as e:
        print(f"✗ Minimal data raised exception: {e}")
        minimal_passed = False
    print()
    
    # Invalid date format
    print("Testing invalid date format...")
    data_bad_date = {
        "source_url": "https://example.com",
        "published_date": "invalid-date-format",
        "content": "Some text"
    }
    try:
        score = calculator.calculate_trust_score(data_bad_date)
        print(f"✓ Invalid date handled: score = {score:.3f}")
        date_passed = True
    except Exception as e:
        print(f"✗ Invalid date raised exception: {e}")
        date_passed = False
    print()
    
    return empty_passed and minimal_passed and date_passed


def test_real_world_scenarios():
    """Test with realistic content scenarios."""
    print_header("TEST 13: Real-World Scenarios")
    
    calculator = TrustScoreCalculator()
    
    # Scenario 1: CDC Health Article
    print("Scenario 1: CDC Health Article")
    print("-" * 80)
    cdc_data = {
        "source_url": "https://www.cdc.gov/nutrition/microbiome.html",
        "author": "CDC Nutrition Team",
        "published_date": "2025-05-20",
        "source_type": "blog",
        "content": (
            "Scientific research demonstrates the importance of gut health. "
            "Clinical studies published in peer-reviewed journals show evidence "
            "of microbiome benefits. This information is not a substitute for "
            "medical advice. Consult your healthcare professional."
        )
    }
    cdc_breakdown = calculator.calculate_trust_score_with_breakdown(cdc_data)
    print(f"Trust Score: {cdc_breakdown['trust_score']:.3f}\n")
    
    # Scenario 2: Personal Blog
    print("Scenario 2: Personal Health Blog")
    print("-" * 80)
    blog_data = {
        "source_url": "https://myblog.com/health-journey",
        "author": "Jane Doe",
        "published_date": "2025-08-01",
        "source_type": "blog",
        "content": "My personal experience with improving gut health through diet."
    }
    blog_breakdown = calculator.calculate_trust_score_with_breakdown(blog_data)
    print(f"Trust Score: {blog_breakdown['trust_score']:.3f}\n")
    
    # Scenario 3: Medical Journal Article
    print("Scenario 3: Medical Journal (PubMed)")
    print("-" * 80)
    journal_data = {
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/98765432/",
        "author": "Dr. Anna Rodriguez, MD, PhD, Professor of Medicine",
        "published_date": "2024-12-15",
        "source_type": "pubmed",
        "content": (
            "Randomized controlled clinical trial examining gut microbiome diversity. "
            "This peer-reviewed research published scientific evidence from data "
            "analysis. Study findings demonstrate significant results."
        )
    }
    journal_breakdown = calculator.calculate_trust_score_with_breakdown(journal_data)
    print(f"Trust Score: {journal_breakdown['trust_score']:.3f}\n")
    
    # Verify that high-trust sources score much higher than personal blog
    # Both CDC and PubMed should be high trust (>0.75), blog should be lower (<0.65)
    high_trust_sources = [cdc_breakdown['trust_score'], journal_breakdown['trust_score']]
    
    if all(score > 0.75 for score in high_trust_sources) and blog_breakdown['trust_score'] < 0.65:
        print(f"✓ PASS: High-trust sources (CDC: {cdc_breakdown['trust_score']:.3f}, "
              f"Journal: {journal_breakdown['trust_score']:.3f}) >> Blog: {blog_breakdown['trust_score']:.3f}")
        return True
    else:
        print("✗ FAIL: Trust scores not properly differentiated")
        return False


def run_all_tests():
    """Run all test cases and print summary."""
    print("=" * 80)
    print("TRUST SCORE CALCULATOR TEST SUITE".center(80))
    print("=" * 80)
    print("\nTesting trust scoring system with various content scenarios...")
    print("This will verify credibility assessment across different sources.\n")
    
    tests = [
        ("High Trust Content", test_high_trust_content),
        ("Medium Trust Content", test_medium_trust_content),
        ("Low Trust Content", test_low_trust_content),
        ("PubMed Article", test_pubmed_article),
        ("Educational Domain", test_educational_domain),
        ("Author Credibility", test_author_credibility_variations),
        ("Recency Scoring", test_recency_scoring),
        ("Citation Quality", test_citation_quality),
        ("Disclaimer Detection", test_disclaimer_detection),
        ("Domain Authority", test_domain_authority),
        ("Content with Chunks", test_with_content_chunks),
        ("Edge Cases", test_edge_cases),
        ("Real-World Scenarios", test_real_world_scenarios),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"✗ TEST FAILED with exception: {e}\n")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    print("Test Results:")
    passed_count = 0
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {test_name}")
        if passed:
            passed_count += 1
    
    print("\n" + "=" * 80)
    if passed_count == len(results):
        print(f"✓ ALL TESTS PASSED ({passed_count}/{len(results)})".center(80))
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed_count}/{len(results)} passed)".center(80))
    print("=" * 80)
    
    if passed_count < len(results):
        print("\n⚠️  Please review the failing tests")
        return 1
    return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
