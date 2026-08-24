"""OpenAPI contract lifecycle summary."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.enums import OpenAPIContractStatus
from domain.types import ContractVersion, ServiceId
from domain.value_model import ValueModel


class OpenAPIContractSummary(ValueModel):
    """Safe immutable identity and mutable lifecycle timestamps without raw JSON."""

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
