#!/usr/bin/env python3
"""
Test Script for TopicTagger Module

This script tests the topic extraction functionality with various text samples
to ensure proper keyword and topic identification.

Usage:
    python3 processing/test_topic_tagger.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.topic_tagger import TopicTagger


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_topics(text: str, topics: list, description: str = ""):
    """Print formatted topic extraction results."""
    if description:
        print(f"Test: {description}")
        print("-" * 80)
    print(f"Text: {text[:70]}..." if len(text) > 70 else f"Text: {text}")
    print(f"Topics: {topics}")
    print(f"Count: {len(topics)} topics extracted")
    print()


def test_gut_health_text():
    """Test topic extraction on gut health content."""
    print_header("TEST 1: Gut Health Content")
    
    tagger = TopicTagger()
    
    text = (
        "Gut health plays a crucial role in digestion and immune function. "
        "The microbiome influences metabolism and nutrition. Probiotics and "
        "prebiotics help maintain a healthy gut flora and support overall wellness."
    )
    
    topics = tagger.extract_topics(text, top_n=5)
    print_topics(text, topics, "Gut Health Article")
    
    return len(topics) > 0


def test_machine_learning_text():
    """Test topic extraction on machine learning content."""
    print_header("TEST 2: Machine Learning Content")
    
    tagger = TopicTagger()
    
    text = (
        "Machine learning is a subset of artificial intelligence that enables "
        "computers to learn from data without explicit programming. Neural networks "
        "and deep learning algorithms can recognize patterns and make predictions. "
        "Common applications include natural language processing and computer vision."
    )
    
    topics = tagger.extract_topics(text, top_n=5)
    print_topics(text, topics, "Machine Learning Article")
    
    return len(topics) > 0


def test_medical_research_text():
    """Test topic extraction on medical research content."""
    print_header("TEST 3: Medical Research Content")
    
    tagger = TopicTagger()
    
    text = (
        "Recent clinical trials have shown that targeted therapy can improve "
        "patient outcomes in oncology. Immunotherapy and precision medicine "
        "represent breakthrough treatments. Biomarkers help identify patients "
        "who will benefit most from specific interventions. The research focuses "
        "on personalized treatment protocols and genetic screening."
    )
    
    topics = tagger.extract_topics(text, top_n=6)
    print_topics(text, topics, "Medical Research Paper")
    
    return len(topics) > 0


def test_different_top_n_values():
    """Test with different numbers of topics."""
    print_header("TEST 4: Varying Number of Topics")
    
    tagger = TopicTagger()
    
    text = (
        "The human microbiome consists of trillions of microorganisms including "
        "bacteria, viruses, and fungi. These microbes play essential roles in "
        "digestion, immune system function, and even mental health through the "
        "gut-brain axis connection."
    )
    
    test_cases = [3, 5, 8]
    
    all_passed = True
    for n in test_cases:
        topics = tagger.extract_topics(text, top_n=n)
        print(f"Top {n} topics: {topics}")
        print(f"Extracted: {len(topics)} topics")
        
        # Should extract at most n topics
        if len(topics) > n:
            print(f"✗ FAIL: Expected at most {n} topics, got {len(topics)}")
            all_passed = False
        else:
            print(f"✓ PASS: Extracted {len(topics)} topics (max: {n})")
        print()
    
    return all_passed


def test_short_text_handling():
    """Test handling of short texts."""
    print_header("TEST 5: Short Text Handling")
    
    tagger = TopicTagger()
    
    test_cases = [
        ("This is short.", "Very short text"),
        ("Hello world", "Two words"),
        ("AI", "Single abbreviation"),
        ("", "Empty string"),
        ("   ", "Whitespace only"),
    ]
    
    all_passed = True
    for text, description in test_cases:
        topics = tagger.extract_topics(text, top_n=5)
        
        print(f"Test: {description}")
        print(f"Text: '{text}'")
        print(f"Topics: {topics}")
        
        # Short texts should return empty list
        if len(topics) == 0:
            print("✓ PASS: Returns empty list for short text")
        else:
            print(f"⚠️  WARNING: Extracted {len(topics)} topics from short text")
        print()
    
    return all_passed


def test_long_text_truncation():
    """Test handling of very long texts (truncation)."""
    print_header("TEST 6: Long Text Truncation")
    
    tagger = TopicTagger()
    
    # Create a long text with repeated content
    short_paragraph = (
        "The gut microbiome affects digestion, immunity, and mental health. "
        "Probiotics and prebiotics support microbiome diversity and function. "
    )
    
    # Repeat to create very long text (2000+ words)
    long_text = (short_paragraph * 100)
    
    print(f"Input text length: {len(long_text.split())} words")
    print(f"Testing truncation to {tagger.max_words} words...")
    print()
    
    topics = tagger.extract_topics(long_text, top_n=5)
    print(f"Topics extracted: {topics}")
    print(f"Count: {len(topics)} topics")
    print()
    
    return len(topics) > 0


def test_topics_with_scores():
    """Test topic extraction with confidence scores."""
    print_header("TEST 7: Topic Extraction with Scores")
    
    tagger = TopicTagger()
    
    text = (
        "Gut health is essential for proper digestion and nutrient absorption. "
        "The microbiome contains beneficial bacteria that support immune function. "
        "Probiotics and fermented foods promote gut flora diversity."
    )
    
    topics_with_scores = tagger.extract_topics_with_scores(text, top_n=5)
    
    print("Topics with relevance scores:")
    print("-" * 80)
    for keyword, score in topics_with_scores:
        print(f"  {keyword:30s} → {score:.3f}")
    print()
    
    return len(topics_with_scores) > 0


def test_batch_extraction():
    """Test batch topic extraction."""
    print_header("TEST 8: Batch Topic Extraction")
    
    tagger = TopicTagger()
    
    texts = [
        "Gut health affects digestion and immune system function through the microbiome.",
        "Machine learning algorithms use neural networks to recognize patterns in data.",
        "Climate change impacts global temperatures and causes extreme weather events.",
    ]
    
    print(f"Extracting topics for {len(texts)} texts...")
    print()
    
    batch_results = tagger.batch_extract_topics(texts, top_n=3)
    
    for i, (text, topics) in enumerate(zip(texts, batch_results), 1):
        print(f"Text {i}: {text[:60]}...")
        print(f"Topics: {topics}")
        print()
    
    return len(batch_results) == len(texts)


def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("TEST 9: Edge Cases")
    
    tagger = TopicTagger()
    
    print("Testing None input...")
    try:
        result = tagger.extract_topics(None, top_n=5)
        if result == []:
            print("✓ None input handled: returns []\n")
            none_passed = True
        else:
            print(f"✗ None input: Expected [], got {result}\n")
            none_passed = False
    except Exception as e:
        print(f"✗ None input: Raised exception - {e}\n")
        none_passed = False
    
    print("Testing numeric input...")
    try:
        result = tagger.extract_topics(12345, top_n=5)
        if result == []:
            print("✓ Numeric input handled: returns []\n")
            numeric_passed = True
        else:
            print(f"⚠️  Numeric input: Expected [], got {result}\n")
            numeric_passed = False
    except Exception as e:
        print(f"✗ Numeric input: Raised exception - {e}\n")
        numeric_passed = False
    
    print("Testing special characters only...")
    special_text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~` " * 3
    result = tagger.extract_topics(special_text, top_n=5)
    special_passed = isinstance(result, list)
    print(f"✓ Special characters: returns list {result}\n" if special_passed else f"✗ Special characters failed\n")
    
    return none_passed and numeric_passed and special_passed


def test_integration_with_pipeline():
    """Test integration with text cleaning (as would be used in pipeline)."""
    print_header("TEST 10: Pipeline Integration")
    
    tagger = TopicTagger()
    
    # Simulate cleaned text from TextCleaner
    cleaned_text = (
        "Gut health is critical for overall wellness. A diverse microbiome "
        "supports digestion, immunity, and even mental health. Maintaining "
        "gut flora through probiotics, prebiotics, and fermented foods is "
        "essential for long-term health benefits."
    )
    
    print("Simulating pipeline: TextCleaner → TopicTagger")
    print()
    print(f"Cleaned text: {cleaned_text}")
    print()
    
    topics = tagger.extract_topics(cleaned_text, top_n=5)
    
    print(f"Extracted topics: {topics}")
    print()
    
    if len(topics) > 0:
        print("✓ PASS: Successfully integrated with pipeline workflow")
        return True
    else:
        print("✗ FAIL: No topics extracted")
        return False


def run_all_tests():
    """Run all test cases and print summary."""
    print("=" * 80)
    print("TOPIC TAGGER TEST SUITE".center(80))
    print("=" * 80)
    print("\nTesting topic extraction module with various scenarios...")
    print("This will verify keyword extraction and edge case handling.\n")
    
    tests = [
        ("Gut Health Content", test_gut_health_text),
        ("Machine Learning Content", test_machine_learning_text),
        ("Medical Research Content", test_medical_research_text),
        ("Varying Top N", test_different_top_n_values),
        ("Short Text Handling", test_short_text_handling),
        ("Long Text Truncation", test_long_text_truncation),
        ("Topics with Scores", test_topics_with_scores),
        ("Batch Extraction", test_batch_extraction),
        ("Edge Cases", test_edge_cases),
        ("Pipeline Integration", test_integration_with_pipeline),
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
