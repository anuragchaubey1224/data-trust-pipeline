"""
PubMed Scraper Module

This module provides a PubMedScraper class for extracting structured information
from PubMed research articles using the official NCBI E-utilities API.

Unlike the blog and YouTube scrapers, this class does NOT inherit from BaseScraper
because it retrieves data via API calls rather than HTML scraping.
"""

import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional

import requests


class PubMedScraper:
    """
    PubMed scraper for extracting structured information from research articles.
    
    Uses the NCBI E-utilities API (efetch) to retrieve article metadata and
    abstracts in XML format. No API key is required, but rate limiting applies
    (3 requests/second without key, 10 requests/second with key).
    
    Attributes:
        api_base_url: Base URL for NCBI E-utilities API
        timeout: Request timeout in seconds
        logger: Logger instance for debugging
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the PubMedScraper.
        
        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_pmid(self, url: str) -> Optional[str]:
        """
        Extract the PubMed ID (PMID) from a PubMed URL.
        
        Supports various URL formats:
        - https://pubmed.ncbi.nlm.nih.gov/31452104/
        - https://www.ncbi.nlm.nih.gov/pubmed/31452104
        - https://pubmed.ncbi.nlm.nih.gov/31452104
        
        Args:
            url: PubMed article URL
            
        Returns:
            PubMed ID as string, or None if not found
        """
        self.logger.info(f"Extracting PMID from URL: {url}")
        
        try:
            # Match patterns like /31452104/ or /31452104
            match = re.search(r'/(\d{7,8})/?', url)
            if match:
                pmid = match.group(1)
                self.logger.info(f"Extracted PMID: {pmid}")
                return pmid
            else:
                self.logger.error(f"Could not extract PMID from URL: {url}")
                return None
        except Exception as e:
            self.logger.error(f"Error extracting PMID: {str(e)}")
            return None
    
    def fetch_pubmed_xml(self, pmid: str) -> Optional[str]:
        """
        Fetch article data from PubMed via E-utilities API.
        
        Makes a request to the NCBI efetch API to retrieve article metadata
        and abstract in XML format.
        
        Args:
            pmid: PubMed ID of the article
            
        Returns:
            Raw XML response as string, or None if request fails
        """
        self.logger.info(f"Fetching PubMed article via API: PMID={pmid}")
        
        try:
            # Build API request URL
            params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            # Make API request
            response = requests.get(
                self.api_base_url,
                params=params,
                timeout=self.timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Return XML content
            xml_data = response.text
            self.logger.info(f"Successfully fetched XML data: {len(xml_data)} characters")
            return xml_data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout fetching PMID {pmid}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching PMID {pmid}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching PMID {pmid}: {str(e)}")
            return None
    
    def parse_pubmed_xml(self, xml_data: str) -> Dict[str, Optional[str]]:
        """
        Parse PubMed XML response and extract article metadata.
        
        Extracts the following fields from the XML:
        - ArticleTitle → title
        - AuthorList → authors (comma-separated)
        - Journal → journal name
        - PubDate → publication year
        - AbstractText → abstract content
        
        Args:
            xml_data: Raw XML response from E-utilities API
            
        Returns:
            Dictionary containing:
                - title: Article title
                - authors: Comma-separated list of authors
                - journal: Journal name
                - year: Publication year
                - abstract: Abstract text
        """
        self.logger.info("Parsing XML response")
        
        result = {
            "title": None,
            "authors": None,
            "journal": None,
            "year": None,
            "abstract": None
        }
        
        try:
            # Parse XML
            root = ET.fromstring(xml_data)
            
            # Find the PubmedArticle element
            article = root.find(".//PubmedArticle")
            if not article:
                self.logger.warning("PubmedArticle element not found in XML")
                return result
            
            # Extract title
            try:
                title_elem = article.find(".//ArticleTitle")
                if title_elem is not None and title_elem.text:
                    result["title"] = title_elem.text.strip()
                else:
                    self.logger.warning("Article title not found")
            except Exception as e:
                self.logger.warning(f"Error extracting title: {str(e)}")
            
            # Extract authors
            try:
                author_list = article.find(".//AuthorList")
                if author_list is not None:
                    authors = []
                    for author in author_list.findall(".//Author"):
                        # Try LastName + ForeName format
                        last_name = author.find("LastName")
                        fore_name = author.find("ForeName")
                        
                        if last_name is not None and fore_name is not None:
                            full_name = f"{fore_name.text} {last_name.text}"
                            authors.append(full_name)
                        elif last_name is not None:
                            authors.append(last_name.text)
                        else:
                            # Try CollectiveName for group authors
                            collective = author.find("CollectiveName")
                            if collective is not None and collective.text:
                                authors.append(collective.text)
                    
                    if authors:
                        result["authors"] = ", ".join(authors)
                else:
                    self.logger.warning("Authors not found")
            except Exception as e:
                self.logger.warning(f"Error extracting authors: {str(e)}")
            
            # Extract journal name
            try:
                journal_elem = article.find(".//Journal/Title")
                if journal_elem is not None and journal_elem.text:
                    result["journal"] = journal_elem.text.strip()
                else:
                    # Try ISOAbbreviation as fallback
                    iso_elem = article.find(".//Journal/ISOAbbreviation")
                    if iso_elem is not None and iso_elem.text:
                        result["journal"] = iso_elem.text.strip()
                    else:
                        self.logger.warning("Journal name not found")
            except Exception as e:
                self.logger.warning(f"Error extracting journal: {str(e)}")
            
            # Extract publication year
            try:
                # Try PubDate/Year first
                year_elem = article.find(".//PubDate/Year")
                if year_elem is not None and year_elem.text:
                    result["year"] = year_elem.text.strip()
                else:
                    # Try MedlineDate as fallback (format: "2019 Aug-Sep")
                    medline_date = article.find(".//PubDate/MedlineDate")
                    if medline_date is not None and medline_date.text:
                        # Extract year from MedlineDate
                        year_match = re.search(r'\b(19|20)\d{2}\b', medline_date.text)
                        if year_match:
                            result["year"] = year_match.group(0)
                        else:
                            self.logger.warning("Year not found in MedlineDate")
                    else:
                        self.logger.warning("Publication year not found")
            except Exception as e:
                self.logger.warning(f"Error extracting year: {str(e)}")
            
            # Extract abstract
            try:
                abstract_elems = article.findall(".//AbstractText")
                if abstract_elems:
                    # Handle structured abstracts (with labels)
                    abstract_parts = []
                    for elem in abstract_elems:
                        label = elem.get("Label", "")
                        text = elem.text or ""
                        
                        if label:
                            abstract_parts.append(f"{label}: {text.strip()}")
                        else:
                            abstract_parts.append(text.strip())
                    
                    result["abstract"] = "\n\n".join(abstract_parts)
                else:
                    self.logger.warning("Abstract not found")
            except Exception as e:
                self.logger.warning(f"Error extracting abstract: {str(e)}")
            
            return result
            
        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {str(e)}")
            return result
        except Exception as e:
            self.logger.error(f"Error parsing XML: {str(e)}")
            return result
    
    def scrape(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape a PubMed article using the E-utilities API.
        
        This method:
        1. Extracts the PMID from the URL
        2. Fetches article data from the PubMed API
        3. Parses the XML response
        4. Returns standardized dictionary format
        
        Args:
            url: URL of the PubMed article to scrape
            
        Returns:
            Dictionary containing:
                - source_url: The original article URL
                - source_type: "pubmed"
                - title: Article title
                - author: Comma-separated list of authors
                - published_date: Publication year
                - description: Journal name
                - content: Abstract text
        """
        self.logger.info(f"Scraping PubMed article: {url}")
        
        try:
            # Extract PMID from URL
            pmid = self.extract_pmid(url)
            if not pmid:
                self.logger.error(f"Failed to extract PMID from URL: {url}")
                return self._empty_result(url)
            
            # Fetch XML data from API
            xml_data = self.fetch_pubmed_xml(pmid)
            if not xml_data:
                self.logger.error(f"Failed to fetch data for PMID: {pmid}")
                return self._empty_result(url)
            
            # Parse XML
            parsed_data = self.parse_pubmed_xml(xml_data)
            
            # Build standardized result
            result = {
                "source_url": url,
                "source_type": "pubmed",
                "title": parsed_data.get("title"),
                "author": parsed_data.get("authors"),
                "published_date": parsed_data.get("year"),
                "description": parsed_data.get("journal"),
                "content": parsed_data.get("abstract")
            }
            
            # Log success
            word_count = len(result["content"].split()) if result["content"] else 0
            self.logger.info(
                f"Successfully scraped PubMed article: "
                f"PMID={pmid}, title='{result['title'][:50] if result['title'] else 'N/A'}...', "
                f"abstract_length={word_count} words"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping PubMed article {url}: {str(e)}")
            return self._empty_result(url)
    
    def _empty_result(self, url: str) -> Dict[str, Optional[str]]:
        """
        Create an empty result dictionary for failed scraping attempts.
        
        Args:
            url: The URL that was attempted to be scraped
            
        Returns:
            Dictionary with source_url and source_type, other fields None
        """
        return {
            "source_url": url,
            "source_type": "pubmed",
            "title": None,
            "author": None,
            "published_date": None,
            "description": None,
            "content": None
        }
