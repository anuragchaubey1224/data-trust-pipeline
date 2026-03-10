"""
Scoring Module for Data Trust Pipeline

This module contains trust scoring components for evaluating
content source credibility and reliability.

Key Components:
- TrustScoreCalculator: Calculates weighted trust scores based on
  multiple credibility factors
"""

from .trust_score import TrustScoreCalculator

__all__ = ['TrustScoreCalculator']
