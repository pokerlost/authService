"""Canonical final OpenAPI authorization response schemas."""

from __future__ import annotations

from typing import Literal

from api.schemas.base import ResponseModel
from domain.types import APIOperationId


class PublicAuthorizationResponse(ResponseModel):
    """Explicit unauthenticated operation policy."""

    type: Literal["public"]


class OAuth2AuthorizationResponse(ResponseModel):
    """Exact canonical OAuth2 operation scope required by one RPC."""

    type: Literal["oauth2"]
    scope: APIOperationId


type AuthorizationResponse = PublicAuthorizationResponse | OAuth2AuthorizationResponse
