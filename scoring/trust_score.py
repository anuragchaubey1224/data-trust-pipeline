"""
Trust Score System for Data Trust Pipeline

This module provides trust scoring functionality for evaluating the credibility
and reliability of content sources. It uses multiple credibility signals to
compute a weighted trust score between 0 and 1.

"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class TrustScoreCalculator:
    """
    A trust scoring utility for evaluating content source credibility.
    
    This class calculates a trust score based on five credibility factors:
    1. Author credibility (25%)
    2. Citation count (20%)
    3. Domain authority (20%)
    4. Recency (20%)
    5. Medical disclaimer presence (15%)
    
    The final trust score is normalized between 0 and 1.
    
    Usage:
        >>> calculator = TrustScoreCalculator()
        >>> data = {
        ...     "source_url": "https://www.nih.gov/article",
        ...     "author": "Dr. John Smith, MD",
        ...     "published_date": "2025-06-15",
        ...     "source_type": "pubmed",
        ...     "content": "Research study shows..."
        ... }
        >>> score = calculator.calculate_trust_score(data)
        >>> print(f"Trust Score: {score:.2f}")
        Trust Score: 0.85
    
    Attributes:
        logger: Logger instance for tracking scoring operations.
        weights: Dictionary of scoring weights for each factor.
        trusted_domains: List of highly trusted domains.
    """
    
    def __init__(self):
        """Initialize the TrustScoreCalculator with scoring weights and trusted domains."""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Scoring weights (must sum to 1.0)
        self.weights = {
            'author': 0.25,
            'citation': 0.20,
            'domain': 0.20,
            'recency': 0.20,
            'disclaimer': 0.15
        }
        
        # Trusted domains for domain authority scoring
        self.trusted_domains = [
            'nih.gov',
            'who.int',
            'cdc.gov',
            'mayoclinic.org',
            'healthline.com',
            'pubmed.ncbi.nlm.nih.gov',
            'ncbi.nlm.nih.gov',
            'nejm.org',  # New England Journal of Medicine
            'bmj.com',   # British Medical Journal
            'thelancet.com',
            'jamanetwork.com',
            'hopkinsmedicine.org',
            'clevelandclinic.org',
        ]
        
        # Expertise indicators for author credibility
        self.expertise_indicators = [
            'dr.', 'dr ', 'md', 'phd', 'ph.d', 'professor', 'prof.',
            'm.d.', 'rn', 'dvm', 'pharmd', 'mph', 'ms', 'msc'
        ]
        
        # Citation keywords
        self.citation_keywords = [
            'study', 'research', 'journal', 'clinical', 'trial',
            'published', 'peer-reviewed', 'evidence', 'findings',
            'analysis', 'data', 'scientific', 'randomized'
        ]
        
        # Medical disclaimer phrases
        self.disclaimer_phrases = [
            'consult your doctor',
            'consult a doctor',
            'medical advice',
            'healthcare professional',
            'not a substitute for medical advice',
            'seek medical advice',
            'talk to your doctor',
            'medical professional',
            'qualified healthcare',
            'professional medical advice'
        ]
        
        self.logger.info("TrustScoreCalculator initialized")
    
    def calculate_author_score(self, author: Optional[str]) -> float:
        """
        Calculate author credibility score based on credentials.
        
        Scoring logic:
        - 1.0: Author has expertise indicators (Dr, MD, PhD, Professor)
        - 0.7: Author exists but no expertise indicators
        - 0.3: No author or unknown
        
        Args:
            author: Author name/credentials string.
        
        Returns:
            Author credibility score between 0.3 and 1.0.
        
        Examples:
            >>> calculator = TrustScoreCalculator()
            >>> calculator.calculate_author_score("Dr. Jane Smith, MD")
            1.0
            
            >>> calculator.calculate_author_score("John Doe")
            0.7
            
            >>> calculator.calculate_author_score(None)
            0.3
        """
        if not author or author.lower() in ['unknown', 'anonymous', 'n/a', '']:
            self.logger.debug("No author information, score: 0.3")
            return 0.3
        
        # Check for expertise indicators
        author_lower = author.lower()
        has_expertise = any(indicator in author_lower for indicator in self.expertise_indicators)
        
        if has_expertise:
            self.logger.debug(f"Author '{author}' has expertise indicators, score: 1.0")
            return 1.0
        else:
            self.logger.debug(f"Author '{author}' exists but no expertise indicators, score: 0.7")
            return 0.7
    
    def calculate_citation_score(self, source_type: str, content: str) -> float:
        """
        Calculate citation quality score based on source type and content.
        
        Scoring logic:
        - PubMed articles: 0.9 (assumed strong citations)
        - Blogs/other: Based on citation keyword count
          - Many keywords: higher score (up to 0.9)
          - Few keywords: medium score (0.4-0.6)
          - No keywords: low score (0.3)
        
        Args:
            source_type: Type of source (e.g., 'pubmed', 'blog', 'youtube').
            content: Text content to analyze for citations.
        
        Returns:
            Citation quality score between 0.3 and 0.9.
        
        Examples:
            >>> calculator = TrustScoreCalculator()
            >>> calculator.calculate_citation_score("pubmed", "Any content")
            0.9
            
            >>> content = "Research study published in journal shows clinical trial evidence"
            >>> calculator.calculate_citation_score("blog", content)
            0.8  # or higher based on keyword count
        """
        # PubMed articles assumed to have strong citations
        if source_type and source_type.lower() == 'pubmed':
            self.logger.debug("PubMed source, citation score: 0.9")
            return 0.9
        
        if not content:
            self.logger.debug("No content provided, citation score: 0.3")
            return 0.3
        
        # Count citation keywords in content
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in self.citation_keywords if keyword in content_lower)
        
        # Score based on keyword frequency
        if keyword_count >= 5:
            score = 0.9
        elif keyword_count >= 3:
            score = 0.7
        elif keyword_count >= 1:
            score = 0.5
        else:
            score = 0.3
        
        self.logger.debug(f"Found {keyword_count} citation keywords, score: {score}")
        return score
    
    def calculate_domain_score(self, source_url: str) -> float:
        """
        Calculate domain authority score based on URL.
        
        Scoring logic:
        - Trusted domains (nih.gov, cdc.gov, etc.): 0.9
        - Educational domains (.edu): 0.85
        - Government domains (.gov): 0.85
        - Other domains: 0.5
        
        Args:
            source_url: Full URL of the source.
        
        Returns:
            Domain authority score between 0.5 and 0.9.
        
        Examples:
            >>> calculator = TrustScoreCalculator()
            >>> calculator.calculate_domain_score("https://www.nih.gov/article")
            0.9
            
            >>> calculator.calculate_domain_score("https://university.edu/research")
            0.85
            
            >>> calculator.calculate_domain_score("https://randomwebsite.com/blog")
            0.5
        """
        if not source_url:
            self.logger.debug("No URL provided, domain score: 0.5")
            return 0.5
        
        try:
            # Parse domain from URL
            parsed = urlparse(source_url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check if domain is in trusted list
            if any(trusted in domain for trusted in self.trusted_domains):
                self.logger.debug(f"Trusted domain '{domain}', score: 0.9")
                return 0.9
            
            # Check for educational domains
            if domain.endswith('.edu'):
                self.logger.debug(f"Educational domain '{domain}', score: 0.85")
                return 0.85
            
            # Check for government domains
            if domain.endswith('.gov'):
                self.logger.debug(f"Government domain '{domain}', score: 0.85")
                return 0.85
            
            # Default score for other domains
            self.logger.debug(f"Standard domain '{domain}', score: 0.5")
            return 0.5
            
        except Exception as e:
            self.logger.warning(f"Error parsing domain from URL '{source_url}': {e}")
            return 0.5
    
    def calculate_recency_score(self, published_date: Optional[str]) -> float:
        """
        Calculate recency score based on publication date.
        
        Scoring logic:
        - < 1 year: 1.0
        - 1-3 years: 0.8
        - 3-5 years: 0.6
        - 5-10 years: 0.4
        - > 10 years: 0.2
        - Missing date: 0.5 (neutral)
        
        Args:
            published_date: Publication date string in ISO format (YYYY-MM-DD)
                          or other parseable format.
        
        Returns:
            Recency score between 0.2 and 1.0.
        
        Examples:
            >>> calculator = TrustScoreCalculator()
            >>> calculator.calculate_recency_score("2025-06-15")
            1.0
            
            >>> calculator.calculate_recency_score("2020-01-01")
            0.6
            
            >>> calculator.calculate_recency_score(None)
            0.5
        """
        if not published_date:
            self.logger.debug("No publication date, recency score: 0.5")
            return 0.5
        
        try:
            # Try to parse the date
            # Support common formats
            date_formats = [
                '%Y-%m-%d',      # 2025-06-15
                '%Y/%m/%d',      # 2025/06/15
                '%d-%m-%Y',      # 15-06-2025
                '%d/%m/%Y',      # 15/06/2025
                '%B %d, %Y',     # June 15, 2025
                '%b %d, %Y',     # Jun 15, 2025
                '%Y',            # 2025
            ]
            
            pub_date = None
            for fmt in date_formats:
                try:
                    pub_date = datetime.strptime(str(published_date), fmt)
                    break
                except ValueError:
                    continue
            
            if pub_date is None:
                # Try extracting year if format not recognized
                year_match = re.search(r'\b(19|20)\d{2}\b', str(published_date))
                if year_match:
                    year = int(year_match.group(0))
                    pub_date = datetime(year, 1, 1)
                else:
                    self.logger.warning(f"Could not parse date '{published_date}', using neutral score")
                    return 0.5
            
            # Calculate years since publication
            current_date = datetime.now()
            years_ago = (current_date - pub_date).days / 365.25
            
            # Score based on age
            if years_ago < 1:
                score = 1.0
            elif years_ago < 3:
                score = 0.8
            elif years_ago < 5:
                score = 0.6
            elif years_ago < 10:
                score = 0.4
            else:
                score = 0.2
            
            self.logger.debug(f"Published {years_ago:.1f} years ago, recency score: {score}")
            return score
            
        except Exception as e:
            self.logger.warning(f"Error calculating recency for date '{published_date}': {e}")
            return 0.5
    
    def calculate_disclaimer_score(self, content: str) -> float:
        """
        Calculate medical disclaimer score based on content.
        
        Searches for medical disclaimer phrases indicating responsible
        health information sharing.
        
        Scoring logic:
        - Has medical disclaimer: 1.0
        - No disclaimer: 0.4
        
        Args:
            content: Text content to check for disclaimers.
        
        Returns:
            Disclaimer score (0.4 or 1.0).
        
        Examples:
            >>> calculator = TrustScoreCalculator()
            >>> content = "Always consult your doctor before making health decisions."
            >>> calculator.calculate_disclaimer_score(content)
            1.0
            
            >>> calculator.calculate_disclaimer_score("Just some health tips.")
            0.4
        """
        if not content:
            self.logger.debug("No content provided, disclaimer score: 0.4")
            return 0.4
        
        content_lower = content.lower()
        
        # Check for disclaimer phrases
        has_disclaimer = any(phrase in content_lower for phrase in self.disclaimer_phrases)
        
        if has_disclaimer:
            self.logger.debug("Medical disclaimer found, score: 1.0")
            return 1.0
        else:
            self.logger.debug("No medical disclaimer found, score: 0.4")
            return 0.4
    
    def calculate_trust_score(self, data: Dict) -> float:
        """
        Calculate overall trust score from content data.
        
        Combines all credibility factors using weighted scoring:
        - Author credibility: 25%
        - Citation quality: 20%
        - Domain authority: 20%
        - Recency: 20%
        - Medical disclaimer: 15%
        
        Args:
            data: Dictionary containing content metadata:
                - source_url: URL of the source
                - author: Author name/credentials
                - published_date: Publication date
                - source_type: Type of source (pubmed, blog, youtube)
                - content: Text content (or content_chunks list)
        
        Returns:
            Trust score between 0.0 and 1.0.
        
        Example:
            >>> calculator = TrustScoreCalculator()
            >>> data = {
            ...     "source_url": "https://www.nih.gov/article",
            ...     "author": "Dr. Smith, MD",
            ...     "published_date": "2025-06-15",
            ...     "source_type": "pubmed",
            ...     "content": "Research study with medical advice disclaimer"
            ... }
            >>> score = calculator.calculate_trust_score(data)
            >>> print(f"{score:.2f}")
            0.87
        """
        self.logger.info("Calculating trust score")
        
        # Extract fields from data
        source_url = data.get('source_url', '')
        author = data.get('author', '')
        published_date = data.get('published_date', '')
        source_type = data.get('source_type', '')
        
        # Get content - handle both single content and content_chunks
        content = data.get('content', '')
        if not content and 'content_chunks' in data:
            chunks = data.get('content_chunks', [])
            if isinstance(chunks, list):
                content = ' '.join(str(chunk) for chunk in chunks)
        
        # Calculate individual scores
        author_score = self.calculate_author_score(author)
        citation_score = self.calculate_citation_score(source_type, content)
        domain_score = self.calculate_domain_score(source_url)
        recency_score = self.calculate_recency_score(published_date)
        disclaimer_score = self.calculate_disclaimer_score(content)
        
        # Log individual scores
        self.logger.info(f"Author credibility score: {author_score:.2f}")
        self.logger.info(f"Citation quality score: {citation_score:.2f}")
        self.logger.info(f"Domain authority score: {domain_score:.2f}")
        self.logger.info(f"Recency score: {recency_score:.2f}")
        self.logger.info(f"Medical disclaimer score: {disclaimer_score:.2f}")
        
        # Calculate weighted trust score
        trust_score = (
            self.weights['author'] * author_score +
            self.weights['citation'] * citation_score +
            self.weights['domain'] * domain_score +
            self.weights['recency'] * recency_score +
            self.weights['disclaimer'] * disclaimer_score
        )
        
        # Ensure score is between 0 and 1
        trust_score = max(0.0, min(1.0, trust_score))
        
        self.logger.info(f"Final trust score: {trust_score:.2f}")
        
        return trust_score
    
    def calculate_trust_score_with_breakdown(self, data: Dict) -> Dict:
        """
        Calculate trust score and return detailed breakdown.
        
        Similar to calculate_trust_score() but returns a dictionary with
        individual factor scores and the final trust score.
        
        Args:
            data: Dictionary containing content metadata.
        
        Returns:
            Dictionary containing:
            - 'trust_score': Final weighted score
            - 'author_score': Author credibility score
            - 'citation_score': Citation quality score
            - 'domain_score': Domain authority score
            - 'recency_score': Recency score
            - 'disclaimer_score': Medical disclaimer score
            - 'weights': Applied weights
        
        Example:
            >>> calculator = TrustScoreCalculator()
            >>> result = calculator.calculate_trust_score_with_breakdown(data)
            >>> print(result)
            {
                'trust_score': 0.82,
                'author_score': 1.0,
                'citation_score': 0.7,
                ...
            }
        """
        # Extract fields
        source_url = data.get('source_url', '')
        author = data.get('author', '')
        published_date = data.get('published_date', '')
        source_type = data.get('source_type', '')
        
        # Get content
        content = data.get('content', '')
        if not content and 'content_chunks' in data:
            chunks = data.get('content_chunks', [])
            if isinstance(chunks, list):
                content = ' '.join(str(chunk) for chunk in chunks)
        
        # Calculate individual scores
        author_score = self.calculate_author_score(author)
        citation_score = self.calculate_citation_score(source_type, content)
        domain_score = self.calculate_domain_score(source_url)
        recency_score = self.calculate_recency_score(published_date)
        disclaimer_score = self.calculate_disclaimer_score(content)
        
        # Calculate final trust score
        trust_score = (
            self.weights['author'] * author_score +
            self.weights['citation'] * citation_score +
            self.weights['domain'] * domain_score +
            self.weights['recency'] * recency_score +
            self.weights['disclaimer'] * disclaimer_score
        )
        
        trust_score = max(0.0, min(1.0, trust_score))
        
        return {
            'trust_score': round(trust_score, 3),
            'author_score': round(author_score, 3),
            'citation_score': round(citation_score, 3),
            'domain_score': round(domain_score, 3),
            'recency_score': round(recency_score, 3),
            'disclaimer_score': round(disclaimer_score, 3),
            'weights': self.weights
        }
