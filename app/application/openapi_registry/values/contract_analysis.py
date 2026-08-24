"""OpenAPI parsing and validation analysis."""

from __future__ import annotations

from domain.openapi_registry import NormalizedAPIOperation
from domain.value_model import ValueModel

from .validation_result import OpenAPIContractValidationResult


class OpenAPIContractAnalysis(ValueModel):
    """Bounded identity facts, normalized operations, and validation report."""

    service_id: str | None
    contract_version: str | None
    openapi_version: str | None
    document_size_bytes: int | None
    operations: list[NormalizedAPIOperation]
    validation: OpenAPIContractValidationResult
