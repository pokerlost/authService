"""Normalized operation authorization policy."""

from __future__ import annotations

from typing import Self

from pydantic import model_validator

from domain.enums import OperationAuthorizationMode
from domain.types import APIOperationId
from domain.value_model import ValueModel


class NormalizedAuthorizationPolicy(ValueModel):
    """Exactly one fail-closed public or canonical OAuth2 scope policy."""

    mode: OperationAuthorizationMode
    required_scope: APIOperationId | None = None

    @model_validator(mode="after")
    def validate_variant(self) -> Self:
        """Enforce the public versus exact-scope truth table."""
        if self.mode is OperationAuthorizationMode.PUBLIC:
            valid = self.required_scope is None
        else:
            valid = self.required_scope is not None
        if not valid:
            raise ValueError("Normalized authorization policy variant is inconsistent")
        return self

    def canonical_payload(self) -> dict[str, object]:
        """Return the deterministic public policy representation."""
        if self.mode is OperationAuthorizationMode.PUBLIC:
            return {"type": "public"}
        if self.required_scope is None:
            raise ValueError("OAuth2 policy is missing its required scope")
        return {
            "type": "oauth2",
            "scope": self.required_scope,
        }
