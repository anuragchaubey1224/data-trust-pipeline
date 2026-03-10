"""
Blog Scraper Module

This module provides a BlogScraper class for extracting structured content
from blog articles. It inherits from BaseScraper and uses readability-lxml
for content extraction.
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from bs4 import BeautifulSoup
from readability import Document

from .base_scraper import BaseScraper


class BlogScraper(BaseScraper):
    """
    Blog scraper for extracting structured content from blog articles.
    
    Inherits from BaseScraper to leverage HTTP fetching, retry logic,
    and HTML parsing capabilities. Extracts metadata (title, author,
    published date, description) and main article content.
    
    Attributes:
        Inherits all attributes from BaseScraper
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
        verify_ssl: bool = True
    ):
        """
        Initialize the BlogScraper.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 2)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        super().__init__(timeout, max_retries, retry_delay, verify_ssl)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def scrape(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape a blog article and extract structured content.
        
        Fetches the page, extracts metadata (title, author, date, description),
        and extracts the main article content.
        
        Args:
            url: The URL of the blog article to scrape
        
        Returns:
            Dictionary containing:
                - source_url: The URL of the article
                - source_type: Always "blog"
                - title: Article title
                - author: Article author
                - published_date: Publication date
                - description: Article description/summary
                - content: Main article text
        
        Raises:
            RequestException: If fetching the page fails
            
        Example:
            >>> scraper = BlogScraper()
            >>> result = scraper.scrape('https://example.com/article')
            >>> print(result['title'])
        """
        self.logger.info(f"Scraping blog URL: {url}")
        
        try:
            # Fetch the page HTML
            html = self.fetch_page(url)
            
            # Parse HTML
            soup = self.parse_html(html)
            
            # Extract metadata
            self.logger.info("Extracting metadata from blog article")
            metadata = self.extract_metadata(soup)
            
            # Extract main article content
            self.logger.info("Extracting article content")
            content = self.extract_article(html)
            
            # Compile structured result
            result = {
                'source_url': url,
                'source_type': 'blog',
                'title': metadata.get('title'),
                'author': metadata.get('author'),
                'published_date': metadata.get('published_date'),
                'description': metadata.get('description'),
                'content': content
            }
            
            # Log summary
            content_length = len(content.split()) if content else 0
            self.logger.info(
                f"Successfully scraped blog article: "
                f"title='{result['title']}', "
                f"content_length={content_length} words"
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error scraping blog article {url}: {e}")
            raise
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """
        Extract metadata from blog article HTML.
        
        Extracts title, author, published date, and description using
        common HTML meta tags and OpenGraph tags.
        
        Args:
            soup: BeautifulSoup object of the page HTML
        
        Returns:
            Dictionary with metadata fields (may contain None values)
        
        Example:
            >>> soup = BeautifulSoup(html, 'lxml')
            >>> metadata = scraper.extract_metadata(soup)
            >>> print(metadata['title'])
        """
        metadata = {
            'title': None,
            'author': None,
            'published_date': None,
            'description': None
        }
        
        # Extract title
        # Try OpenGraph title first, then regular title tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata['title'] = og_title['content'].strip()
        elif soup.title:
            metadata['title'] = soup.title.text.strip()
        else:
            # Try h1 as fallback
            h1 = soup.find('h1')
            if h1:
                metadata['title'] = h1.get_text(strip=True)
                
        if not metadata['title']:
            self.logger.warning("Could not extract title from blog article")
        
        # Extract author
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta and author_meta.get('content'):
            metadata['author'] = author_meta['content'].strip()
        else:
            # Try article:author meta tag
            author_article = soup.find('meta', property='article:author')
            if author_article and author_article.get('content'):
                metadata['author'] = author_article['content'].strip()
        
        if not metadata['author']:
            self.logger.warning("Could not extract author from blog article")
        
        # Extract published date
        date_published = soup.find('meta', property='article:published_time')
        if date_published and date_published.get('content'):
            metadata['published_date'] = date_published['content'].strip()
        else:
            # Try alternate date meta tags
            date_meta = soup.find('meta', attrs={'name': 'date'})
            if date_meta and date_meta.get('content'):
                metadata['published_date'] = date_meta['content'].strip()
            else:
                # Try pubdate meta tag
                pubdate = soup.find('meta', attrs={'name': 'pubdate'})
                if pubdate and pubdate.get('content'):
                    metadata['published_date'] = pubdate['content'].strip()
                else:
                    # Try time tag with datetime attribute
                    time_tag = soup.find('time', attrs={'datetime': True})
                    if time_tag:
                        metadata['published_date'] = time_tag['datetime'].strip()
        
        if not metadata['published_date']:
            self.logger.warning("Could not extract published date from blog article")
        
        # Extract description
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta and desc_meta.get('content'):
            metadata['description'] = desc_meta['content'].strip()
        else:
            # Try OpenGraph description
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                metadata['description'] = og_desc['content'].strip()
        
        if not metadata['description']:
            self.logger.warning("Could not extract description from blog article")
        
        return metadata
    
    def extract_article(self, html: str) -> str:
        """
        Extract main article content from HTML using readability.
        
        Uses the readability-lxml library to identify and extract the main
        article content, removing ads, navigation, and other boilerplate.
        Includes preprocessing to remove unwanted elements and fallback
        strategies for better content extraction.
        
        Args:
            html: Raw HTML content as a string
        
        Returns:
            Cleaned article text as a string
        
        Example:
            >>> content = scraper.extract_article(html)
            >>> print(f"Article length: {len(content.split())} words")
        """
        try:
            # Preprocess: Remove unwanted elements and sanitize HTML
            preprocessed_html = self._preprocess_html(html)
            sanitized_html = self._sanitize_html(preprocessed_html)
            
            # Use readability to extract main content with better settings
            doc = Document(
                sanitized_html,
                min_text_length=50,  # Lower threshold for better content capture
                retry_length=200
            )
            article_html = doc.summary()
            
            # Check if readability returned valid content
            if not article_html or len(article_html.strip()) < 50:
                raise ValueError("Readability returned insufficient content")
            
            # Parse the cleaned HTML
            soup = BeautifulSoup(article_html, 'lxml')
            
            # Post-process: Remove remaining unwanted elements
            self._remove_unwanted_elements(soup)
            
            # Extract text from content elements
            paragraphs = []
            
            # Extract from semantic content tags
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'pre', 'code']):
                text = tag.get_text(strip=True)
                
                # Filter out unwanted patterns
                if text and self._is_valid_content(text):
                    paragraphs.append(text)
            
            # Join all paragraphs with double newlines
            content = '\n\n'.join(paragraphs)
            
            # If content is still empty or too short, try fallback extraction
            if not content or len(content.split()) < 50:
                self.logger.warning("Primary extraction yielded insufficient content, trying fallback")
                content = self._fallback_extraction(html)
            
            if not content:
                self.logger.warning("Extracted content is empty")
            
            return content
        
        except Exception as e:
            self.logger.error(f"Error extracting article content: {e}")
            # Try fallback extraction on error
            try:
                return self._fallback_extraction(html)
            except Exception as fallback_error:
                self.logger.error(f"Fallback extraction also failed: {fallback_error}")
                return ""
    
    def _preprocess_html(self, html: str) -> str:
        """
        Preprocess HTML by removing unwanted elements before main extraction.
        
        Removes navigation, ads, sidebars, footers, and other non-content elements
        that interfere with content extraction.
        
        Args:
            html: Raw HTML content
        
        Returns:
            Preprocessed HTML with unwanted elements removed
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # List of unwanted element selectors
        unwanted_selectors = [
            # Navigation elements
            'nav', 'header', 'footer', '[role="navigation"]', '[role="banner"]',
            '.nav', '.navigation', '.navbar', '.menu', '.header', '.footer',
            '#nav', '#navigation', '#navbar', '#menu', '#header', '#footer',
            
            # Ads and promotional content
            '.ad', '.ads', '.advertisement', '.promo', '.promotion', '.sponsored',
            '#ad', '#ads', '#advertisement', 
            '[class*="ad-"]', '[id*="ad-"]', '[class*="ads-"]',
            'iframe[src*="ads"]', 'iframe[src*="doubleclick"]',
            
            # Sidebars and complementary content
            'aside', '.sidebar', '.side-bar', '#sidebar', '[role="complementary"]',
            
            # Social sharing and related
            '.share', '.social', '.sharing', '.share-buttons', '.social-share',
            '.related', '.related-posts', '.related-articles',
            
            # Comments
            '.comments', '.comment-section', '#comments', '[class*="comment"]',
            
            # Cookie banners and popups
            '.cookie', '.cookie-banner', '.cookie-notice', '.gdpr',
            '.modal', '.popup', '.overlay',
            
            # Scripts and styles
            'script', 'style', 'noscript',
            
            # Other common unwanted elements
            '.newsletter', '.subscription', '.subscribe', 
            '.breadcrumb', '.breadcrumbs',
            '[class*="author-bio"]', '[class*="author-info"]'
        ]
        
        # Remove unwanted elements
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()
        
        # Remove elements with specific attributes indicating ads/tracking
        for element in soup.find_all(attrs={'data-ad': True}):
            element.decompose()
        for element in soup.find_all(attrs={'data-ad-slot': True}):
            element.decompose()
        
        return str(soup)
    
    def _sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML by removing NULL bytes and control characters.
        
        Fixes issues with readability/lxml when HTML contains invalid characters.
        
        Args:
            html: HTML string to sanitize
        
        Returns:
            Sanitized HTML string
        """
        # Remove NULL bytes
        html = html.replace('\x00', '')
        
        # Remove control characters (except tab, newline, carriage return)
        sanitized = []
        for char in html:
            code = ord(char)
            # Keep: tab (9), newline (10), carriage return (13), and printable chars (32-126, 128+)
            if code in (9, 10, 13) or code >= 32:
                sanitized.append(char)
        
        return ''.join(sanitized)
    
    def _remove_unwanted_elements(self, soup: BeautifulSoup) -> None:
        """
        Remove unwanted elements from BeautifulSoup object (in-place).
        
        Post-processing step to remove elements that might have passed
        through readability extraction.
        
        Args:
            soup: BeautifulSoup object to clean
        """
        # Remove elements with display:none or visibility:hidden
        for element in soup.find_all(style=True):
            style = element.get('style', '').lower()
            if 'display:none' in style or 'display: none' in style:
                element.decompose()
            elif 'visibility:hidden' in style or 'visibility: hidden' in style:
                element.decompose()
        
        # Remove common unwanted classes that slip through
        unwanted_classes = [
            'share', 'social', 'advertisement', 'promo', 'sidebar',
            'related', 'comments', 'footer', 'header', 'nav'
        ]
        
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', [])).lower()
            if any(unwanted in classes for unwanted in unwanted_classes):
                element.decompose()
    
    def _is_valid_content(self, text: str) -> bool:
        """
        Check if text is valid article content.
        
        Filters out common non-content patterns like navigation links,
        copyright notices, and promotional text.
        
        Args:
            text: Text to validate
        
        Returns:
            True if text appears to be valid content, False otherwise
        """
        # Filter out very short text
        if len(text) < 10:
            return False
        
        # Filter out common non-content patterns (case-insensitive)
        text_lower = text.lower()
        
        unwanted_patterns = [
            'click here', 'read more', 'continue reading', 'share this',
            'tweet this', 'subscribe', 'sign up', 'follow us',
            'cookie', 'terms of service', 'privacy policy',
            'all rights reserved', '©', 'copyright',
            'advertisement', 'sponsored',
            'table of contents', 'jump to',
        ]
        
        # If text consists mainly of unwanted patterns, reject it
        if any(pattern in text_lower for pattern in unwanted_patterns):
            if len(text) < 100:  # Only reject short text with these patterns
                return False
        
        # Filter out text that's mostly links or navigation
        if text_lower.count('|') > 3 or text_lower.count('»') > 2:
            return False
        
        return True
    
    def _fallback_extraction(self, html: str) -> str:
        """
        Fallback content extraction strategy.
        
        Alternative extraction method when readability fails or produces
        insufficient content. Tries to find content using semantic HTML5
        elements and common content class/id patterns.
        
        Args:
            html: Raw HTML content
        
        Returns:
            Extracted content text
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Remove unwanted elements first
            for selector in ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']:
                for element in soup.find_all(selector):
                    element.decompose()
            
            # Strategy 1: Look for semantic HTML5 article tag
            article = soup.find('article')
            if article:
                self.logger.debug("Fallback: Found <article> tag")
                paragraphs = []
                for p in article.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                    text = p.get_text(strip=True)
                    if text and self._is_valid_content(text):
                        paragraphs.append(text)
                
                content = '\n\n'.join(paragraphs)
                if len(content.split()) > 50:
                    return content
            
            # Strategy 2: Look for main tag
            main = soup.find('main')
            if main:
                self.logger.debug("Fallback: Found <main> tag")
                paragraphs = []
                for p in main.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                    text = p.get_text(strip=True)
                    if text and self._is_valid_content(text):
                        paragraphs.append(text)
                
                content = '\n\n'.join(paragraphs)
                if len(content.split()) > 50:
                    return content
            
            # Strategy 3: Look for common content class/id patterns
            content_patterns = [
                ('class', 'article-content'),
                ('class', 'post-content'),
                ('class', 'entry-content'),
                ('class', 'content'),
                ('id', 'content'),
                ('id', 'main-content'),
                ('class', 'main-content'),
                ('class', 'post'),
                ('class', 'article'),
            ]
            
            for attr_type, attr_value in content_patterns:
                try:
                    if attr_type == 'class':
                        container = soup.find('div', class_=attr_value)
                    else:
                        container = soup.find('div', id=attr_value)
                    
                    if container:
                        self.logger.debug(f"Fallback: Found content container with {attr_type}={attr_value}")
                        paragraphs = []
                        for p in container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                            text = p.get_text(strip=True)
                            if text and self._is_valid_content(text):
                                paragraphs.append(text)
                        
                        content = '\n\n'.join(paragraphs)
                        if len(content.split()) > 50:
                            return content
                except Exception as e:
                    self.logger.debug(f"Error checking pattern {attr_type}={attr_value}: {e}")
                    continue
            
            # Strategy 4: Extract all paragraphs from body, filtering heavily
            self.logger.debug("Fallback: Extracting all paragraphs from body")
            body = soup.find('body')
            if body:
                paragraphs = []
                for p in body.find_all('p'):
                    text = p.get_text(strip=True)
                    # More strict filtering for this fallback
                    if text and len(text) > 30 and self._is_valid_content(text):
                        paragraphs.append(text)
                
                return '\n\n'.join(paragraphs)
            
            return ""
        
        except Exception as e:
            self.logger.error(f"Error in fallback extraction: {e}")
            return ""
    
    def scrape_multiple(self, urls: list) -> list:
        """
        Scrape multiple blog articles.
        
        Convenience method for scraping multiple URLs.
        
        Args:
            urls: List of blog article URLs
        
        Returns:
            List of dictionaries containing scraped data
        
        Example:
            >>> scraper = BlogScraper()
            >>> urls = ['https://example.com/post1', 'https://example.com/post2']
            >>> results = scraper.scrape_multiple(urls)
            >>> print(f"Scraped {len(results)} articles")
        """
        results = []
        total = len(urls)
        
        self.logger.info(f"Starting batch scrape of {total} blog articles")
        
        for idx, url in enumerate(urls, 1):
            self.logger.info(f"Processing {idx}/{total}: {url}")
            
            try:
                result = self.scrape(url)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to scrape {url}: {e}")
                # Add failed entry to maintain order
                results.append({
                    'source_url': url,
                    'source_type': 'blog',
                    'title': None,
                    'author': None,
                    'published_date': None,
                    'description': None,
                    'content': None,
                    'error': str(e)
                })
        
        self.logger.info(f"Completed batch scrape: {len(results)}/{total} processed")
        return results
