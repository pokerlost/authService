"""Public request model configuration."""

from __future__ import annotations

from pydantic import ConfigDict

from .api_model import APIModel


class RequestModel(APIModel):
    """Immutable public JSON request model."""

    model_config = ConfigDict(frozen=True)
