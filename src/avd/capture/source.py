"""Abstract frame streaming sources for AVD input.

This module defines a common interface for time-aligned frame capture from a
webcam index, a video file, or an image directory.
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Sequence, Tuple

import cv2

FrameItem = Tuple[float, "cv2.Mat"]


class FrameSource(ABC):
    """Frame source interface yielding timestamped OpenCV frames."""

    def __init__(self, target_fps: float = 1.0) -> None:
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps

    @abstractmethod
    def frames(self) -> Iterator[FrameItem]:
        """Yield (timestamp, frame) pairs."""


class WebcamSource(FrameSource):
    """Capture frames from a webcam at a fixed target rate."""

    def __init__(self, index: int = 0, target_fps: float = 1.0) -> None:
        super().__init__(target_fps=target_fps)
        self.index = index

    def frames(self) -> Iterator[FrameItem]:
        capture = cv2.VideoCapture(self.index)
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open webcam index {self.index}")

        last_emit = 0.0
        while True:
            success, frame = capture.read()
            if not success:
                break
            now = time.time()
            if now - last_emit < self.frame_interval:
                continue
            last_emit = now
            yield now, frame

        capture.release()


class VideoSource(FrameSource):
    """Capture frames from a video file at a fixed target rate."""

    def __init__(self, path: str, target_fps: float = 1.0) -> None:
        super().__init__(target_fps=target_fps)
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Video file does not exist: {self.path}")

    def frames(self) -> Iterator[FrameItem]:
        capture = cv2.VideoCapture(str(self.path))
        if not capture.isOpened():
            raise RuntimeError(f"Unable to open video file {self.path}")

        last_emit = 0.0
        while True:
            success, frame = capture.read()
            if not success:
                break
            now = time.time()
            if now - last_emit < self.frame_interval:
                continue
            last_emit = now
            yield now, frame

        capture.release()


class ImageDirSource(FrameSource):
    """Capture frames from an image directory at a fixed target rate."""

    def __init__(self, directory: str, target_fps: float = 1.0) -> None:
        super().__init__(target_fps=target_fps)
        self.directory = Path(directory)
        if not self.directory.is_dir():
            raise FileNotFoundError(f"Image directory does not exist: {self.directory}")
        self.files = sorted(
            [p for p in self.directory.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}]
        )

    def frames(self) -> Iterator[FrameItem]:
        last_emit = 0.0
        for file_path in self.files:
            frame = cv2.imread(str(file_path))
            if frame is None:
                continue
            now = time.time()
            if now - last_emit < self.frame_interval:
                time.sleep(self.frame_interval - (now - last_emit))
                now = time.time()
            last_emit = now
            yield now, frame
