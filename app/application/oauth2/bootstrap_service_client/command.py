"""Bootstrap-service-client application command."""

from __future__ import annotations

from typing import Self
from uuid import UUID

from pydantic import field_validator, model_validator
from pypokerlost.enums import PokerlostScopes
from pypokerlost.types import PokerlostAudience

from application import Command


class BootstrapServiceClientCommand(Command):
    """Exact operator input for one new service principal and client."""

    service_slug: str
    client_id: UUID | None = None
    scopes: tuple[PokerlostScopes, ...]
    audiences: tuple[PokerlostAudience, ...]

    @field_validator("service_slug")
    @classmethod
    def validate_service_slug(cls, value: str) -> str:
        """Require a non-empty exact service binding without normalization."""
        if not value.strip():
            raise ValueError("Service slug must not be empty")
        return value

    @model_validator(mode="after")
    def validate_grants(self) -> Self:
        """Require non-empty, duplicate-free exact grant collections."""
        if not self.scopes:
            raise ValueError("At least one Pokerlost scope is required")
        if len(frozenset(self.scopes)) != len(self.scopes):
            raise ValueError("Duplicate Pokerlost scopes are not allowed")
        if not self.audiences:
            raise ValueError("At least one audience is required")
        if len(frozenset(self.audiences)) != len(self.audiences):
            raise ValueError("Duplicate audiences are not allowed")
        return self
