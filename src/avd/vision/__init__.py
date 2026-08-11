"""Vision utilities for screen rectification, ROI extraction, digit recognition, and colour tagging.

This package contains the core image-processing pipeline for canonicalising
monitor screens and extracting readings from regions of interest.
"""

from .rectify import rectify_screen
from .roi_extract import crop_roi
from .digit_recognize import Recognizer, OnnxDigitRecognizer, StubDigitRecognizer
from .colour_tag import dominant_colour

__all__ = [
    "rectify_screen",
    "crop_roi",
    "Recognizer",
    "OnnxDigitRecognizer",
    "StubDigitRecognizer",
    "dominant_colour",
]
