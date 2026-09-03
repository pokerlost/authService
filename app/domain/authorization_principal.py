"""Authorization principal aggregate."""

from __future__ import annotations

from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, model_validator
from pydantic_core import PydanticCustomError
from pypokerlost.enums import PrincipalStatus, PrincipalType

from domain.value_model import ValueModel


class AuthorizationPrincipal(ValueModel):
    """Human or service authorization identity without role-derived authority."""

    principal_id: UUID
    principal_type: PrincipalType
    status: PrincipalStatus
    account_id: UUID | None
    service_slug: str | None
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @model_validator(mode="after")
    def validate_invariants(self) -> Self:
        """Enforce the exact human/service binding shape."""
        if self.principal_type is PrincipalType.HUMAN:
            if self.account_id is None or self.service_slug is not None:
                raise PydanticCustomError(
                    "invalid_principal_binding",
                    "Human principal requires only an account binding",
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
        return self

    @classmethod
    def create_human(
        cls,
        *,
        principal_id: UUID,
        account_id: UUID,
        now: datetime,
    ) -> Self:
        """Create an active human principal with no implicit authority."""
        return cls(
            principal_id=principal_id,
            principal_type=PrincipalType.HUMAN,
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
        """Create an active service principal with no implicit authority."""
        return cls(
            principal_id=principal_id,
            principal_type=PrincipalType.SERVICE,
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
            status=status,
            account_id=self.account_id,
            service_slug=self.service_slug,
            created_at=self.created_at,
            updated_at=now,
        )
