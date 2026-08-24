"""Deterministic normalized OpenAPI contract diff calculation."""

from __future__ import annotations

from uuid import UUID

from application.fingerprinting import canonical_fingerprint
from domain.enums import OperationAuthorizationMode, SecurityChangeLevel

from .values import (
    ChangedAPIOperation,
    NormalizedAPIOperation,
    NormalizedAuthorizationPolicy,
    OpenAPIContractDiff,
)

_SECURITY_LEVEL_RANK = {
    SecurityChangeLevel.NONE: 0,
    SecurityChangeLevel.TIGHTENING: 1,
    SecurityChangeLevel.WEAKENING: 2,
    SecurityChangeLevel.BREAKING: 3,
}


class OpenAPIContractDiffCalculator:
    """Compare transport and exact authorization metadata by semantic operation ID."""

    def calculate(
        self,
        *,
        base_contract_id: UUID | None,
        candidate_contract_id: UUID,
        base_operations: list[NormalizedAPIOperation],
        candidate_operations: list[NormalizedAPIOperation],
    ) -> OpenAPIContractDiff:
        """Build sorted changes, aggregate security effect, and canonical diff hash."""
        base_by_id = {operation.api_operation_id: operation for operation in base_operations}
        candidate_by_id = {
            operation.api_operation_id: operation for operation in candidate_operations
        }
        added = [
            candidate_by_id[api_operation_id]
            for api_operation_id in sorted(candidate_by_id.keys() - base_by_id.keys())
        ]
        removed = [
            base_by_id[api_operation_id]
            for api_operation_id in sorted(base_by_id.keys() - candidate_by_id.keys())
        ]
        changed: list[ChangedAPIOperation] = []
        for api_operation_id in sorted(base_by_id.keys() & candidate_by_id.keys()):
            before = base_by_id[api_operation_id]
            after = candidate_by_id[api_operation_id]
            if before == after:
                continue
            level = self._classify_operation_change(before, after)
            changed.append(
                ChangedAPIOperation(
                    api_operation_id=api_operation_id,
                    before=before,
                    after=after,
                    security_change_level=level,
                )
            )

        levels = [change.security_change_level for change in changed]
        levels.extend(
            SecurityChangeLevel.WEAKENING
            if operation.authorization.mode is OperationAuthorizationMode.PUBLIC
            else SecurityChangeLevel.NONE
            for operation in added
        )
        levels.extend(SecurityChangeLevel.TIGHTENING for _operation in removed)
        security_level = max(
            levels,
            key=_SECURITY_LEVEL_RANK.__getitem__,
            default=SecurityChangeLevel.NONE,
        )
        requires_acknowledgement = security_level in (
            SecurityChangeLevel.WEAKENING,
            SecurityChangeLevel.BREAKING,
        )
        payload = self._canonical_payload(
            base_contract_id=base_contract_id,
            candidate_contract_id=candidate_contract_id,
            added=added,
            removed=removed,
            changed=changed,
            security_level=security_level,
            requires_acknowledgement=requires_acknowledgement,
        )
        return OpenAPIContractDiff(
            base_contract_id=base_contract_id,
            candidate_contract_id=candidate_contract_id,
            diff_hash=canonical_fingerprint(payload),
            added_operations=added,
            removed_operations=removed,
            changed_operations=changed,
            security_change_level=security_level,
            requires_security_acknowledgement=requires_acknowledgement,
        )

    def _classify_operation_change(
        self,
        before: NormalizedAPIOperation,
        after: NormalizedAPIOperation,
    ) -> SecurityChangeLevel:
        if before.http_method != after.http_method or before.path != after.path:
            return SecurityChangeLevel.BREAKING
        return self._classify_policy_change(before.authorization, after.authorization)

    def _classify_policy_change(
        self,
        before: NormalizedAuthorizationPolicy,
        after: NormalizedAuthorizationPolicy,
    ) -> SecurityChangeLevel:
        if before == after:
            return SecurityChangeLevel.NONE
        if before.mode is OperationAuthorizationMode.PUBLIC:
            return SecurityChangeLevel.TIGHTENING
        if after.mode is OperationAuthorizationMode.PUBLIC:
            return SecurityChangeLevel.WEAKENING
        if before.required_scope != after.required_scope:
            return SecurityChangeLevel.BREAKING
        return SecurityChangeLevel.BREAKING

    def _canonical_payload(
        self,
        *,
        base_contract_id: UUID | None,
        candidate_contract_id: UUID,
        added: list[NormalizedAPIOperation],
        removed: list[NormalizedAPIOperation],
        changed: list[ChangedAPIOperation],
        security_level: SecurityChangeLevel,
        requires_acknowledgement: bool,
    ) -> dict[str, object]:
        return {
            "baseContractId": str(base_contract_id) if base_contract_id is not None else None,
            "candidateContractId": str(candidate_contract_id),
            "addedOperations": [operation.canonical_payload() for operation in added],
            "removedOperations": [operation.canonical_payload() for operation in removed],
            "changedOperations": [
                {
                    "operationId": change.api_operation_id,
                    "before": change.before.canonical_payload(),
                    "after": change.after.canonical_payload(),
                    "securityChangeLevel": change.security_change_level.value,
                }
                for change in changed
            ],
            "securityChangeLevel": security_level.value,
            "requiresSecurityAcknowledgement": requires_acknowledgement,
        }
