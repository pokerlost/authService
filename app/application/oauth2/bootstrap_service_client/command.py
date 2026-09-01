"""Bootstrap-service-client application command."""

from __future__ import annotations

from typing import Self
from uuid import UUID

from pydantic import field_validator, model_validator
from pypokerlost.types import OAuthScope

from application import Command
from domain.resource_indicator import ResourceIndicator


class BootstrapServiceClientCommand(Command):
    """Exact operator input for one new service principal and client."""

    service_slug: str
    client_id: UUID | None = None
    scopes: tuple[OAuthScope, ...]
    resources: tuple[ResourceIndicator, ...]

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
            raise ValueError("At least one OAuth2 scope is required")
        if len(frozenset(self.scopes)) != len(self.scopes):
            raise ValueError("Duplicate OAuth2 scopes are not allowed")
        if not self.resources:
            raise ValueError("At least one resource indicator is required")
        if len({resource.value for resource in self.resources}) != len(self.resources):
            raise ValueError("Duplicate resource indicators are not allowed")
        return self
