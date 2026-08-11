"""Tests for screen rectification in the AVD pipeline."""

from __future__ import annotations

import cv2
import numpy as np

from avd.vision.rectify import rectify_screen


def test_rectify_synthetic_quad() -> None:
    width, height = 640, 480
    warped = np.zeros((height, width, 3), dtype=np.uint8)
    quad = np.array([[150, 120], [520, 100], [540, 380], [100, 360]], dtype=np.int32)
    cv2.fillConvexPoly(warped, quad, (255, 255, 255))

    output, confidence = rectify_screen(warped, width, height)
    assert confidence > 0.0
    assert output.shape == (height, width, 3)
    values = output.reshape(-1, 3)
    assert any((pixel == [0, 0, 0]).all() for pixel in values)
    assert any((pixel == [255, 255, 255]).all() for pixel in values)
