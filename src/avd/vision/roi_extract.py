"""ROI extraction utilities for the AVD pipeline.

This module crops regions of interest from a rectified monitor frame.
"""

from __future__ import annotations

from typing import Tuple

import cv2


def crop_roi(frame: "cv2.Mat", roi: Tuple[int, int, int, int]) -> "cv2.Mat":
    x, y, w, h = roi
    return frame[y : y + h, x : x + w].copy()
