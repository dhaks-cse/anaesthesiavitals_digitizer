"""Digit recognition abstractions and implementations for AVD.

This module defines a Recognizer protocol and concrete recognizers for ONNX
models and a stub implementation for development and testing.
"""

from __future__ import annotations

from abc import ABC
from typing import Protocol, Tuple

import cv2
import numpy as np
import onnxruntime as ort


class Recognizer(Protocol):
    """Recognizes numeric readings from ROI image crops."""

    def recognize(self, roi: "cv2.Mat", digits: int) -> Tuple[float | None, float]:
        """Return detected value and confidence."""


class OnnxDigitRecognizer(ABC):
    """ONNX-backed digit recognizer."""

    def __init__(self, model_path: str) -> None:
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    def _preprocess(self, roi: "cv2.Mat") -> np.ndarray:
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        resized = cv2.resize(thresh, (128, 64), interpolation=cv2.INTER_AREA)
        normalized = resized.astype("float32") / 255.0
        return normalized[np.newaxis, np.newaxis, :, :]

    def recognize(self, roi: "cv2.Mat", digits: int) -> Tuple[float | None, float]:
        input_tensor = self._preprocess(roi)
        outputs = self.session.run(None, {self.session.get_inputs()[0].name: input_tensor})
        logits = np.asarray(outputs[0]).squeeze()
        if logits.ndim != 1:
            return None, 0.0
        value = float(np.argmax(logits))
        confidence = float(np.max(logits))
        return value, confidence


class StubDigitRecognizer:
    """Stub recognizer that returns a fixed value and confidence."""

    def __init__(self, value: float = 42.0, confidence: float = 0.7) -> None:
        self.value = value
        self.confidence = confidence

    def recognize(self, roi: "cv2.Mat", digits: int) -> Tuple[float, float]:
        return self.value, self.confidence
