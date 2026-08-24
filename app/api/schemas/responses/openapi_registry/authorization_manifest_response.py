"""Authorization manifest response schema."""

from __future__ import annotations

from uuid import UUID

from api.schemas.base import ResponseModel
from domain.types import ContractVersion, ServiceId

from .api_operation_response import ApiOperationResponse


class AuthorizationManifestResponse(ResponseModel):
    """Normalized active control-plane manifest without raw OpenAPI JSON."""

    service_id: ServiceId
    contract_id: UUID
    contract_version: ContractVersion
    schema_hash: str
    operations: list[ApiOperationResponse]
