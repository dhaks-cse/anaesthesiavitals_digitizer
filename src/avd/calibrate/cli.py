"""Calibration CLI for building monitor profiles from a source stream."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
from pydantic import ValidationError

from ..capture.source import ImageDirSource, VideoSource, WebcamSource
from ..store.models import MonitorProfile, ProfileParameter
from ..vision.rectify import rectify_screen


def _make_source(source: str, path: str | None) -> WebcamSource | VideoSource | ImageDirSource:
    if source == "cam":
        return WebcamSource(index=0, target_fps=1.0)
    if source == "video":
        if path is None:
            raise ValueError("--path is required for video source")
        return VideoSource(path=path, target_fps=1.0)
    if source == "images":
        if path is None:
            raise ValueError("--path is required for images source")
        return ImageDirSource(directory=path, target_fps=1.0)
    raise ValueError("source must be one of cam, video, images")


def calibrate_profile(source: str, path: str | None, out: str) -> None:
    source_obj = _make_source(source, path)
    frame_count = 0
    parameters: list[ProfileParameter] = []
    selected_rect: tuple[int, int, int, int] | None = None

    for _, frame in source_obj.frames():
        frame_count += 1
        if frame_count > 1:
            break

        rectified, _ = rectify_screen(frame, 1280, 720)
        clone = rectified.copy()
        rects: list[tuple[int, int, int, int]] = []

        def on_mouse(event: int, x: int, y: int, flags: int, _param: Any) -> None:
            nonlocal selected_rect, clone
            if event == cv2.EVENT_LBUTTONDOWN:
                selected_rect = (x, y, 0, 0)
            elif event == cv2.EVENT_MOUSEMOVE and selected_rect is not None:
                x0, y0, _, _ = selected_rect
                selected_rect = (x0, y0, x - x0, y - y0)
                clone = rectified.copy()
                cv2.rectangle(clone, (x0, y0), (x, y), (0, 255, 0), 2)
            elif event == cv2.EVENT_LBUTTONUP and selected_rect is not None:
                x0, y0, x1, y1 = selected_rect[0], selected_rect[1], x, y
                selected_rect = None
                w = abs(x1 - x0)
                h = abs(y1 - y0)
                rects.append((min(x0, x1), min(y0, y1), w, h))

        cv2.namedWindow("Calibrate")
        cv2.setMouseCallback("Calibrate", on_mouse)

        while True:
            cv2.imshow("Calibrate", clone)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("n"):
                if selected_rect is not None:
                    x, y, w, h = selected_rect
                    if w > 0 and h > 0:
                        rects.append((x, y, w, h))
                        selected_rect = None
                if len(rects) >= 1:
                    break

        cv2.destroyAllWindows()

    if not rects:
        raise RuntimeError("No ROIs selected during calibration")

    for idx, roi in enumerate(rects, start=1):
        print(f"Define parameter {idx}")
        name = input("Name: ").strip()
        expected_colour = input("Expected colour (red/green/blue/white): ").strip().lower()
        minimum = float(input("Minimum value: ").strip())
        maximum = float(input("Maximum value: ").strip())
        digits = int(input("Digits: ").strip())
        max_delta_per_sec = float(input("Max delta per second: ").strip())
        parameters.append(
            ProfileParameter(
                name=name,
                roi=roi,
                expected_colour=expected_colour,
                min=minimum,
                max=maximum,
                digits=digits,
                max_delta_per_sec=max_delta_per_sec,
            )
        )

    profile = MonitorProfile(
        name=Path(out).stem,
        canonical_width=1280,
        canonical_height=720,
        parameters=parameters,
    )
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(profile.model_dump_json(indent=2))
    print(f"Wrote profile to {out}")
