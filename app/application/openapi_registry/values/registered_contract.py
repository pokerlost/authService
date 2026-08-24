"""Registered OpenAPI contract summary result."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from domain.enums import OpenAPIContractStatus
from domain.types import ContractVersion, ServiceId
from domain.value_model import ValueModel


class RegisteredOpenAPIContract(ValueModel):
    """Registration response without echoing the immutable JSON document."""

    contract_id: UUID
    service_id: ServiceId
    contract_version: ContractVersion
    schema_hash: str
    status: OpenAPIContractStatus
    created_at: datetime
