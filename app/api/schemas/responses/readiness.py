"""Readiness result schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel


class ReadinessDependencies(ResponseModel):
    """Required runtime dependency states."""

    postgresql: Literal["ready"] = Field(description="PostgreSQL readiness state.")


class ReadinessResult(ResponseModel):
    """Aggregate runtime readiness result."""

    status: Literal["ready"] = Field(description="Aggregate service readiness state.")
    dependencies: ReadinessDependencies = Field(description="Required dependency states.")
