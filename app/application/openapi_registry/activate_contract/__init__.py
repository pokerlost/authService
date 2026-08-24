"""Activate OpenAPI contract operation facade."""

from __future__ import annotations

from .command import ActivateOpenAPIContractCommand
from .handler import ActivateOpenAPIContractHandler

__all__ = (
    "ActivateOpenAPIContractCommand",
    "ActivateOpenAPIContractHandler",
)
