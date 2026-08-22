"""Liveness result schema."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LivenessResult(BaseModel):
    """Process liveness result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["healthy"] = Field(description="Current process liveness state.")
