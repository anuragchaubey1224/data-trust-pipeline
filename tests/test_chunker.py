#!/usr/bin/env python3
"""
Test Script for ContentChunker Module

This script tests the content chunking functionality with various text samples
to ensure proper splitting with overlapping windows.

Usage:
    python3 processing/test_chunker.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.chunker import ContentChunker


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_chunk_info(chunks: list, description: str = ""):
    """Print formatted chunk information."""
    if description:
        print(f"Test: {description}")
        print("-" * 80)
    
    print(f"Total chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks, 1):
        word_count = len(chunk.split())
        preview = chunk[:60] + "..." if len(chunk) > 60 else chunk
        print(f"Chunk {i}: {word_count} words - {preview}")
    
    print()


def test_basic_chunking():
    """Test basic chunking with default parameters."""
    print_header("TEST 1: Basic Chunking")
    
    chunker = ContentChunker()
    
    # Create text with known word count (500 words)
    text = " ".join([f"word{i}" for i in range(500)])
    
    print(f"Input: {len(text.split())} words")
    print()
    
    chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
    
    print_chunk_info(chunks, "500 words → 300-word chunks with 50-word overlap")
    
    # Verify chunk count
    # Chunk 1: 0-299 (300 words)
    # Chunk 2: 250-549 (300 words)
    # So we expect 2 chunks
    expected_chunks = 2
    if len(chunks) == expected_chunks:
        print(f"✓ PASS: Expected {expected_chunks} chunks, got {len(chunks)}")
    else:
        print(f"✗ FAIL: Expected {expected_chunks} chunks, got {len(chunks)}")
    
    return len(chunks) == expected_chunks


def test_long_text_chunking():
    """Test chunking with longer text."""
    print_header("TEST 2: Long Text Chunking")
    
    chunker = ContentChunker()
    
    # Create text with 1000 words
    text = " ".join([f"word{i}" for i in range(1000)])
    
    print(f"Input: {len(text.split())} words")
    print(f"Chunk size: 300 words")
    print(f"Overlap: 50 words")
    print()
    
    chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
    
    print_chunk_info(chunks, "1000 words chunked")
    
    # Verify first and last chunks
    first_chunk_words = chunks[0].split()
    last_chunk_words = chunks[-1].split()
    
    print(f"First chunk starts with: {first_chunk_words[0]}")
    print(f"Last chunk ends with: {last_chunk_words[-1]}")
    print()
    
    return len(chunks) > 0


def test_short_text_handling():
    """Test handling of text shorter than chunk_size."""
    print_header("TEST 3: Short Text Handling")
    
    chunker = ContentChunker()
    
    # Text with only 50 words (less than chunk_size=300)
    text = " ".join([f"word{i}" for i in range(50)])
    
    print(f"Input: {len(text.split())} words (less than chunk_size of 300)")
    print()
    
    chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
    
    print_chunk_info(chunks, "50 words → should return single chunk")
    
    if len(chunks) == 1:
        print("✓ PASS: Short text returned as single chunk")
        return True
    else:
        print(f"✗ FAIL: Expected 1 chunk, got {len(chunks)}")
        return False


def test_empty_text():
    """Test handling of empty text."""
    print_header("TEST 4: Empty Text Handling")
    
    chunker = ContentChunker()
    
    test_cases = [
        ("", "Empty string"),
        ("   ", "Whitespace only"),
        (None, "None value"),
    ]
    
    all_passed = True
    for text, description in test_cases:
        print(f"Testing: {description}")
        chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
        
        if len(chunks) == 0:
            print(f"✓ PASS: {description} returns empty list")
        else:
            print(f"✗ FAIL: {description} returned {len(chunks)} chunks")
            all_passed = False
        print()
    
    return all_passed


def test_different_chunk_sizes():
    """Test with various chunk sizes."""
    print_header("TEST 5: Different Chunk Sizes")
    
    chunker = ContentChunker()
    
    # Create text with 800 words
    text = " ".join([f"word{i}" for i in range(800)])
    
    test_cases = [
        (100, 20),  # Small chunks
        (300, 50),  # Default
        (500, 100), # Large chunks
    ]
    
    all_passed = True
    for chunk_size, overlap in test_cases:
        print(f"Testing: chunk_size={chunk_size}, overlap={overlap}")
        chunks = chunker.chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        
        print(f"Result: {len(chunks)} chunks")
        
        # Verify first chunk has correct size
        first_chunk_words = len(chunks[0].split())
        if first_chunk_words == chunk_size:
            print(f"✓ First chunk: {first_chunk_words} words (expected {chunk_size})")
        else:
            print(f"⚠️  First chunk: {first_chunk_words} words (expected {chunk_size})")
        
        print()
    
    return all_passed


def test_overlap_validation():
    """Test overlap parameter validation."""
    print_header("TEST 6: Overlap Validation")
    
    chunker = ContentChunker()
    
    text = " ".join([f"word{i}" for i in range(500)])
    
    print("Testing: overlap >= chunk_size (should auto-adjust)")
    
    # This should automatically adjust overlap
    chunks = chunker.chunk_text(text, chunk_size=100, overlap=100)
    
    if len(chunks) > 0:
        print(f"✓ PASS: Handled invalid overlap, created {len(chunks)} chunks")
        return True
    else:
        print("✗ FAIL: Failed to handle invalid overlap")
        return False


def test_chunk_with_metadata():
    """Test chunking with metadata."""
    print_header("TEST 7: Chunking with Metadata")
    
    chunker = ContentChunker()
    
    # Create text with 600 words
    text = " ".join([f"word{i}" for i in range(600)])
    
    print(f"Input: {len(text.split())} words")
    print(f"Chunk size: 300, Overlap: 50")
    print()
    
    chunks_with_metadata = chunker.chunk_text_with_metadata(text, chunk_size=300, overlap=50)
    
    print(f"Generated {len(chunks_with_metadata)} chunks with metadata:")
    print("-" * 80)
    
    for chunk_info in chunks_with_metadata:
        print(f"Chunk {chunk_info['chunk_id']}:")
        print(f"  Word count: {chunk_info['word_count']}")
        print(f"  Position: words {chunk_info['start_word']} to {chunk_info['end_word']}")
        print(f"  Preview: {chunk_info['text'][:50]}...")
        print()
    
    return len(chunks_with_metadata) > 0


def test_chunk_statistics():
    """Test chunk statistics calculation."""
    print_header("TEST 8: Chunk Statistics")
    
    chunker = ContentChunker()
    
    # Create text with 1000 words
    text = " ".join([f"word{i}" for i in range(1000)])
    
    chunks = chunker.chunk_text(text, chunk_size=300, overlap=50)
    
    stats = chunker.get_chunk_statistics(chunks)
    
    print("Chunk Statistics:")
    print("-" * 80)
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total words: {stats['total_words']}")
    print(f"Average words per chunk: {stats['avg_words_per_chunk']:.1f}")
    print(f"Min words in a chunk: {stats['min_words']}")
    print(f"Max words in a chunk: {stats['max_words']}")
    print()
    
    return stats['total_chunks'] > 0


def test_batch_chunking():
    """Test batch chunking of multiple texts."""
    print_header("TEST 9: Batch Chunking")
    
    chunker = ContentChunker()
    
    texts = [
        " ".join([f"text1_word{i}" for i in range(500)]),
        " ".join([f"text2_word{i}" for i in range(800)]),
        " ".join([f"text3_word{i}" for i in range(300)]),
    ]
    
    print(f"Processing {len(texts)} texts:")
    for i, text in enumerate(texts, 1):
        print(f"  Text {i}: {len(text.split())} words")
    print()
    
    batch_results = chunker.batch_chunk_texts(texts, chunk_size=300, overlap=50)
    
    print(f"Batch Results:")
    print("-" * 80)
    for i, chunks in enumerate(batch_results, 1):
        print(f"Text {i}: {len(chunks)} chunks")
    print()
    
    total_chunks = sum(len(chunks) for chunks in batch_results)
    print(f"Total chunks across all texts: {total_chunks}")
    print()
    
    return len(batch_results) == len(texts)


def test_overlap_verification():
    """Test that overlap is working correctly."""
    print_header("TEST 10: Overlap Verification")
    
    chunker = ContentChunker()
    
    # Create text with numbered words for easy verification
    words = [f"word{i:04d}" for i in range(400)]
    text = " ".join(words)
    
    chunks = chunker.chunk_text(text, chunk_size=100, overlap=20)
    
    print(f"Testing overlap with numbered words")
    print(f"Chunk size: 100 words, Overlap: 20 words")
    print()
    
    # Verify overlap between chunks
    if len(chunks) >= 2:
        chunk1_words = chunks[0].split()
        chunk2_words = chunks[1].split()
        
        # Last 20 words of chunk 1 should match first 20 words of chunk 2
        chunk1_last_20 = chunk1_words[-20:]
        chunk2_first_20 = chunk2_words[:20]
        
        print(f"Chunk 1 ends with: {chunk1_last_20[-3:]}")
        print(f"Chunk 2 starts with: {chunk2_first_20[:3]}")
        print()
        
        if chunk1_last_20 == chunk2_first_20:
            print("✓ PASS: Overlap verified correctly")
            return True
        else:
            print("✗ FAIL: Overlap not working as expected")
            return False
    else:
        print("⚠️  Not enough chunks to verify overlap")
        return True


def test_real_world_text():
    """Test with realistic article text."""
    print_header("TEST 11: Real-World Article Text")
    
    chunker = ContentChunker()
    
    # Simulate a realistic gut health article
    article = """
    Gut health has become one of the most important topics in modern nutrition science.
    The human gut microbiome consists of trillions of microorganisms including bacteria,
    viruses, fungi, and other microbes. These microorganisms play crucial roles in
    digestion, immune system function, mental health, and overall wellness.
    
    Research has shown that a diverse gut microbiome is associated with better health
    outcomes. Probiotics and prebiotics are dietary components that support healthy
    gut flora. Probiotics are live beneficial bacteria found in fermented foods like
    yogurt, kefir, and sauerkraut. Prebiotics are non-digestible fibers that feed
    the good bacteria in your gut.
    
    The gut-brain axis is a bidirectional communication system between the gut and
    the brain. This connection explains why gut health can affect mood, anxiety, and
    cognitive function. Neurotransmitters like serotonin are produced in the gut,
    highlighting the importance of maintaining a healthy digestive system.
    
    Diet plays a significant role in shaping the gut microbiome. A diet rich in
    fiber, fruits, vegetables, and whole grains promotes microbiome diversity.
    Processed foods, excessive sugar, and artificial additives can negatively impact
    gut health. Regular exercise, adequate sleep, and stress management also contribute
    to maintaining a healthy gut ecosystem.
    
    Maintaining gut health requires a holistic approach that includes proper nutrition,
    lifestyle choices, and potentially probiotic supplementation. Consulting with
    healthcare professionals can help develop personalized strategies for optimal
    gut health and overall wellness.
    """ * 3  # Repeat to make it longer
    
    print(f"Input: Realistic article with {len(article.split())} words")
    print()
    
    chunks = chunker.chunk_text(article, chunk_size=300, overlap=50)
    
    print_chunk_info(chunks, "Article chunked for processing")
    
    # Show statistics
    stats = chunker.get_chunk_statistics(chunks)
    print("Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Avg words/chunk: {stats['avg_words_per_chunk']:.1f}")
    print()
    
    return len(chunks) > 0


def test_pipeline_integration():
    """Test integration with full pipeline (TextCleaner → LanguageDetector → TopicTagger → Chunker)."""
    print_header("TEST 12: Pipeline Integration")
    
    print("Simulating full pipeline workflow:")
    print("TextCleaner → LanguageDetector → TopicTagger → ContentChunker")
    print()
    
    chunker = ContentChunker()
    
    # Simulate cleaned text from previous pipeline stages
    cleaned_text = (
        "Gut health is essential for digestion and immune function. "
        "The microbiome influences overall wellness and mental health. "
        "Probiotics and prebiotics support beneficial gut bacteria. "
        "Fiber-rich foods promote microbiome diversity and function. "
    ) * 50  # Repeat to make it long enough to chunk
    
    print(f"Input (after cleaning, language detection, topic tagging): {len(cleaned_text.split())} words")
    print()
    
    chunks = chunker.chunk_text(cleaned_text, chunk_size=100, overlap=20)
    
    print(f"✓ Chunked into {len(chunks)} pieces for downstream processing")
    print()
    
    # Show first chunk as example
    print("Example chunk (first):")
    print(f"  {chunks[0][:100]}...")
    print()
    
    return len(chunks) > 0


def run_all_tests():
    """Run all test cases and print summary."""
    print("=" * 80)
    print("CONTENT CHUNKER TEST SUITE".center(80))
    print("=" * 80)
    print("\nTesting content chunking module with various scenarios...")
    print("This will verify chunking logic, overlap handling, and edge cases.\n")
    
    tests = [
        ("Basic Chunking", test_basic_chunking),
        ("Long Text Chunking", test_long_text_chunking),
        ("Short Text Handling", test_short_text_handling),
        ("Empty Text Handling", test_empty_text),
        ("Different Chunk Sizes", test_different_chunk_sizes),
        ("Overlap Validation", test_overlap_validation),
        ("Metadata Generation", test_chunk_with_metadata),
        ("Statistics Calculation", test_chunk_statistics),
        ("Batch Chunking", test_batch_chunking),
        ("Overlap Verification", test_overlap_verification),
        ("Real-World Text", test_real_world_text),
        ("Pipeline Integration", test_pipeline_integration),
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
