"""Normalized operation authorization read projection."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from domain.enums import OperationAuthorizationMode
from domain.types import APIOperationId
from domain.value_model import ValueModel


class OperationAuthorizationProjection(ValueModel):
    """One contract operation with its final public or OAuth2 policy."""

    api_operation_row_id: UUID
    api_operation_id: APIOperationId
    http_method: Literal["GET", "POST"]
    path: str
    mode: OperationAuthorizationMode
    required_scope: APIOperationId | None
