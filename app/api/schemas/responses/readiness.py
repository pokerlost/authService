"""Readiness result schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReadinessDependencies(BaseModel):
    """Required runtime dependency states."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    postgresql: Literal["ready"] = Field(description="PostgreSQL readiness state.")


class ReadinessResult(BaseModel):
    """Aggregate runtime readiness result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["ready"] = Field(description="Aggregate service readiness state.")
    dependencies: ReadinessDependencies = Field(description="Required dependency states.")
