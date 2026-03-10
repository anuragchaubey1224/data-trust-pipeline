"""
Storage Module

This module provides data storage functionality for the data pipeline.

Classes:
    JSONStorageWriter: Write processed data to JSON files with schema normalization
"""

from storage.json_writer import JSONStorageWriter

__all__ = ['JSONStorageWriter']
