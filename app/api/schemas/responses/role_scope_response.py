"""Explicit human role scope grant responses."""

from __future__ import annotations

from datetime import datetime

from api.schemas.base import ResponseModel
from domain.enums import Role
from domain.types import APIOperationId


class RoleScopeGrantResponse(ResponseModel):
    """One persisted direct human role scope grant."""

    role: Role
    scope: APIOperationId
    created_at: datetime


class RoleScopesResponse(ResponseModel):
    """Bounded deterministic list of direct human role scope grants."""

    items: list[RoleScopeGrantResponse]
