"""Kalman smoothing for accepted AVD values.

This module contains a lightweight one-dimensional Kalman smoother for the
values that pass plausibility checks.
"""

from __future__ import annotations

import numpy as np


class KalmanSmoother:
    """One-dimensional Kalman filter for smoothing accepted numeric readings."""

    def __init__(self, process_variance: float = 1e-2, measurement_variance: float = 1e-1) -> None:
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.posteri_estimate: float | None = None
        self.posteri_error_estimate = 1.0

    def smooth(self, measurement: float) -> float:
        if self.posteri_estimate is None:
            self.posteri_estimate = measurement
            return measurement

        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance
        kalman_gain = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + kalman_gain * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - kalman_gain) * priori_error_estimate
        return self.posteri_estimate
