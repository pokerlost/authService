"""Safe request and actor context for durable security audit."""

from __future__ import annotations

from uuid import UUID

from domain.enums import Role
from domain.types import APIOperationId
from domain.value_model import ValueModel


class AuditContext(ValueModel):
    """Non-secret actor and request identifiers attached to a security mutation."""

    request_id: str | None = None
    correlation_id: str | None = None
    api_operation_id: APIOperationId | None = None
    actor_principal_id: UUID | None = None
    actor_role: Role | None = None
