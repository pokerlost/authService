"""One changed normalized OpenAPI operation."""

from __future__ import annotations

from domain.enums import SecurityChangeLevel
from domain.openapi_registry import NormalizedAPIOperation
from domain.types import APIOperationId
from domain.value_model import ValueModel


class ChangedAPIOperation(ValueModel):
    """Before and after metadata for one stable semantic operation ID."""

    api_operation_id: APIOperationId
    before: NormalizedAPIOperation
    after: NormalizedAPIOperation
    security_change_level: SecurityChangeLevel
