"""Lazy PokerLost OpenAPI contract generation."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

API_DESCRIPTION = (
    "PokerLost centralized identity, authentication, and coarse-grained authorization service."
)
OPENAPI_TAGS = [
    {"name": "health", "description": "Process and mandatory dependency health."},
    {"name": "users", "description": "Public ordinary-user account operations."},
    {"name": "jwks", "description": "Public signing-key set publication."},
]


class PokerLostAPI(FastAPI):
    """FastAPI with lazy cached PokerLost service metadata."""

    def openapi(self) -> dict[str, Any]:
        """Generate the OpenAPI contract only when first requested."""
        if self.openapi_schema is not None:
            return self.openapi_schema
        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
            tags=OPENAPI_TAGS,
        )
        schema["x-pokerlost-service"] = {"id": "authService"}
        self.openapi_schema = schema
        return schema
