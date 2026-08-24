"""Registered service identity request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import ServiceId


class RegisteredServiceRequest(APIModel):
    """Exact case-sensitive PokerLost platform service identifier."""

    service_id: ServiceId = Field(description="Canonical registered PokerLost service ID.")
