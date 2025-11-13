"""
Módulo de scraping web asíncrono.
"""

from .html_parser import parse_html
from .metadata_extractor import extract_metadata
from .async_http import fetch_url

__all__ = [
    'parse_html',
    'extract_metadata',
    'fetch_url'
]