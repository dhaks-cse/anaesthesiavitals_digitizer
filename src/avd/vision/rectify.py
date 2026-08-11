"""Screen rectification utilities for the AVD pipeline.

This module detects the largest screen quadrilateral in a frame, computes a
homography, and warps the image to a fixed canonical size.
"""

from __future__ import annotations

import cv2
import numpy as np
from typing import Optional, Tuple


def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def rectify_screen(frame: "cv2.Mat", width: int, height: int) -> Tuple["cv2.Mat", float]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    best_quad: Optional[np.ndarray] = None
    best_area = 0.0

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > best_area:
                best_area = area
                best_quad = approx.reshape(4, 2)

    if best_quad is None or best_area < 1000:
        return frame.copy(), 0.0

    src_pts = _order_points(best_quad)
    dst_pts = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(frame, matrix, (width, height))
    confidence = min(1.0, best_area / (frame.shape[0] * frame.shape[1]))
    return warped, float(confidence)
