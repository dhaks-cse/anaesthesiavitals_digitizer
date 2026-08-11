"""Synthetic monitor generator for AVD tests."""

from __future__ import annotations

import cv2
import numpy as np


def generate_synthetic_screen(width: int = 1280, height: int = 720) -> "numpy.ndarray":
    screen = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.rectangle(screen, (100, 100), (1180, 620), (32, 32, 32), -1)
    cv2.putText(screen, "72", (920, 180), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 255, 0), 8)
    cv2.putText(screen, "98", (920, 320), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 0, 0), 8)
    cv2.putText(screen, "120", (400, 580), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (255, 255, 255), 8)
    return screen
