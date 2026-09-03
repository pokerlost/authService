"""Persisted authorization scope definition domain value."""

from __future__ import annotations

from uuid import UUID

from pydantic import AwareDatetime, field_validator
from pypokerlost.enums import PokerlostScopes

from domain.value_model import ValueModel


class ScopeDefinition(ValueModel):
    """One stable scope catalog entry."""

    scope_id: UUID
    name: PokerlostScopes
    description: str
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("description")
    @classmethod
    def validate_description(cls, description: str) -> str:
        """Reject an empty or whitespace-only catalog description."""
        if not description.strip():
            raise ValueError("Scope description must not be empty")
        return description
