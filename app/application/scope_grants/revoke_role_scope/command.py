"""Role scope revocation command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.enums import Role
from domain.types import APIOperationId
from domain.value_model import ValueModel


class RevokeRoleScopeCommand(ValueModel):
    """One exact human role and canonical operation scope revocation."""

    role: Role
    scope: APIOperationId
    audit_context: AuditContext
