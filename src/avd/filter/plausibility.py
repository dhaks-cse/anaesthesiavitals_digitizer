"""Plausibility filter for AVD readings.

This module rejects invalid readings if they violate profile bounds, colour
expectations, or allowed rate-of-change, while preserving confidence values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import cv2

from ..vision.colour_tag import dominant_colour
from ..store.models import ProfileParameter

if TYPE_CHECKING:
    from numpy import ndarray


@dataclass
class FilterResult:
    value: float | None
    confidence: float
    reason: str | None = None
    verified: bool = True


class PlausibilityFilter:
    """Apply plausibility rules and optional smoothing to readings."""

    def __init__(self) -> None:
        self.last_values: dict[str, float] = {}

    def filter(
        self,
        parameter: ProfileParameter,
        value: float,
        confidence: float,
        roi_image: "numpy.ndarray",
        timestamp: float,
    ) -> FilterResult:
        if value < parameter.min or value > parameter.max:
            return FilterResult(None, confidence, "value out of range", False)

        dominant = dominant_colour(roi_image)
        if dominant != parameter.expected_colour:
            return FilterResult(None, confidence, "colour mismatch", False)

        previous = self.last_values.get(parameter.name)
        if previous is not None:
            delta = abs(value - previous)
            if delta > parameter.max_delta_per_sec:
                return FilterResult(None, confidence, "rate change exceeded", False)

        self.last_values[parameter.name] = value
        return FilterResult(value, confidence)
