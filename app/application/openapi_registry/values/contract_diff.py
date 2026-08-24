"""Deterministic OpenAPI contract diff."""

from __future__ import annotations

from uuid import UUID

from domain.enums import SecurityChangeLevel
from domain.openapi_registry import NormalizedAPIOperation
from domain.value_model import ValueModel

from .changed_operation import ChangedAPIOperation


class OpenAPIContractDiff(ValueModel):
    """Candidate changes against the active contract of the same service."""

    base_contract_id: UUID | None
    candidate_contract_id: UUID
    diff_hash: str
    added_operations: list[NormalizedAPIOperation]
    removed_operations: list[NormalizedAPIOperation]
    changed_operations: list[ChangedAPIOperation]
    security_change_level: SecurityChangeLevel
    requires_security_acknowledgement: bool
