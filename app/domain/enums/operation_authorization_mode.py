"""Normalized OpenAPI operation authorization mode."""

from __future__ import annotations

from enum import StrEnum


class OperationAuthorizationMode(StrEnum):
    """Final public or exact OAuth2 scope authorization mode."""

    PUBLIC = "public"
    OAUTH2 = "oauth2"
