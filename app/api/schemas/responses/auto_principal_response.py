"""Master-created AUTO principal response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.types import ServiceSlug


class AutoPrincipalResponse(ResponseModel):
    """AUTO principal identifier and canonical source service slug."""

    principal_id: UUID
    service_slug: ServiceSlug
    created_at: datetime
