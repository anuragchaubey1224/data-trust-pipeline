"""
YouTube Scraper Module

This module provides a YouTubeScraper class for extracting structured content
from YouTube videos including metadata and transcripts.
"""

import logging
import re
from typing import Dict, Optional
from datetime import datetime

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class YouTubeScraper:
    """
    YouTube scraper for extracting video metadata and transcripts.
    
    Extracts structured information from YouTube videos including title,
    channel name, publish date, description, and video transcripts.
    
    Attributes:
        logger: Logger instance for debugging
    """
    
    def __init__(self):
        """Initialize the YouTubeScraper."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract YouTube video ID from a URL.
        
        Supports various YouTube URL formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        
        Args:
            url: YouTube video URL
        
        Returns:
            Video ID string
        
        Raises:
            ValueError: If video ID cannot be extracted
        
        Example:
            >>> scraper = YouTubeScraper()
            >>> video_id = scraper.extract_video_id('https://www.youtube.com/watch?v=aircAruvnKk')
            >>> print(video_id)
            aircAruvnKk
        """
        # Pattern to match various YouTube URL formats
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard watch URL
            r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URL
            r'^([0-9A-Za-z_-]{11})$'             # Just the ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                self.logger.debug(f"Extracted video ID: {video_id}")
                return video_id
        
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    def get_video_metadata(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract video metadata using yt-dlp.
        
        Extracts title, author (channel name), publish date, and description
        from the YouTube video.
        
        Args:
            url: YouTube video URL
        
        Returns:
            Dictionary containing metadata fields
        
        Raises:
            Exception: If metadata extraction fails
        
        Example:
            >>> scraper = YouTubeScraper()
            >>> metadata = scraper.get_video_metadata('https://www.youtube.com/watch?v=aircAruvnKk')
            >>> print(metadata['title'])
        """
        self.logger.info("Extracting video metadata")
        
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            # Extract metadata
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                metadata = {
                    'title': info.get('title'),
                    'author': info.get('uploader') or info.get('channel'),
                    'publish_date': info.get('upload_date'),
                    'description': info.get('description')
                }
            
            self.logger.info(
                f"Successfully extracted metadata: title='{metadata['title']}', "
                f"author='{metadata['author']}'"
            )
            
            return metadata
        
        except Exception as e:
            self.logger.error(f"Error extracting video metadata: {e}")
            raise
    
    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Fetch video transcript using youtube-transcript-api.
        
        Attempts to fetch the transcript in English. If not available,
        returns None and logs a warning.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Full transcript text as a string, or None if unavailable
        
        Example:
            >>> scraper = YouTubeScraper()
            >>> transcript = scraper.get_transcript('aircAruvnKk')
            >>> print(f"Transcript length: {len(transcript.split())} words")
        """
        self.logger.info(f"Fetching transcript for video ID: {video_id}")
        
        try:
            # Fetch transcript using the API
            api = YouTubeTranscriptApi()
            fetched_transcript = api.fetch(video_id)
            
            # Extract text from all snippets
            transcript_text = ' '.join([snippet.text for snippet in fetched_transcript.snippets])
            
            word_count = len(transcript_text.split())
            self.logger.info(f"Successfully fetched transcript: {word_count} words")
            
            return transcript_text
        
        except TranscriptsDisabled:
            self.logger.warning(f"Transcripts are disabled for video: {video_id}")
            return None
        
        except NoTranscriptFound:
            self.logger.warning(f"No transcript found for video: {video_id}")
            return None
        
        except VideoUnavailable:
            self.logger.error(f"Video unavailable: {video_id}")
            return None
        
        except Exception as e:
            self.logger.warning(f"Error fetching transcript: {e}")
            return None
    
    def scrape(self, url: str) -> Dict[str, Optional[str]]:
        """
        Scrape a YouTube video and extract structured content.
        
        Main method that coordinates the extraction of video ID, metadata,
        and transcript, returning a structured dictionary.
        
        Args:
            url: YouTube video URL
        
        Returns:
            Dictionary containing:
                - source_url: The video URL
                - source_type: Always "youtube"
                - title: Video title
                - author: Channel name
                - published_date: Publication date
                - description: Video description
                - content: Full transcript text
        
        Raises:
            Exception: If scraping fails
        
        Example:
            >>> scraper = YouTubeScraper()
            >>> result = scraper.scrape('https://www.youtube.com/watch?v=aircAruvnKk')
            >>> print(result['title'])
        """
        self.logger.info(f"Scraping YouTube video: {url}")
        
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            
            # Get video metadata
            metadata = self.get_video_metadata(url)
            
            # Fetch transcript
            transcript = self.get_transcript(video_id)
            
            # Compile structured result
            result = {
                'source_url': url,
                'source_type': 'youtube',
                'title': metadata.get('title'),
                'author': metadata.get('author'),
                'published_date': metadata.get('publish_date'),
                'description': metadata.get('description'),
                'content': transcript
            }
            
            # Log summary
            content_length = len(transcript.split()) if transcript else 0
            self.logger.info(
                f"Successfully scraped YouTube video: "
                f"title='{result['title']}', "
                f"transcript_length={content_length} words"
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error scraping YouTube video {url}: {e}")
            raise
    
    def scrape_multiple(self, urls: list) -> list:
        """
        Scrape multiple YouTube videos.
        
        Convenience method for batch processing multiple video URLs.
        
        Args:
            urls: List of YouTube video URLs
        
        Returns:
            List of dictionaries containing scraped data
        
        Example:
            >>> scraper = YouTubeScraper()
            >>> urls = ['https://www.youtube.com/watch?v=id1', 'https://www.youtube.com/watch?v=id2']
            >>> results = scraper.scrape_multiple(urls)
            >>> print(f"Scraped {len(results)} videos")
        """
        results = []
        total = len(urls)
        
        self.logger.info(f"Starting batch scrape of {total} YouTube videos")
        
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
                    'source_type': 'youtube',
                    'title': None,
                    'author': None,
                    'published_date': None,
                    'description': None,
                    'content': None,
                    'error': str(e)
                })
        
        self.logger.info(f"Completed batch scrape: {len(results)}/{total} processed")
        return results
