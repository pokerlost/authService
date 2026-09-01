"""Persisted OAuth2 scope catalog domain value."""

from __future__ import annotations

from uuid import UUID

from pydantic import AwareDatetime, field_validator
from pypokerlost.types import PokerlostScope

from domain.value_model import ValueModel


class OAuthScopeDefinition(ValueModel):
    """One persisted OAuth2 scope catalog entry."""

    scope_id: UUID
    name: PokerlostScope
    description: str
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @field_validator("description")
    @classmethod
    def validate_description(cls, description: str) -> str:
        """Reject an empty or whitespace-only catalog description."""
        if not description.strip():
            raise ValueError("OAuth2 scope description must not be empty")
        return description
