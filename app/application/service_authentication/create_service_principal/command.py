"""Create AUTO service principal command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.types import ServiceSlug
from domain.value_model import ValueModel


class CreateServicePrincipalCommand(ValueModel):
    """Canonical service identity requested by an operator."""

    service_slug: ServiceSlug
    audit_context: AuditContext
