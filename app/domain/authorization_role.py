"""Persisted authorization role domain value."""

from __future__ import annotations

from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, model_validator
from pydantic_core import PydanticCustomError

from domain.enums import PrincipalType, RoleCode
from domain.value_model import ValueModel


class AuthorizationRole(ValueModel):
    """One exact role and its compatible principal category."""

    role_id: UUID
    code: RoleCode
    principal_type: PrincipalType
    created_at: AwareDatetime
    updated_at: AwareDatetime

    @model_validator(mode="after")
    def validate_compatibility(self) -> Self:
        """Require the fixed human/service role compatibility matrix."""
        human_role = self.code in (RoleCode.USER, RoleCode.SUPPORT, RoleCode.MASTER)
        if (self.principal_type is PrincipalType.HUMAN and human_role) or (
            self.principal_type is PrincipalType.SERVICE and self.code is RoleCode.AUTO
        ):
            return self
        raise PydanticCustomError(
            "invalid_principal_role",
            "Authorization role is incompatible with its principal type",
        )
