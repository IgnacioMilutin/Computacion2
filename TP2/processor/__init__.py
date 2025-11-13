"""
Módulo de procesamiento intensivo (CPU-bound tasks).
"""

from .screenshot import generate_screenshot
from .performance import analyze_performance
from .image_processor import process_images, generate_thumbnail

__all__ = [
    'generate_screenshot',
    'analyze_performance',
    'process_images',
    'generate_thumbnail'
]