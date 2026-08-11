"""Tests for plausibility filtering in the AVD pipeline."""

from __future__ import annotations

import cv2
import numpy as np

from avd.filter.plausibility import PlausibilityFilter
from avd.store.models import ProfileParameter


def _dummy_roi(color: tuple[int, int, int]) -> "numpy.ndarray":
    roi = np.full((10, 10, 3), color, dtype=np.uint8)
    return roi


def test_filter_rejects_out_of_range() -> None:
    parameter = ProfileParameter(
        name="HR",
        roi=(0, 0, 10, 10),
        expected_colour="green",
        min=30.0,
        max=180.0,
        digits=3,
        max_delta_per_sec=20.0,
    )
    filter_engine = PlausibilityFilter()
    result = filter_engine.filter(parameter, 250.0, 0.8, _dummy_roi((0, 255, 0)), 0.0)
    assert result.value is None
    assert result.reason == "value out of range"


def test_filter_rejects_colour_mismatch() -> None:
    parameter = ProfileParameter(
        name="SpO2",
        roi=(0, 0, 10, 10),
        expected_colour="blue",
        min=70.0,
        max=100.0,
        digits=3,
        max_delta_per_sec=10.0,
    )
    filter_engine = PlausibilityFilter()
    result = filter_engine.filter(parameter, 95.0, 0.9, _dummy_roi((0, 255, 0)), 0.0)
    assert result.value is None
    assert result.reason == "colour mismatch"


def test_filter_rejects_rate_change() -> None:
    parameter = ProfileParameter(
        name="NIBP",
        roi=(0, 0, 10, 10),
        expected_colour="white",
        min=40.0,
        max=200.0,
        digits=3,
        max_delta_per_sec=5.0,
    )
    filter_engine = PlausibilityFilter()
    assert filter_engine.filter(parameter, 80.0, 0.8, _dummy_roi((255, 255, 255)), 0.0).value == 80.0
    result = filter_engine.filter(parameter, 92.0, 0.7, _dummy_roi((255, 255, 255)), 1.0)
    assert result.value is None
    assert result.reason == "rate change exceeded"
