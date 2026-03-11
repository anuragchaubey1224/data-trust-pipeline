"""
Language Detection Module for Data Trust Pipeline

This module provides language detection functionality for cleaned text content.
It identifies the language of text using the langdetect library and returns
ISO language codes.

"""

import logging
from typing import Optional

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect library not installed. Install with: pip install langdetect")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LanguageDetector:
    """
    A language detection utility for identifying the language of text content.
    
    This class uses the langdetect library to identify languages and return
    ISO 639-1 language codes (e.g., 'en' for English, 'es' for Spanish).
    
    Usage:
        >>> detector = LanguageDetector()
        >>> language = detector.detect_language("Hello world")
        >>> print(language)
        'en'
    
    Attributes:
        logger: Logger instance for tracking detection operations.
        min_text_length: Minimum text length for reliable detection (default: 20).
    """
    
    def __init__(self, min_text_length: int = 20):
        """
        Initialize the LanguageDetector.
        
        Args:
            min_text_length: Minimum number of characters required for detection.
                           Texts shorter than this return "unknown". Default: 20.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.min_text_length = min_text_length
        
        if not LANGDETECT_AVAILABLE:
            self.logger.error("langdetect library not available. Language detection will not work.")
            self.logger.info("Install with: pip install langdetect")
        else:
            self.logger.info("LanguageDetector initialized (min_text_length=%d)", min_text_length)
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Returns ISO 639-1 language codes such as:
        - 'en': English
        - 'es': Spanish
        - 'fr': French
        - 'de': German
        - 'hi': Hindi
        - 'zh-cn': Chinese (Simplified)
        - 'ja': Japanese
        - etc.
        
        Args:
            text: Text string to detect language from.
        
        Returns:
            ISO 639-1 language code (e.g., 'en', 'es', 'fr') or 'unknown'
            if detection fails or text is too short.
        
        Examples:
            >>> detector = LanguageDetector()
            >>> detector.detect_language("Gut health is essential for digestion.")
            'en'
            
            >>> detector.detect_language("La salud intestinal es importante.")
            'es'
            
            >>> detector.detect_language("hi")
            'unknown'
        """
        # Check if langdetect is available
        if not LANGDETECT_AVAILABLE:
            self.logger.error("langdetect library not available")
            return "unknown"
        
        # Validate input
        if text is None:
            self.logger.warning("Input text is None")
            return "unknown"
        
        if not isinstance(text, str):
            self.logger.warning(f"Converting non-string input to string: {type(text)}")
            text = str(text)
        
        # Remove extra whitespace
        text = text.strip()
        
        # Check if text is empty
        if not text:
            self.logger.warning("Input text is empty")
            return "unknown"
        
        # Check minimum length
        if len(text) < self.min_text_length:
            self.logger.warning(
                "Text too short for reliable detection (length=%d, min=%d)",
                len(text), self.min_text_length
            )
            return "unknown"
        
        # Detect language
        try:
            self.logger.info("Detecting language (text length: %d chars)", len(text))
            language_code = detect(text)
            self.logger.info("Language detected: %s", language_code)
            return language_code
        
        except LangDetectException as e:
            self.logger.error("Language detection failed (LangDetectException): %s", str(e))
            return "unknown"
        
        except Exception as e:
            self.logger.error("Unexpected error during language detection: %s", str(e))
            return "unknown"
    
    def detect_with_confidence(self, text: str) -> dict:
        """
        Detect language and return result with confidence information.
        
        This method provides additional metadata about the detection process,
        including whether the text met minimum length requirements.
        
        Args:
            text: Text string to detect language from.
        
        Returns:
            Dictionary containing:
            - 'language': detected language code or 'unknown'
            - 'reliable': boolean indicating if detection is reliable
            - 'text_length': length of input text
            - 'reason': explanation if language is 'unknown'
        
        Example:
            >>> detector = LanguageDetector()
            >>> result = detector.detect_with_confidence("Hello world, this is a test")
            >>> print(result)
            {
                'language': 'en',
                'reliable': True,
                'text_length': 28,
                'reason': None
            }
        """
        result = {
            'language': 'unknown',
            'reliable': False,
            'text_length': len(text) if text else 0,
            'reason': None
        }
        
        if not text or not text.strip():
            result['reason'] = 'empty_text'
            return result
        
        text = text.strip()
        result['text_length'] = len(text)
        
        if len(text) < self.min_text_length:
            result['reason'] = 'text_too_short'
            return result
        
        if not LANGDETECT_AVAILABLE:
            result['reason'] = 'langdetect_not_installed'
            return result
        
        try:
            language_code = detect(text)
            result['language'] = language_code
            result['reliable'] = True
            result['reason'] = None
        except LangDetectException:
            result['reason'] = 'detection_failed'
        except Exception as e:
            result['reason'] = f'error: {str(e)}'
        
        return result
    
    def detect_batch(self, texts: list[str]) -> list[str]:
        """
        Detect languages for multiple texts.
        
        Convenience method for processing multiple texts efficiently.
        
        Args:
            texts: List of text strings to detect languages from.
        
        Returns:
            List of language codes corresponding to each input text.
        
        Example:
            >>> detector = LanguageDetector()
            >>> texts = ["Hello world", "Bonjour le monde", "Hola mundo"]
            >>> languages = detector.detect_batch(texts)
            >>> print(languages)
            ['en', 'fr', 'es']
        """
        self.logger.info(f"Detecting languages for batch of {len(texts)} texts")
        
        languages = []
        for i, text in enumerate(texts):
            try:
                language = self.detect_language(text)
                languages.append(language)
            except Exception as e:
                self.logger.error(f"Error detecting language for text {i}: {e}")
                languages.append("unknown")
        
        return languages
    
    def is_language(self, text: str, expected_language: str) -> bool:
        """
        Check if text is in the expected language.
        
        Args:
            text: Text string to check.
            expected_language: Expected ISO language code (e.g., 'en', 'es').
        
        Returns:
            True if detected language matches expected language, False otherwise.
        
        Example:
            >>> detector = LanguageDetector()
            >>> detector.is_language("Hello world", "en")
            True
            >>> detector.is_language("Hello world", "es")
            False
        """
        detected = self.detect_language(text)
        return detected == expected_language.lower()
    
    def get_supported_languages(self) -> list[str]:
        """
        Get list of commonly supported language codes.
        
        Note: langdetect supports 55+ languages. This returns the most common ones.
        
        Returns:
            List of ISO 639-1 language codes.
        """
        return [
            'af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el',
            'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he', 'hi', 'hr',
            'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml',
            'mr', 'ne', 'nl', 'no', 'pa', 'pl', 'pt', 'ro', 'ru', 'sk',
            'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr',
            'uk', 'ur', 'vi', 'zh-cn', 'zh-tw'
        ]


if __name__ == "__main__":
    # Quick test
    detector = LanguageDetector()
    
    test_texts = [
        "Gut health is essential for digestion.",
        "La salud intestinal es importante.",
        "hi",
        "Bonjour, comment allez-vous?",
    ]
    
    print("Quick Language Detection Test\n" + "="*50)
    for text in test_texts:
        language = detector.detect_language(text)
        print(f"Text: {text[:40]}")
        print(f"Language: {language}\n")
