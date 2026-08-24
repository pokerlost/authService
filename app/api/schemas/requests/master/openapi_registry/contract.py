"""OpenAPI contract identity request."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import APIModel


class OpenAPIContractRequest(APIModel):
    """One persisted immutable OpenAPI contract identifier."""

    contract_id: UUID = Field(description="Persisted OpenAPI contract identifier.")
