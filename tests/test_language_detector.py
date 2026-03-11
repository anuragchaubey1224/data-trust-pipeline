#!/usr/bin/env python3
"""
Test Script for LanguageDetector Module

This script tests the language detection functionality with various text samples
in different languages to ensure proper identification of language codes.

Usage:
    python3 processing/test_language_detector.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from processing.language_detector import LanguageDetector


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80 + "\n")


def print_test_result(test_name: str, text: str, expected: str, detected: str):
    """Print formatted test results."""
    status = "✓ PASS" if detected == expected or expected == "any" else "✗ FAIL"
    print(f"{status} {test_name}")
    print(f"  Text: {text[:60]}..." if len(text) > 60 else f"  Text: {text}")
    print(f"  Detected: {detected}")
    if expected != "any":
        print(f"  Expected: {expected}")
    print()


def test_english_detection():
    """Test English language detection."""
    print_header("TEST 1: English Language Detection")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("Gut health is essential for digestion.", "en"),
        ("Machine learning is transforming technology.", "en"),
        ("The quick brown fox jumps over the lazy dog.", "en"),
        ("Data science combines statistics and programming.", "en"),
    ]
    
    all_passed = True
    for text, expected in test_cases:
        detected = detector.detect_language(text)
        passed = detected == expected
        print_test_result("English Text", text, expected, detected)
        if not passed:
            all_passed = False
    
    return all_passed


def test_spanish_detection():
    """Test Spanish language detection."""
    print_header("TEST 2: Spanish Language Detection")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("La salud intestinal es importante.", "es"),
        ("El aprendizaje automático es fascinante.", "es"),
        ("Hola, ¿cómo estás hoy?", "es"),
        ("La ciencia de datos es muy interesante.", "es"),
    ]
    
    all_passed = True
    for text, expected in test_cases:
        detected = detector.detect_language(text)
        passed = detected == expected
        print_test_result("Spanish Text", text, expected, detected)
        if not passed:
            all_passed = False
    
    return all_passed


def test_multilingual_detection():
    """Test detection of various languages."""
    print_header("TEST 3: Multiple Languages Detection")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("Bonjour, comment allez-vous?", "fr", "French"),
        ("Guten Tag, wie geht es Ihnen?", "de", "German"),
        ("आंत स्वास्थ्य पाचन के लिए महत्वपूर्ण है।", "hi", "Hindi"),
        ("Ciao, come stai? Tutto bene oggi?", "it", "Italian"),
        ("Olá, como você está?", "pt", "Portuguese"),
        ("Здравствуйте, как дела?", "ru", "Russian"),
        ("こんにちは、お元気ですか？今日はいい天気ですね。", "ja", "Japanese"),
        ("你好，你好吗？今天天气很好。我很高兴认识你。", "zh-cn", "Chinese"),
    ]
    
    all_passed = True
    for text, expected, name in test_cases:
        detected = detector.detect_language(text)
        passed = detected == expected
        print(f"{'✓' if passed else '✗'} {name}")
        print(f"  Text: {text}")
        print(f"  Detected: {detected} (Expected: {expected})")
        print()
        if not passed:
            all_passed = False
    
    return all_passed


def test_short_text_handling():
    """Test handling of short text that's too short for detection."""
    print_header("TEST 4: Short Text Handling")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("hi", "Short greeting"),
        ("ok", "Very short"),
        ("a", "Single character"),
        ("", "Empty string"),
        ("   ", "Whitespace only"),
    ]
    
    all_passed = True
    for text, description in test_cases:
        detected = detector.detect_language(text)
        passed = detected == "unknown"
        print(f"{'✓' if passed else '✗'} {description}")
        print(f"  Text: '{text}'")
        print(f"  Detected: {detected} (Expected: unknown)")
        print()
        if not passed:
            all_passed = False
    
    return all_passed


def test_edge_cases():
    """Test edge cases and error handling."""
    print_header("TEST 5: Edge Cases")
    
    detector = LanguageDetector()
    
    print("Testing None input...")
    try:
        result = detector.detect_language(None)
        if result == "unknown":
            print("✓ None input handled: returns 'unknown'\n")
            none_passed = True
        else:
            print(f"✗ None input: Expected 'unknown', got '{result}'\n")
            none_passed = False
    except Exception as e:
        print(f"✗ None input: Raised exception - {e}\n")
        none_passed = False
    
    print("Testing numeric input...")
    try:
        result = detector.detect_language(12345)
        if result == "unknown":
            print("✓ Numeric input handled: returns 'unknown'\n")
            numeric_passed = True
        else:
            print(f"✗ Numeric input: Expected 'unknown', got '{result}'\n")
            numeric_passed = False
    except Exception as e:
        print(f"✗ Numeric input: Raised exception - {e}\n")
        numeric_passed = False
    
    print("Testing special characters...")
    special_text = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
    result = detector.detect_language(special_text)
    special_passed = result == "unknown"
    print(f"{'✓' if special_passed else '✗'} Special characters: {result}\n")
    
    return none_passed and numeric_passed and special_passed


def test_confidence_detection():
    """Test detection with confidence information."""
    print_header("TEST 6: Detection with Confidence")
    
    detector = LanguageDetector()
    
    test_cases = [
        ("This is a long enough text for reliable detection", True),
        ("short", False),
        ("", False),
    ]
    
    all_passed = True
    for text, should_be_reliable in test_cases:
        result = detector.detect_with_confidence(text)
        passed = result['reliable'] == should_be_reliable
        
        print(f"{'✓' if passed else '✗'} Text: '{text[:40]}...' " if len(text) > 40 else f"{'✓' if passed else '✗'} Text: '{text}'")
        print(f"  Language: {result['language']}")
        print(f"  Reliable: {result['reliable']} (Expected: {should_be_reliable})")
        print(f"  Text Length: {result['text_length']}")
        if result['reason']:
            print(f"  Reason: {result['reason']}")
        print()
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_batch_detection():
    """Test batch language detection."""
    print_header("TEST 7: Batch Detection")
    
    detector = LanguageDetector()
    
    texts = [
        "Hello, this is an English sentence.",
        "Bonjour, ceci est une phrase française.",
        "Hola, esta es una oración en español.",
        "hi",  # Too short
    ]
    
    expected = ["en", "fr", "es", "unknown"]
    
    print(f"Detecting languages for {len(texts)} texts...\n")
    detected = detector.detect_batch(texts)
    
    all_passed = True
    for i, (text, exp, det) in enumerate(zip(texts, expected, detected), 1):
        passed = det == exp
        print(f"{'✓' if passed else '✗'} Text {i}: {text[:40]}...")
        print(f"  Detected: {det} (Expected: {exp})")
        print()
        if not passed:
            all_passed = False
    
    return all_passed


def test_is_language():
    """Test language checking functionality."""
    print_header("TEST 8: Language Checking")
    
    detector = LanguageDetector()
    
    print("Testing is_language() method...\n")
    
    # Test English
    text = "This is definitely an English sentence with enough words."
    is_en = detector.is_language(text, "en")
    is_es = detector.is_language(text, "es")
    
    print(f"Text: {text}")
    print(f"  Is English? {is_en} (Expected: True)")
    print(f"  Is Spanish? {is_es} (Expected: False)")
    print()
    
    return is_en and not is_es


def test_integration_with_cleaned_text():
    """Test with text that has been cleaned (simulating pipeline)."""
    print_header("TEST 9: Integration with Cleaned Text")
    
    detector = LanguageDetector()
    
    # Simulate text that went through TextCleaner
    cleaned_texts = [
        "Machine learning enables computers to learn from data without explicit programming.",
        "El aprendizaje automático permite a las computadoras aprender de los datos.",
        "L'apprentissage automatique permet aux ordinateurs d'apprendre à partir de données.",
    ]
    
    expected = ["en", "es", "fr"]
    
    print("Testing cleaned text from pipeline...\n")
    
    all_passed = True
    for text, exp in zip(cleaned_texts, expected):
        detected = detector.detect_language(text)
        passed = detected == exp
        
        print(f"{'✓' if passed else '✗'} Detected: {detected} (Expected: {exp})")
        print(f"  Text: {text[:60]}...")
        print()
        
        if not passed:
            all_passed = False
    
    return all_passed


def run_all_tests():
    """Run all test cases and display summary."""
    print_header("LANGUAGE DETECTOR TEST SUITE")
    
    print("Testing language detection module with various scenarios...")
    print("This will verify detection of multiple languages and edge cases.\n")
    
    # Run all tests
    test_results = {
        "English Detection": test_english_detection(),
        "Spanish Detection": test_spanish_detection(),
        "Multiple Languages": test_multilingual_detection(),
        "Short Text Handling": test_short_text_handling(),
        "Edge Cases": test_edge_cases(),
        "Confidence Detection": test_confidence_detection(),
        "Batch Detection": test_batch_detection(),
        "Language Checking": test_is_language(),
        "Integration Test": test_integration_with_cleaned_text(),
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
        print("\n🎉 LanguageDetector is working correctly!")
        print("\nNext steps:")
        print("  1. Integrate with text cleaning pipeline")
        print("  2. Add language-based content filtering")
        print("  3. Implement topic tagging module")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*80)
        print("\n⚠️  Please review the failing tests")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
