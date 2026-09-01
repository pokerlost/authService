"""Authorization principal aggregate."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, model_validator
from pydantic_core import PydanticCustomError
from pypokerlost.types import (
    AuthorizationRole,
    PrincipalStatus,
    PrincipalType,
)

from domain.value_model import ValueModel


class AuthorizationPrincipal(ValueModel):
    """Human or service authorization identity with one compatible role."""

    principal_id: UUID
    principal_type: PrincipalType
    role: AuthorizationRole
    status: PrincipalStatus
    account_id: UUID | None
    service_slug: str | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @model_validator(mode="after")
    def validate_invariants(self) -> Self:
        """Enforce binding XOR and exact role compatibility."""
        if self.principal_type is PrincipalType.HUMAN:
            if self.account_id is None or self.service_slug is not None:
                raise PydanticCustomError(
                    "invalid_principal_binding",
                    "Human principal requires only an account binding",
                )
            if self.role not in (
                AuthorizationRole.USER,
                AuthorizationRole.SUPPORT,
                AuthorizationRole.MASTER,
            ):
                raise PydanticCustomError(
                    "invalid_principal_role",
                    "Human principal requires a human role",
                )
            return self

        if (
            self.account_id is not None
            or self.service_slug is None
            or not self.service_slug.strip()
        ):
            raise PydanticCustomError(
                "invalid_principal_binding",
                "Service principal requires only a non-empty service binding",
            )
        if self.role is not AuthorizationRole.AUTO:
            raise PydanticCustomError(
                "invalid_principal_role",
                "Service principal requires the auto role",
            )
        return self

    @classmethod
    def create_human(
        cls,
        *,
        principal_id: UUID,
        account_id: UUID,
        role: AuthorizationRole,
        now: datetime,
    ) -> Self:
        """Create an active human principal with one explicit human role."""
        return cls(
            principal_id=principal_id,
            principal_type=PrincipalType.HUMAN,
            role=role,
            status=PrincipalStatus.ACTIVE,
            account_id=account_id,
            service_slug=None,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_service(
        cls,
        *,
        principal_id: UUID,
        service_slug: str,
        now: datetime,
    ) -> Self:
        """Create an active service principal with the only compatible role."""
        return cls(
            principal_id=principal_id,
            principal_type=PrincipalType.SERVICE,
            role=AuthorizationRole.AUTO,
            status=PrincipalStatus.ACTIVE,
            account_id=None,
            service_slug=service_slug,
            created_at=now,
            updated_at=now,
        )

    def set_status(self, status: PrincipalStatus, *, now: datetime) -> Self:
        """Return the aggregate with an explicit active or disabled status."""
        return self.__class__(
            principal_id=self.principal_id,
            principal_type=self.principal_type,
            role=self.role,
            status=status,
            account_id=self.account_id,
            service_slug=self.service_slug,
            created_at=self.created_at,
            updated_at=now,
        )

    def assign_human_role(self, role: AuthorizationRole, *, now: datetime) -> Self:
        """Return a human principal with one newly assigned explicit role."""
        if self.principal_type is not PrincipalType.HUMAN:
            raise PydanticCustomError(
                "invalid_principal_role",
                "Only human principals can be assigned a human role",
            )
        return self.__class__(
            principal_id=self.principal_id,
            principal_type=self.principal_type,
            role=role,
            status=self.status,
            account_id=self.account_id,
            service_slug=self.service_slug,
            created_at=self.created_at,
            updated_at=now,
        )
