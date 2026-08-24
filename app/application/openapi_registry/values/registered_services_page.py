"""Bounded registered-service keyset page."""

from __future__ import annotations

from domain.types import ServiceId
from domain.value_model import ValueModel

from .registered_service_summary import RegisteredServiceSummary


class RegisteredServicesPage(ValueModel):
    """One deterministic page and the next service-ID cursor when present."""

    items: list[RegisteredServiceSummary]
    next_cursor: ServiceId | None
