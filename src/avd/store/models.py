"""SQLAlchemy models for local AVD storage.

This module defines tables for case metadata, timestamped readings, and saved
monitor profiles.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, conint, confloat, constr
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    parameter: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    canonical_width: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_height: Mapped[int] = mapped_column(Integer, nullable=False)
    definition: Mapped[str] = mapped_column(Text, nullable=False)


class ProfileParameter(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    roi: tuple[conint(ge=0), conint(ge=0), conint(gt=0), conint(gt=0)]
    expected_colour: constr(strip_whitespace=True, min_length=1)
    min: confloat(ge=0.0)
    max: confloat(gt=0.0)
    digits: conint(gt=0)
    max_delta_per_sec: confloat(ge=0.0)


class MonitorProfile(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    canonical_width: conint(gt=0)
    canonical_height: conint(gt=0)
    parameters: list[ProfileParameter] = Field(min_length=1)
