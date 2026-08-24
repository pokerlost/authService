"""OpenAPI contract summary response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.enums import OpenAPIContractStatus
from domain.types import ContractVersion, ServiceId


class OpenApiContractSummaryResponse(ResponseModel):
    """Immutable contract identity and mutable lifecycle metadata without JSON."""

    contract_id: UUID
    service_id: ServiceId
    contract_version: ContractVersion
    openapi_version: str
    schema_hash: str
    status: OpenAPIContractStatus
    validated_at: datetime | None
    activated_at: datetime | None
    retired_at: datetime | None
    created_at: datetime
    updated_at: datetime
