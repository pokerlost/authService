"""List registered services query."""

from __future__ import annotations

from pydantic import Field

from domain.types import ServiceId
from domain.value_model import ValueModel


class ListRegisteredServicesQuery(ValueModel):
    """Bounded service-ID keyset pagination input."""

    limit: int = Field(ge=1, le=100)
    after_service_id: ServiceId | None = None
