"""Normalized OpenAPI operation response schema."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from api.schemas.base import ResponseModel
from domain.types import APIOperationId

from .authorization_response import AuthorizationResponse


class ApiOperationResponse(ResponseModel):
    """Semantic identity, transport metadata, and canonical authorization."""

    operation_id: APIOperationId = Field(alias="operationId")
    method: Literal["GET", "POST"]
    path: str
    authorization: AuthorizationResponse
