"""Tests for storage round-trip in the AVD pipeline."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from avd.store.db import Database


def test_database_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "test_avd.sqlite"
    database = Database(path=str(db_path))
    case = database.create_case(description="Unit test case")
    reading = database.add_reading(
        case_id=case.id,
        timestamp=datetime.utcnow(),
        parameter="HR",
        value=75.0,
        confidence=0.85,
        verified=False,
    )
    readings = database.get_readings_for_case(case.id)
    assert len(readings) == 1
    assert readings[0].parameter == "HR"
    assert readings[0].value == 75.0
    assert readings[0].verified is False
