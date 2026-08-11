"""Frame source abstractions for video, webcam, and image directory input.

This module exposes capture backends that yield timestamped frames at a
configurable target rate while dropping frames if input is too fast.
"""

from .source import FrameSource, WebcamSource, VideoSource, ImageDirSource

__all__ = ["FrameSource", "WebcamSource", "VideoSource", "ImageDirSource"]
