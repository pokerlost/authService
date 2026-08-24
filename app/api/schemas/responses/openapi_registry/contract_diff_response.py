"""OpenAPI contract diff response schemas."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.enums import SecurityChangeLevel
from domain.types import APIOperationId

from .api_operation_response import ApiOperationResponse


class ChangedApiOperationResponse(ResponseModel):
    """Before and after metadata for one stable semantic operation."""

    operation_id: APIOperationId = Field(alias="operationId")
    before: ApiOperationResponse
    after: ApiOperationResponse
    security_change_level: SecurityChangeLevel


class ContractDiffResponse(ResponseModel):
    """Deterministic candidate diff and security acknowledgement metadata."""

    base_contract_id: UUID | None
    candidate_contract_id: UUID
    diff_hash: str
    added_operations: list[ApiOperationResponse]
    removed_operations: list[ApiOperationResponse]
    changed_operations: list[ChangedApiOperationResponse]
    security_change_level: SecurityChangeLevel
    requires_security_acknowledgement: bool
