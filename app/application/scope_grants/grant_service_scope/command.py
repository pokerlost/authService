"""Service scope grant command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.types import APIOperationId, ServiceSlug
from domain.value_model import ValueModel


class GrantServiceScopeCommand(ValueModel):
    """Source service, resource audience, and exact operation scope grant."""

    service_slug: ServiceSlug
    audience: ServiceSlug
    scope: APIOperationId
    audit_context: AuditContext
