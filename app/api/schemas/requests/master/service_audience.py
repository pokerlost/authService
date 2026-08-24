"""Master AUTO audience grant request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import ServiceSlug


class ServiceAudienceRequest(APIModel):
    """Exact source service and target audience grant identity."""

    service_slug: ServiceSlug = Field(description="Canonical source SERVICE_SLUG.")
    audience: ServiceSlug = Field(description="Canonical target SERVICE_SLUG audience.")
