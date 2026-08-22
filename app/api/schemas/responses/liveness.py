"""Liveness result schema."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel


class LivenessResult(ResponseModel):
    """Process liveness result."""

    status: Literal["healthy"] = Field(description="Current process liveness state.")
