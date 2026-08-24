"""List OpenAPI contracts query."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from domain.types import ServiceId
from domain.value_model import ValueModel


class ListOpenAPIContractsQuery(ValueModel):
    """Bounded UUID-keyset contract page for one exact registered service."""

    service_id: ServiceId
    limit: int = Field(ge=1, le=100)
    after_contract_id: UUID | None = None
