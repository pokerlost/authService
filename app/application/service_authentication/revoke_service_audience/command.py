"""Revoke AUTO service audience command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.types import ServiceSlug
from domain.value_model import ValueModel


class RevokeServiceAudienceCommand(ValueModel):
    """Explicit source service and target audience selected for revocation."""

    service_slug: ServiceSlug
    audience: ServiceSlug
    audit_context: AuditContext
