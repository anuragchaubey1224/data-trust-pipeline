"""
Helper utilities for the data trust pipeline.

This module provides utility functions for loading and managing configuration files.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml


def load_sources(config_path: str = "config/sources.yaml") -> Dict[str, List[str]]:
    """
    Load and parse data source URLs from a YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file containing source URLs.
                    Defaults to 'config/sources.yaml'.
    
    Returns:
        Dictionary containing lists of URLs for each source type:
        - 'blogs': List of blog URLs
        - 'youtube': List of YouTube video URLs
        - 'pubmed': List of PubMed article URLs
    
    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
        ValueError: If the configuration structure is invalid.
    
    Example:
        >>> sources = load_sources()
        >>> print(sources['blogs'])
        ['https://towardsdatascience.com/sample-article', ...]
    """
    # Convert to absolute path if relative
    config_path_obj = Path(config_path)
    
    # Check if file exists
    if not config_path_obj.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            f"Please ensure the file exists at the specified location."
        )
    
    try:
        # Read and parse YAML file
        with open(config_path_obj, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
        # Validate configuration structure
        if not isinstance(config_data, dict):
            raise ValueError(
                f"Invalid configuration format. Expected a dictionary, "
                f"got {type(config_data).__name__}"
            )
        
        # Ensure all required keys exist
        required_keys = ['blogs', 'youtube', 'pubmed']
        missing_keys = [key for key in required_keys if key not in config_data]
        
        if missing_keys:
            raise ValueError(
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )
        
        # Validate that each key contains a list
        for key in required_keys:
            if not isinstance(config_data[key], list):
                raise ValueError(
                    f"Configuration key '{key}' must be a list, "
                    f"got {type(config_data[key]).__name__}"
                )
        
        return config_data
    
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Error parsing YAML file '{config_path}': {str(e)}"
        )
    except Exception as e:
        raise Exception(
            f"Unexpected error loading configuration from '{config_path}': {str(e)}"
        )


def get_source_count(sources: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Get the count of URLs for each source type.
    
    Args:
        sources: Dictionary of source URLs returned by load_sources().
    
    Returns:
        Dictionary with counts for each source type.
    
    Example:
        >>> sources = load_sources()
        >>> counts = get_source_count(sources)
        >>> print(counts)
        {'blogs': 3, 'youtube': 2, 'pubmed': 1}
    """
    return {key: len(urls) for key, urls in sources.items()}
