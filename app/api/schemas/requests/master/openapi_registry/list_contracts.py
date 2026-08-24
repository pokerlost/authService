"""OpenAPI contract list request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel
from application.openapi_registry import ListOpenAPIContractsQuery
from domain.types import ServiceId


class ListOpenAPIContractsRequest(APIModel):
    """Bounded UUID-keyset page for one registered service."""

    service_id: ServiceId = Field(description="Canonical registered PokerLost service ID.")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum contracts to return.")
    after_contract_id: UUID | None = Field(
        default=None,
        description="Exclusive contract UUID keyset cursor.",
    )

    def to_query(self) -> ListOpenAPIContractsQuery:
        """Map bounded transport pagination to the read query."""
        return ListOpenAPIContractsQuery(
            service_id=self.service_id,
            limit=self.limit,
            after_contract_id=self.after_contract_id,
        )
