"""SQLite database helper for AVD local storage.

This module provides a simple SQLAlchemy-backed database helper for creating
and using the local storage tables for cases, readings, and profiles.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base, Case, Reading


class Database:
    """Local SQLite database manager for AVD."""

    def __init__(self, path: str = "avd.sqlite") -> None:
        self.path = Path(path)
        self.engine = create_engine(f"sqlite:///{self.path}", future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, future=True)
        Base.metadata.create_all(self.engine)

    def create_case(self, description: str | None = None) -> Case:
        with self.SessionLocal() as session:
            case = Case(started_at=datetime.utcnow(), description=description)
            session.add(case)
            session.commit()
            session.refresh(case)
            return case

    def add_reading(
        self,
        case_id: int,
        timestamp: datetime,
        parameter: str,
        value: float,
        confidence: float,
        verified: bool,
    ) -> Reading:
        with self.SessionLocal() as session:
            reading = Reading(
                case_id=case_id,
                timestamp=timestamp,
                parameter=parameter,
                value=value,
                confidence=confidence,
                verified=verified,
            )
            session.add(reading)
            session.commit()
            session.refresh(reading)
            return reading

    def get_readings_for_case(self, case_id: int) -> list[Reading]:
        with self.SessionLocal() as session:
            return session.query(Reading).filter_by(case_id=case_id).all()
