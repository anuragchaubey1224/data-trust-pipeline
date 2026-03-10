"""
Base Scraper Foundation Layer

This module provides a reusable BaseScraper class for web scraping operations.
It includes retry logic, error handling, logging, and HTML parsing capabilities.
"""

import logging
import time
from typing import Optional

import certifi
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
    RequestException,
    SSLError
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseScraper:
    """
    Base scraper class for fetching and parsing web content.
    
    This class provides core functionality for making HTTP requests with
    retry logic, timeout handling, and HTML parsing using BeautifulSoup.
    
    Attributes:
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 2)
        headers: HTTP request headers including User-Agent
        logger: Logger instance for debugging
    """
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
        verify_ssl: bool = True
    ):
        """
        Initialize the BaseScraper.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 2)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        
        # Realistic browser User-Agent header
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # Initialize logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch a web page with retry logic and error handling.
        
        Makes an HTTP GET request with automatic retries on failure.
        Includes timeout handling and comprehensive error logging.
        
        Args:
            url: The URL to fetch
        
        Returns:
            Raw HTML content as a string
        
        Raises:
            RequestException: If all retry attempts fail
            ValueError: If the URL is invalid or empty
        
        Example:
            >>> scraper = BaseScraper()
            >>> html = scraper.fetch_page('https://example.com')
        """
        if not url or not isinstance(url, str):
            raise ValueError(f"Invalid URL: {url}")
        
        self.logger.info(f"Fetching URL: {url}")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.debug(
                    f"Attempt {attempt}/{self.max_retries} for {url}"
                )
                
                # Make HTTP GET request with SSL verification
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=certifi.where() if self.verify_ssl else False
                )
                
                # Raise exception for bad status codes (4xx, 5xx)
                response.raise_for_status()
                
                self.logger.info(
                    f"Successfully fetched {url} "
                    f"(Status: {response.status_code}, "
                    f"Size: {len(response.content)} bytes)"
                )
                
                return response.text
            
            except Timeout as e:
                self.logger.warning(
                    f"Timeout on attempt {attempt}/{self.max_retries} for {url}: {e}"
                )
                if attempt == self.max_retries:
                    self.logger.error(f"All retry attempts exhausted for {url}")
                    raise RequestException(
                        f"Request timed out after {self.max_retries} attempts: {url}"
                    ) from e
            
            except SSLError as e:
                self.logger.warning(
                    f"SSL error on attempt {attempt}/{self.max_retries} for {url}: {e}"
                )
                if attempt == self.max_retries:
                    self.logger.error(
                        f"SSL verification failed after {self.max_retries} attempts for {url}. "
                        r"Try: pip install --upgrade certifi or run /Applications/Python\ 3.12/Install\ Certificates.command"
                    )
                    raise RequestException(
                        f"SSL verification failed after {self.max_retries} attempts: {url}"
                    ) from e
            
            except ConnectionError as e:
                self.logger.warning(
                    f"Connection error on attempt {attempt}/{self.max_retries} for {url}: {e}"
                )
                if attempt == self.max_retries:
                    self.logger.error(f"Connection failed after {self.max_retries} attempts for {url}")
                    raise RequestException(
                        f"Connection failed after {self.max_retries} attempts: {url}"
                    ) from e
            
            except HTTPError as e:
                status_code = e.response.status_code if e.response else 'unknown'
                self.logger.error(
                    f"HTTP error {status_code} on attempt {attempt}/{self.max_retries} for {url}: {e}"
                )
                
                # Don't retry on client errors (4xx) except 429 (rate limit)
                if e.response and 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    self.logger.error(f"Client error, not retrying: {url}")
                    raise RequestException(
                        f"HTTP {status_code} error: {url}"
                    ) from e
                
                if attempt == self.max_retries:
                    self.logger.error(f"HTTP error persisted after {self.max_retries} attempts for {url}")
                    raise RequestException(
                        f"HTTP error after {self.max_retries} attempts: {url}"
                    ) from e
            
            except RequestException as e:
                self.logger.warning(
                    f"Request exception on attempt {attempt}/{self.max_retries} for {url}: {e}"
                )
                if attempt == self.max_retries:
                    self.logger.error(f"Request failed after {self.max_retries} attempts for {url}")
                    raise RequestException(
                        f"Request failed after {self.max_retries} attempts: {url}"
                    ) from e
            
            # Wait before retrying (except on last attempt)
            if attempt < self.max_retries:
                self.logger.info(f"Waiting {self.retry_delay}s before retry...")
                time.sleep(self.retry_delay)
        
        # This should never be reached due to the raise in the loop
        raise RequestException(f"Unexpected error fetching {url}")
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content into a BeautifulSoup object.
        
        Uses the lxml parser for fast and efficient HTML parsing.
        
        Args:
            html: Raw HTML content as a string
        
        Returns:
            BeautifulSoup object for parsing and navigation
        
        Raises:
            ValueError: If HTML is empty or invalid
        
        Example:
            >>> scraper = BaseScraper()
            >>> html = '<html><body><h1>Title</h1></body></html>'
            >>> soup = scraper.parse_html(html)
            >>> print(soup.h1.text)
            Title
        """
        if not html or not isinstance(html, str):
            raise ValueError("HTML content is empty or invalid")
        
        self.logger.debug(f"Parsing HTML content ({len(html)} characters)")
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            self.logger.debug("HTML parsed successfully")
            return soup
        
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
            raise ValueError(f"Failed to parse HTML: {e}") from e
    
    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Fetch a URL and return parsed BeautifulSoup object.
        
        This is a convenience method that combines fetch_page() and parse_html()
        into a single operation.
        
        Args:
            url: The URL to fetch and parse
        
        Returns:
            BeautifulSoup object ready for content extraction
        
        Raises:
            RequestException: If fetching fails
            ValueError: If parsing fails
        
        Example:
            >>> scraper = BaseScraper()
            >>> soup = scraper.get_soup('https://example.com')
            >>> title = soup.title.text
        """
        self.logger.info(f"Fetching and parsing: {url}")
        
        # Fetch the page
        html = self.fetch_page(url)
        
        # Parse the HTML
        soup = self.parse_html(html)
        
        self.logger.info(f"Successfully retrieved and parsed: {url}")
        return soup
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text content using a CSS selector.
        
        Helper method for extracting text from parsed HTML.
        
        Args:
            soup: BeautifulSoup object
            selector: CSS selector string
        
        Returns:
            Extracted text or None if not found
        
        Example:
            >>> scraper = BaseScraper()
            >>> soup = scraper.get_soup('https://example.com')
            >>> title = scraper.extract_text(soup, 'h1')
        """
        try:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
            return None
        except Exception as e:
            self.logger.warning(f"Error extracting text with selector '{selector}': {e}")
            return None


def main():
    """
    Demonstration of BaseScraper usage.
    
    This example shows how to use the BaseScraper class to fetch
    and parse web content.
    """
    # Initialize scraper
    scraper = BaseScraper(timeout=30, max_retries=3, retry_delay=2)
    
    # Example URL (a simple, reliable website)
    test_url = "https://example.com"
    
    print("=" * 60)
    print("BaseScraper Demo")
    print("=" * 60)
    
    try:
        # Method 1: Fetch and parse separately
        print("\n[Method 1] Fetch and parse separately:")
        print(f"Fetching: {test_url}")
        html = scraper.fetch_page(test_url)
        print(f"✓ Fetched {len(html)} characters")
        
        soup = scraper.parse_html(html)
        print(f"✓ Parsed HTML successfully")
        
        # Extract title
        title = soup.title.text if soup.title else "No title found"
        print(f"Page title: {title}")
        
        # Method 2: Use convenience method
        print("\n[Method 2] Using get_soup():")
        soup = scraper.get_soup(test_url)
        
        # Extract heading
        h1 = scraper.extract_text(soup, 'h1')
        print(f"Main heading: {h1}")
        
        # Extract paragraph
        p = scraper.extract_text(soup, 'p')
        print(f"First paragraph: {p[:100]}..." if p and len(p) > 100 else f"First paragraph: {p}")
        
        print("\n" + "=" * 60)
        print("✓ Demo completed successfully")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()