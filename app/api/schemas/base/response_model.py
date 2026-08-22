"""Public response model configuration."""

from __future__ import annotations

from pydantic import ConfigDict

from .api_model import APIModel


class ResponseModel(APIModel):
    """Immutable public response model."""

    model_config = ConfigDict(frozen=True)
