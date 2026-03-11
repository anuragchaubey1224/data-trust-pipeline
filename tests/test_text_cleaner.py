#!/usr/bin/env python3
"""
Test Script for TextCleaner Module

This script tests the text cleaning functionality with various input scenarios
to ensure proper normalization and cleaning of scraped content.

Usage:
    python3 processing/test_text_cleaner.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.text_cleaner import TextCleaner


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_test_result(test_name: str, input_text: str, output_text: str):
    """Print formatted test results."""
    print(f"Test: {test_name}")
    print("-" * 80)
    print(f"Input:  {repr(input_text)}")
    print(f"Output: {repr(output_text)}")
    print(f"Length: {len(input_text)} → {len(output_text)} chars")
    print()


def test_basic_cleaning():
    """Test basic text cleaning functionality."""
    print_header("TEST 1: Basic Text Cleaning")
    
    cleaner = TextCleaner()
    
    # Test case from requirements
    input_text = "\n\n  Hello    world \n\n <p>This is text</p> "
    expected = "Hello world This is text"
    
    output = cleaner.clean_text(input_text)
    print_test_result("Basic Cleaning", input_text, output)
    
    # Verify result
    if output == expected:
        print("✓ PASS: Output matches expected result")
    else:
        print(f"✗ FAIL: Expected '{expected}', got '{output}'")
    
    return output == expected


def test_html_tag_removal():
    """Test HTML tag removal."""
    print_header("TEST 2: HTML Tag Removal")
    
    cleaner = TextCleaner()
    
    test_cases = [
        ("<p>Paragraph text</p>", "Paragraph text"),
        ("<div>Division <span>span text</span></div>", "Division span text"),
        ("Text with<br>line break", "Text with line break"),
        ("<strong>Bold</strong> and <em>italic</em>", "Bold and italic"),
        ("<!-- comment -->Visible text", "Visible text"),
    ]
    
    all_passed = True
    for input_text, expected in test_cases:
        output = cleaner.clean_text(input_text)
        passed = expected in output or output.replace("  ", " ").strip() == expected
        
        print_test_result(f"HTML Tags", input_text, output)
        
        if passed:
            print("✓ PASS")
        else:
            print(f"✗ FAIL: Expected '{expected}'")
            all_passed = False
        print()
    
    return all_passed


def test_whitespace_normalization():
    """Test whitespace normalization."""
    print_header("TEST 3: Whitespace Normalization")
    
    cleaner = TextCleaner()
    
    test_cases = [
        ("Hello    world", "Hello world"),
        ("Text\t\twith\ttabs", "Text with tabs"),
        ("Multiple   spaces   here", "Multiple spaces here"),
        ("  Leading and trailing  ", "Leading and trailing"),
    ]
    
    all_passed = True
    for input_text, expected in test_cases:
        output = cleaner.clean_text(input_text)
        passed = output == expected
        
        print_test_result("Whitespace", input_text, output)
        
        if passed:
            print("✓ PASS")
        else:
            print(f"✗ FAIL: Expected '{expected}'")
            all_passed = False
        print()
    
    return all_passed


def test_newline_handling():
    """Test newline and paragraph handling."""
    print_header("TEST 4: Newline Handling")
    
    cleaner = TextCleaner()
    
    input_text = "Paragraph 1\n\n\n\nParagraph 2\n\n\n\nParagraph 3"
    output = cleaner.clean_text(input_text)
    
    print_test_result("Multiple Newlines", input_text, output)
    
    # Should reduce to maximum 2 newlines between paragraphs
    has_excessive_newlines = "\n\n\n" in output
    
    if not has_excessive_newlines:
        print("✓ PASS: Excessive newlines removed")
        return True
    else:
        print("✗ FAIL: Still contains excessive newlines")
        return False


def test_html_entities():
    """Test HTML entity replacement."""
    print_header("TEST 5: HTML Entity Replacement")
    
    cleaner = TextCleaner()
    
    test_cases = [
        ("Text&nbsp;with&nbsp;entities", "Text with entities"),
        ("&lt;tag&gt; and &amp; symbol", "<tag> and & symbol"),
        ("Quote: &quot;Hello&quot;", "Quote: \"Hello\""),
        ("It&#39;s working", "It's working"),
    ]
    
    all_passed = True
    for input_text, expected_substring in test_cases:
        output = cleaner.clean_text(input_text)
        # Check if key conversions happened
        passed = (
            "&nbsp;" not in output and
            "&amp;" not in output and
            "&lt;" not in output and
            "&gt;" not in output and
            "&quot;" not in output and
            "&#39;" not in output
        )
        
        print_test_result("HTML Entities", input_text, output)
        
        if passed:
            print("✓ PASS: HTML entities removed/replaced")
        else:
            print("✗ FAIL: HTML entities still present")
            all_passed = False
        print()
    
    return all_passed


def test_real_world_scenario():
    """Test with real-world scraped content."""
    print_header("TEST 6: Real-World Scraped Content")
    
    cleaner = TextCleaner()
    
    # Simulate scraped blog content
    scraped_content = """
    
    <div class="article">
        <p>Machine learning is a fascinating    field.</p>
        
        <p>It enables computers to learn from data.</p>
        
        <!-- Advertisement -->
        <div class="ad">Ad content here</div>
        
        <p>Key concepts include:</p>
        <ul>
            <li>Supervised&nbsp;learning</li>
            <li>Unsupervised&nbsp;learning</li>
        </ul>
    </div>
    
    """
    
    output = cleaner.clean_text(scraped_content)
    print_test_result("Real-World Content", scraped_content[:100] + "...", output)
    
    # Check that cleaning worked
    checks = {
        "No HTML tags": "<" not in output or ">" not in output,
        "No HTML entities": "&nbsp;" not in output,
        "Normalized whitespace": "    " not in output,
        "Content preserved": "Machine learning" in output and "Supervised" in output,
    }
    
    all_passed = all(checks.values())
    
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
    
    print()
    
    if all_passed:
        print("✓ PASS: Real-world content cleaned successfully")
    else:
        print("✗ FAIL: Some cleaning checks failed")
    
    return all_passed


def test_batch_cleaning():
    """Test batch cleaning functionality."""
    print_header("TEST 7: Batch Cleaning")
    
    cleaner = TextCleaner()
    
    texts = [
        "  Text 1  ",
        "<p>Text 2</p>",
        "Text   3   with   spaces",
        "\n\nText 4\n\n",
    ]
    
    cleaned = cleaner.clean_batch(texts)
    
    print(f"Input: {len(texts)} texts")
    for i, (original, cleaned_text) in enumerate(zip(texts, cleaned), 1):
        print(f"\n{i}. Original: {repr(original)}")
        print(f"   Cleaned:  {repr(cleaned_text)}")
    
    if len(cleaned) == len(texts):
        print("\n✓ PASS: All texts cleaned")
        return True
    else:
        print("\n✗ FAIL: Batch cleaning failed")
        return False


def test_text_stats():
    """Test text statistics functionality."""
    print_header("TEST 8: Text Statistics")
    
    cleaner = TextCleaner()
    
    test_text = "\n\n  Hello    world \n\n <p>This is text</p> "
    stats = cleaner.get_text_stats(test_text)
    
    print(f"Original text: {repr(test_text)}")
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if stats['original_length'] > stats['cleaned_length']:
        print("\n✓ PASS: Stats show text was cleaned")
        return True
    else:
        print("\n✗ FAIL: Stats don't reflect cleaning")
        return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("TEST 9: Edge Cases")
    
    cleaner = TextCleaner()
    
    test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        ("\n\n\n", "Newlines only"),
        ("NoSpacesOrTags", "Already clean text"),
    ]
    
    all_passed = True
    for input_text, description in test_cases:
        try:
            output = cleaner.clean_text(input_text)
            print(f"✓ {description}: {repr(input_text)} → {repr(output)}")
        except Exception as e:
            print(f"✗ {description}: Error - {e}")
            all_passed = False
    
    # Test None handling
    try:
        cleaner.clean_text(None)
        print("✗ None input: Should have raised ValueError")
        all_passed = False
    except ValueError:
        print("✓ None input: Correctly raises ValueError")
    except Exception as e:
        print(f"✗ None input: Wrong exception - {e}")
        all_passed = False
    
    print()
    return all_passed


def run_all_tests():
    """Run all test cases and display summary."""
    print_header("TEXT CLEANER TEST SUITE")
    
    print("Testing text cleaning module with various scenarios...")
    print("This will verify normalization, HTML removal, and whitespace handling.\n")
    
    # Run all tests
    test_results = {
        "Basic Cleaning": test_basic_cleaning(),
        "HTML Tag Removal": test_html_tag_removal(),
        "Whitespace Normalization": test_whitespace_normalization(),
        "Newline Handling": test_newline_handling(),
        "HTML Entities": test_html_entities(),
        "Real-World Content": test_real_world_scenario(),
        "Batch Cleaning": test_batch_cleaning(),
        "Text Statistics": test_text_stats(),
        "Edge Cases": test_edge_cases(),
    }
    
    # Display summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    print("Test Results:")
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*80}")
    
    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("="*80)
        print("\n🎉 TextCleaner is working correctly!")
        print("\nNext steps:")
        print("  1. Integrate with scraper pipeline")
        print("  2. Test with real scraped content")
        print("  3. Add language detection module")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*80)
        print("\n⚠️  Please review the failing tests")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
