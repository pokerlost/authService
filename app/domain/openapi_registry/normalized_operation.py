"""Normalized executable OpenAPI operation."""

from __future__ import annotations

from typing import Literal

from domain.types import APIOperationId
from domain.value_model import ValueModel

from .normalized_authorization import NormalizedAuthorizationPolicy


class NormalizedAPIOperation(ValueModel):
    """Stable semantic identity plus transport and authorization metadata."""

    api_operation_id: APIOperationId
    http_method: Literal["GET", "POST"]
    path: str
    authorization: NormalizedAuthorizationPolicy

    def canonical_payload(self) -> dict[str, object]:
        """Return deterministic operation metadata for hashing and manifests."""
        return {
            "operationId": self.api_operation_id,
            "method": self.http_method,
            "path": self.path,
            "authorization": self.authorization.canonical_payload(),
        }
