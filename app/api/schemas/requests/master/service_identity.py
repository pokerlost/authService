"""Master AUTO service identity request."""

from __future__ import annotations

from pydantic import Field

from api.schemas.base import APIModel
from domain.types import ServiceSlug


class ServiceIdentityRequest(APIModel):
    """Canonical AUTO source service selected for management."""

    service_slug: ServiceSlug = Field(description="Canonical source SERVICE_SLUG.")
