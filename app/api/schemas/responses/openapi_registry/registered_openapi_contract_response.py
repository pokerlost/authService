"""Registered OpenAPI contract response schema."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from api.schemas.base import ResponseModel
from domain.enums import OpenAPIContractStatus
from domain.types import ContractVersion, ServiceId


class RegisteredOpenApiContractResponse(ResponseModel):
    """Registration summary without the submitted JSON document."""

    contract_id: UUID
    service_id: ServiceId
    contract_version: ContractVersion
    schema_hash: str
    status: OpenAPIContractStatus
    created_at: datetime
