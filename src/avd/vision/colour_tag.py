"""Colour tagging utilities for AVD plausibility checks.

This module computes a dominant colour for a region of interest and maps it to
an expected colour label.
"""

from __future__ import annotations

from collections import Counter

import cv2
import numpy as np


def _bgr_to_name(bgr: tuple[int, int, int]) -> str:
    blue, green, red = bgr
    if red > green and red > blue:
        return "red"
    if green > red and green > blue:
        return "green"
    if blue > red and blue > green:
        return "blue"
    return "white"


def dominant_colour(roi: "cv2.Mat") -> str:
    pixels = roi.reshape(-1, 3)
    sample = pixels[np.random.choice(pixels.shape[0], min(1000, pixels.shape[0]), replace=False)]
    counts = Counter(tuple(int(v) for v in pixel) for pixel in sample)
    most_common = counts.most_common(1)
    if not most_common:
        return "unknown"
    return _bgr_to_name(most_common[0][0])
