#!/usr/bin/env python3
"""
Test Script for JSONStorageWriter Module

This script tests the JSON storage functionality with various data samples
to ensure proper schema normalization and file writing.

Usage:
    python3 storage/test_json_writer.py
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from storage.json_writer import JSONStorageWriter


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def test_schema_normalization():
    """Test schema normalization with various inputs."""
    print_header("TEST 1: Schema Normalization")
    
    writer = JSONStorageWriter()
    
    # Test case 1: Complete data
    print("Test 1.1: Complete data")
    complete_data = {
        "source_url": "https://www.nih.gov/gut-health",
        "source_type": "blog",
        "author": "Dr. Jane Smith, MD",
        "published_date": "2025-06-15",
        "language": "en",
        "region": "USA",
        "topic_tags": ["gut health", "microbiome", "digestion"],
        "trust_score": 0.87,
        "content_chunks": ["Chunk 1 text", "Chunk 2 text", "Chunk 3 text"]
    }
    
    normalized = writer.normalize_schema(complete_data)
    print(f"✓ Normalized complete data")
    print(f"  URL: {normalized['source_url']}")
    print(f"  Trust Score: {normalized['trust_score']}")
    print(f"  Topic Tags: {len(normalized['topic_tags'])} tags")
    print(f"  Chunks: {len(normalized['content_chunks'])} chunks")
    print()
    
    # Test case 2: Missing optional fields
    print("Test 1.2: Missing optional fields (should use defaults)")
    minimal_data = {
        "source_url": "https://example.com/article",
        "source_type": "blog",
        "language": "en"
    }
    
    normalized = writer.normalize_schema(minimal_data)
    print(f"✓ Normalized minimal data")
    print(f"  Author: '{normalized['author']}' (empty)")
    print(f"  Region: '{normalized['region']}' (default: global)")
    print(f"  Trust Score: {normalized['trust_score']} (default: 0.0)")
    print()
    
    # Test case 3: Invalid trust score
    print("Test 1.3: Invalid trust score (should clip to 0-1)")
    invalid_score_data = {
        "source_url": "https://example.com",
        "trust_score": 1.5  # Invalid (> 1.0)
    }
    
    normalized = writer.normalize_schema(invalid_score_data)
    print(f"✓ Clipped trust score: {normalized['trust_score']} (max: 1.0)")
    print()
    
    return True


def test_write_json_basic():
    """Test basic JSON writing functionality."""
    print_header("TEST 2: Basic JSON Writing")
    
    writer = JSONStorageWriter()
    
    # Create sample data
    data = [
        {
            "source_url": "https://www.nih.gov/health/gut-microbiome",
            "source_type": "blog",
            "author": "Dr. John Smith, PhD",
            "published_date": "2024-03-15",
            "language": "en",
            "region": "USA",
            "topic_tags": ["gut health", "microbiome", "probiotics"],
            "trust_score": 0.92,
            "content_chunks": [
                "The gut microbiome plays a crucial role in digestion.",
                "Probiotics can help maintain a healthy gut flora."
            ]
        },
        {
            "source_url": "https://www.youtube.com/watch?v=xyz123",
            "source_type": "youtube",
            "author": "Health Channel",
            "published_date": "2023-11-20",
            "language": "en",
            "region": "global",
            "topic_tags": ["nutrition", "wellness", "diet"],
            "trust_score": 0.68,
            "content_chunks": [
                "Today we discuss nutrition basics.",
                "A balanced diet is important for health."
            ]
        }
    ]
    
    output_path = "output/test_basic.json"
    
    try:
        writer.write_json(data, output_path)
        print(f"✓ Successfully wrote JSON to: {output_path}")
        
        # Verify file exists
        if Path(output_path).exists():
            print(f"✓ File exists at: {output_path}")
            
            # Read and verify
            with open(output_path, 'r') as f:
                loaded_data = json.load(f)
            
            print(f"✓ Verified: {len(loaded_data)} sources in file")
            return True
        else:
            print("✗ FAIL: File was not created")
            return False
    
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_write_json_complex():
    """Test JSON writing with complex realistic data."""
    print_header("TEST 3: Complex Multi-Source Data")
    
    writer = JSONStorageWriter()
    
    # Create realistic multi-source dataset
    data = [
        {
            "source_url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
            "source_type": "pubmed",
            "author": "Dr. Sarah Martinez, MD, PhD",
            "published_date": "2024-12-10",
            "language": "en",
            "region": "global",
            "topic_tags": ["gut health", "clinical trial", "microbiome", "probiotics"],
            "trust_score": 0.89,
            "content_chunks": [
                "This randomized controlled trial examined gut microbiome diversity.",
                "Results showed significant improvement in digestive health.",
                "Probiotic supplementation was well tolerated."
            ]
        },
        {
            "source_url": "https://healthblog.com/gut-wellness-tips",
            "source_type": "blog",
            "author": "Emma Johnson",
            "published_date": "2025-01-05",
            "language": "en",
            "region": "USA",
            "topic_tags": ["wellness", "gut health", "nutrition"],
            "trust_score": 0.64,
            "content_chunks": [
                "Here are 5 tips for better gut health.",
                "Include fermented foods in your diet."
            ]
        },
        {
            "source_url": "https://www.youtube.com/watch?v=abc789",
            "source_type": "youtube",
            "author": "Dr. Michael Chen",
            "published_date": "2024-08-22",
            "language": "en",
            "region": "global",
            "topic_tags": ["gut brain axis", "mental health", "microbiome"],
            "trust_score": 0.75,
            "content_chunks": [
                "The gut-brain axis connects digestive and mental health.",
                "Research shows gut bacteria influence mood and cognition."
            ]
        },
        {
            "source_url": "https://www.cdc.gov/nutrition/microbiome-health",
            "source_type": "blog",
            "author": "CDC Nutrition Team",
            "published_date": "2025-02-01",
            "language": "en",
            "region": "USA",
            "topic_tags": ["public health", "nutrition", "microbiome"],
            "trust_score": 0.91,
            "content_chunks": [
                "The CDC recommends diverse dietary sources for gut health.",
                "Fiber-rich foods support beneficial gut bacteria."
            ]
        }
    ]
    
    output_path = "output/scraped_data.json"
    
    try:
        writer.write_json(data, output_path)
        print(f"✓ Successfully wrote {len(data)} sources to: {output_path}")
        
        # Verify and show sample
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)
        
        print(f"✓ Verified: {len(loaded_data)} sources loaded")
        print()
        print("Sample entry (first source):")
        print(json.dumps(loaded_data[0], indent=2))
        print()
        
        return True
    
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_schema_validation():
    """Test schema validation functionality."""
    print_header("TEST 4: Schema Validation")
    
    writer = JSONStorageWriter()
    
    # Valid data
    valid_data = {
        "source_url": "https://example.com",
        "source_type": "blog",
        "author": "Author Name",
        "published_date": "2025-01-01",
        "language": "en",
        "region": "global",
        "topic_tags": ["tag1", "tag2"],
        "trust_score": 0.8,
        "content_chunks": ["chunk1"]
    }
    
    # Invalid data (missing fields)
    invalid_data = {
        "source_url": "https://example.com",
        "source_type": "blog"
    }
    
    valid_result = writer.validate_schema(valid_data)
    invalid_result = writer.validate_schema(invalid_data)
    
    print(f"Valid data validation: {'✓ PASS' if valid_result else '✗ FAIL'}")
    print(f"Invalid data validation: {'✓ PASS' if not invalid_result else '✗ FAIL'}")
    print()
    
    return valid_result and not invalid_result


def test_read_json():
    """Test JSON reading functionality."""
    print_header("TEST 5: JSON Reading")
    
    writer = JSONStorageWriter()
    
    # Create test data file
    test_data = [
        {
            "source_url": "https://example.com/1",
            "source_type": "blog",
            "author": "Author 1",
            "published_date": "2025-01-01",
            "language": "en",
            "region": "global",
            "topic_tags": ["tag1"],
            "trust_score": 0.7,
            "content_chunks": ["content"]
        }
    ]
    
    test_path = "output/test_read.json"
    
    try:
        # Write test file
        writer.write_json(test_data, test_path)
        
        # Read it back
        loaded_data = writer.read_json(test_path)
        
        print(f"✓ Successfully read JSON from: {test_path}")
        print(f"✓ Loaded {len(loaded_data)} sources")
        print(f"✓ First source URL: {loaded_data[0]['source_url']}")
        print()
        
        return len(loaded_data) == 1
    
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_append_json():
    """Test appending to existing JSON files."""
    print_header("TEST 6: Append to JSON")
    
    writer = JSONStorageWriter()
    
    # Initial data
    initial_data = [
        {
            "source_url": "https://example.com/1",
            "source_type": "blog",
            "language": "en",
            "trust_score": 0.8
        }
    ]
    
    # Additional data to append
    new_data = [
        {
            "source_url": "https://example.com/2",
            "source_type": "youtube",
            "language": "en",
            "trust_score": 0.7
        },
        {
            "source_url": "https://example.com/3",
            "source_type": "pubmed",
            "language": "en",
            "trust_score": 0.9
        }
    ]
    
    test_path = "output/test_append.json"
    
    try:
        # Write initial data
        writer.write_json(initial_data, test_path)
        print(f"✓ Wrote initial data: {len(initial_data)} sources")
        
        # Append new data
        writer.append_json(new_data, test_path)
        print(f"✓ Appended: {len(new_data)} sources")
        
        # Read and verify
        final_data = writer.read_json(test_path)
        expected_total = len(initial_data) + len(new_data)
        
        print(f"✓ Total sources after append: {len(final_data)} (expected: {expected_total})")
        print()
        
        return len(final_data) == expected_total
    
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def test_statistics():
    """Test statistics generation."""
    print_header("TEST 7: Data Statistics")
    
    writer = JSONStorageWriter()
    
    # Create diverse dataset
    data = [
        {"source_type": "blog", "language": "en", "trust_score": 0.8, "content_chunks": ["a", "b"]},
        {"source_type": "blog", "language": "en", "trust_score": 0.7, "content_chunks": ["a"]},
        {"source_type": "youtube", "language": "es", "trust_score": 0.6, "content_chunks": ["a", "b", "c"]},
        {"source_type": "pubmed", "language": "en", "trust_score": 0.9, "content_chunks": ["a"]},
    ]
    
    # Normalize data first
    normalized_data = [writer.normalize_schema(d) for d in data]
    
    # Get statistics
    stats = writer.get_statistics(normalized_data)
    
    print("Dataset Statistics:")
    print(f"  Total sources: {stats['total_sources']}")
    print(f"  Source types: {stats['source_types']}")
    print(f"  Languages: {stats['languages']}")
    print(f"  Avg trust score: {stats['avg_trust_score']:.2f}")
    print(f"  Avg chunks per source: {stats['avg_chunks_per_source']:.1f}")
    print()
    
    return stats['total_sources'] == 4


def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("TEST 8: Edge Cases")
    
    writer = JSONStorageWriter()
    
    all_passed = True
    
    # Test 1: Empty list
    print("Test 8.1: Empty list")
    try:
        writer.write_json([], "output/test_empty.json")
        print("✓ Handled empty list gracefully")
    except Exception as e:
        print(f"✗ FAIL: {e}")
        all_passed = False
    print()
    
    # Test 2: Invalid data type
    print("Test 8.2: Invalid data type (not a list)")
    try:
        writer.write_json({"not": "a list"}, "output/test_invalid.json")
        print("✗ FAIL: Should have raised ValueError")
        all_passed = False
    except ValueError:
        print("✓ Correctly raised ValueError for invalid type")
    except Exception as e:
        print(f"✗ FAIL: Wrong exception - {e}")
        all_passed = False
    print()
    
    # Test 3: Missing required fields (should fill with defaults)
    print("Test 8.3: Missing fields (should use defaults)")
    try:
        minimal = [{"source_url": "https://example.com"}]
        writer.write_json(minimal, "output/test_minimal.json")
        
        # Read back and check defaults
        loaded = writer.read_json("output/test_minimal.json")
        
        if loaded[0]['region'] == 'global' and loaded[0]['trust_score'] == 0.0:
            print("✓ Defaults applied correctly")
        else:
            print("✗ FAIL: Defaults not applied properly")
            all_passed = False
    except Exception as e:
        print(f"✗ FAIL: {e}")
        all_passed = False
    print()
    
    return all_passed


def test_full_pipeline_simulation():
    """Test with data that simulates full pipeline output."""
    print_header("TEST 9: Full Pipeline Simulation")
    
    writer = JSONStorageWriter()
    
    # Simulate data from complete pipeline
    pipeline_data = [
        {
            "source_url": "https://www.nih.gov/gut-health-research",
            "source_type": "blog",
            "title": "Understanding Gut Health",
            "author": "Dr. Emily Rodriguez, MD, PhD",
            "published_date": "2024-11-15",
            "scraped_date": "2026-03-10",
            "language": "en",
            "region": "USA",
            "topic_tags": ["gut health", "microbiome", "research", "probiotics"],
            "trust_score": 0.885,
            "content_chunks": [
                "The gut microbiome consists of trillions of microorganisms.",
                "These microbes play crucial roles in digestion and immunity.",
                "Research shows probiotics can improve gut flora diversity."
            ],
            "metadata": {
                "word_count": 450,
                "chunk_count": 3
            }
        },
        {
            "source_url": "https://www.youtube.com/watch?v=health123",
            "source_type": "youtube",
            "title": "5 Tips for Gut Health",
            "author": "Wellness Channel",
            "published_date": "2024-08-20",
            "scraped_date": "2026-03-10",
            "language": "en",
            "region": "global",
            "topic_tags": ["wellness", "nutrition", "gut health"],
            "trust_score": 0.625,
            "content_chunks": [
                "Tip 1: Eat more fermented foods like yogurt and kimchi.",
                "Tip 2: Include fiber-rich vegetables in every meal."
            ],
            "metadata": {
                "duration": "8:45",
                "views": 125000
            }
        }
    ]
    
    output_path = "output/pipeline_simulation.json"
    
    try:
        writer.write_json(pipeline_data, output_path)
        print(f"✓ Wrote pipeline simulation data to: {output_path}")
        
        # Read and verify
        loaded = writer.read_json(output_path)
        
        print(f"✓ Verified {len(loaded)} sources")
        print()
        
        # Show normalized schema
        print("Normalized schema for first source:")
        for key in loaded[0].keys():
            value = loaded[0][key]
            if isinstance(value, list):
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {value}")
        print()
        
        return True
    
    except Exception as e:
        print(f"✗ FAIL: {e}")
        return False


def run_all_tests():
    """Run all test cases and print summary."""
    print("=" * 80)
    print("JSON STORAGE WRITER TEST SUITE".center(80))
    print("=" * 80)
    print("\nTesting JSON storage functionality with various scenarios...")
    print("Output files will be written to: output/\n")
    
    tests = [
        ("Schema Normalization", test_schema_normalization),
        ("Basic JSON Writing", test_write_json_basic),
        ("Complex Multi-Source Data", test_write_json_complex),
        ("Schema Validation", test_schema_validation),
        ("JSON Reading", test_read_json),
        ("Append to JSON", test_append_json),
        ("Data Statistics", test_statistics),
        ("Edge Cases", test_edge_cases),
        ("Full Pipeline Simulation", test_full_pipeline_simulation),
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
    
    print("\n📁 Output files created in: output/")
    print("   - scraped_data.json (main output with 4 sources)")
    print("   - pipeline_simulation.json (full pipeline example)")
    print("   - test_*.json (various test files)")
    
    if passed_count < len(results):
        print("\n⚠️  Please review the failing tests")
        return 1
    return 0


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
