"""Registered service page response schema."""

from __future__ import annotations

from api.schemas.base import ResponseModel
from domain.types import ServiceId

from .registered_service_response import RegisteredServiceResponse


class RegisteredServicesPageResponse(ResponseModel):
    """Bounded deterministic service list and optional keyset cursor."""

    items: list[RegisteredServiceResponse]
    next_cursor: ServiceId | None
