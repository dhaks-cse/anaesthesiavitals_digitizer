"""Top-level CLI for running and calibrating the Smart Anaesthesia Vitals Digitizer."""

from __future__ import annotations

from pathlib import Path

import cv2
import typer

from .capture.source import ImageDirSource, VideoSource, WebcamSource
from .calibrate.cli import calibrate_profile
from datetime import datetime
from .store.db import Database
from .store.models import MonitorProfile
from .vision import crop_roi, rectify_screen, StubDigitRecognizer
from .filter.plausibility import PlausibilityFilter

app = typer.Typer()


def _make_source(source: str, path: str | None) -> WebcamSource | VideoSource | ImageDirSource:
    if source == "cam":
        return WebcamSource(index=0, target_fps=1.0)
    if source == "video":
        if path is None:
            raise typer.BadParameter("--path is required for video source")
        return VideoSource(path=path, target_fps=1.0)
    if source == "images":
        if path is None:
            raise typer.BadParameter("--path is required for images source")
        return ImageDirSource(directory=path, target_fps=1.0)
    raise typer.BadParameter("source must be one of cam, video, images")


@app.command()
def calibrate(source: str = typer.Option("video", help="Source type: video or cam."), path: str | None = typer.Option(None, help="Path for video or image source."), out: str = typer.Option("profiles/example_monitor.json", help="Destination profile JSON.")) -> None:
    calibrate_profile(source, path, out)


@app.command()
def run(source: str = typer.Option("cam", help="Source type: cam, video, or images."), path: str | None = typer.Option(None, help="Path for video or image source."), profile: str = typer.Option(..., help="Monitor profile JSON path."), db_path: str = typer.Option("avd.sqlite", help="SQLite database path.")) -> None:
    profile_data = MonitorProfile.model_validate_json(Path(profile).read_text())
    source_obj = _make_source(source, path)
    database = Database(path=db_path)
    case = database.create_case(description=f"Run with profile {profile_data.name}")

    recognizer = StubDigitRecognizer()
    filter_engine = PlausibilityFilter()

    print(f"Starting run with profile {profile_data.name}")
    while True:
        try:
            timestamp, frame = next(source_obj.frames())
        except StopIteration:
            break

        rectified, confidence = rectify_screen(frame, profile_data.canonical_width, profile_data.canonical_height)
        if confidence < 0.1:
            print("Warning: poor rectification confidence, using raw frame")

        print(f"Timestamp: {timestamp:.2f} rect_conf={confidence:.2f}")
        for parameter in profile_data.parameters:
            roi_image = crop_roi(rectified, parameter.roi)
            value, recog_conf = recognizer.recognize(roi_image, parameter.digits)
            if value is None:
                continue
            result = filter_engine.filter(parameter, value, recog_conf, roi_image, timestamp)
            if result.value is not None:
                database.add_reading(
                    case_id=case.id,
                    timestamp=datetime.utcfromtimestamp(timestamp),
                    parameter=parameter.name,
                    value=result.value,
                    confidence=result.confidence,
                    verified=result.verified,
                )
                print(f"{parameter.name}: {result.value:.1f} conf={result.confidence:.2f} verified={result.verified}")
            else:
                print(f"{parameter.name}: rejected ({result.reason}) conf={result.confidence:.2f}")

            cv2.imshow("Rectified", rectified)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    app()
