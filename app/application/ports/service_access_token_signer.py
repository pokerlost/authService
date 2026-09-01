"""Service access-token signing port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, field_validator, model_validator
from pydantic_core import PydanticCustomError

from domain.enums import PrincipalType, RoleCode
from domain.resource_indicator import ResourceIndicator
from domain.scope_name import ScopeName
from domain.value_model import ValueModel


class ServiceAccessTokenClaims(ValueModel):
    """Exact application-owned claims for a short-lived service token."""

    issuer: str
    subject: UUID
    audience: ResourceIndicator
    issued_at: AwareDatetime
    not_before: AwareDatetime
    expires_at: AwareDatetime
    token_id: UUID
    client_id: UUID
    scope: str
    principal_type: PrincipalType
    role: RoleCode
    service_slug: str

    @field_validator("issuer")
    @classmethod
    def validate_issuer(cls, issuer: str) -> str:
        """Keep a non-empty issuer exact rather than normalizing it."""
        if not issuer.strip() or issuer != issuer.strip():
            raise ValueError("Token issuer must be non-empty and must not contain outer whitespace")
        return issuer

    @field_validator("service_slug")
    @classmethod
    def validate_service_slug(cls, service_slug: str) -> str:
        """Reject an empty service binding without changing it."""
        if not service_slug.strip():
            raise ValueError("Service slug must not be empty")
        return service_slug

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, scope: str) -> str:
        """Require a non-empty, duplicate-free, sorted canonical scope string."""
        tokens = scope.split(" ")
        if not scope or any(not token for token in tokens):
            raise PydanticCustomError(
                "invalid_service_token_scope",
                "Service token scope must not be empty",
            )
        parsed_tokens = tuple(ScopeName.parse(token).value for token in tokens)
        if len(frozenset(parsed_tokens)) != len(parsed_tokens) or tuple(sorted(parsed_tokens)) != (
            parsed_tokens
        ):
            raise PydanticCustomError(
                "invalid_service_token_scope",
                "Service token scopes must be unique and sorted",
            )
        return scope

    @model_validator(mode="after")
    def validate_service_claims(self) -> Self:
        """Enforce temporal and service-identity claim invariants."""
        if self.not_before > self.issued_at:
            raise PydanticCustomError(
                "invalid_service_token_time",
                "Token not-before time cannot follow issuance time",
            )
        if self.expires_at <= self.issued_at:
            raise PydanticCustomError(
                "invalid_service_token_time",
                "Token expiry must follow issuance time",
            )
        if self.subject == self.client_id:
            raise PydanticCustomError(
                "invalid_service_token_identity",
                "Service principal and OAuth2 client identifiers must differ",
            )
        if self.principal_type is not PrincipalType.SERVICE or self.role is not RoleCode.AUTO:
            raise PydanticCustomError(
                "invalid_service_token_principal",
                "Service token requires a service principal with the auto role",
            )
        return self


class ServiceAccessTokenSigner(ABC):
    """Sign exact service claims without exposing key material."""

    @abstractmethod
    def sign(self, claims: ServiceAccessTokenClaims) -> str:
        """Return one compact signed JWT."""
        raise NotImplementedError
