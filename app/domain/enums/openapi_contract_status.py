"""OpenAPI contract lifecycle status."""

from __future__ import annotations

from enum import StrEnum


class OpenAPIContractStatus(StrEnum):
    """Persisted immutable contract lifecycle state."""

    REGISTERED = "registered"
    VALIDATED = "validated"
    ACTIVE = "active"
    RETIRED = "retired"
