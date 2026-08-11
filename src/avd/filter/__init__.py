"""Plausibility filter and state-tracking utilities for vitals readings.

This package checks each reading against parameter bounds, dominant colour, and
rate-of-change limits, then applies a Kalman smoother over accepted values.
"""

from .plausibility import PlausibilityFilter, FilterResult
from .kalman import KalmanSmoother

__all__ = ["PlausibilityFilter", "FilterResult", "KalmanSmoother"]
