"""Create AUTO service credential command."""

from __future__ import annotations

from application.audit import AuditContext
from domain.types import ServiceSlug
from domain.value_model import ValueModel


class CreateServiceCredentialCommand(ValueModel):
    """Service identity receiving a new independently revocable credential."""

    service_slug: ServiceSlug
    audit_context: AuditContext
