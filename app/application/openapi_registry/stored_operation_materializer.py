"""Materialize normalized operations from persistence projections."""

from __future__ import annotations

from application.errors import IntegrityError
from persistence.projections import OperationAuthorizationProjection

from .values import NormalizedAPIOperation, NormalizedAuthorizationPolicy


def materialize_stored_operations(
    rows: list[OperationAuthorizationProjection],
) -> list[NormalizedAPIOperation]:
    """Reassert the normalized public versus OAuth2 authorization invariants."""
    try:
        operations = [
            NormalizedAPIOperation(
                api_operation_id=row.api_operation_id,
                http_method=row.http_method,
                path=row.path,
                authorization=NormalizedAuthorizationPolicy(
                    mode=row.mode,
                    required_scope=row.required_scope,
                ),
            )
            for row in rows
        ]
    except ValueError as exception:
        raise IntegrityError from exception
    operations.sort(key=lambda operation: operation.api_operation_id)
    return operations
