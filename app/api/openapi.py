"""Lazy PokerLost OpenAPI contract generation."""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Any, Final

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from domain.authservice_scopes import (
    AUTH_SERVICE_OPERATION_IDS,
    AUTH_SERVICE_PROTECTED_SCOPE_IDS,
    AUTH_SERVICE_PUBLIC_OPERATION_IDS,
)

API_DESCRIPTION = (
    "PokerLost centralized identity, authentication, and coarse-grained authorization service."
)


class OpenAPITag(StrEnum):
    """Transport-level OpenAPI route categories."""

    SERVICE = "service"
    JWKS = "jwks"
    USERS = "users"
    AUTH = "auth"
    SESSIONS = "sessions"
    OAUTH = "oauth"
    ACCOUNT = "account"
    OPENAPI = "openapi"
    MASTER = "master"
    SUPPORT = "support"


OPENAPI_TAGS = [
    {"name": OpenAPITag.SERVICE, "description": "Parameterless service operations."},
    {"name": OpenAPITag.JWKS, "description": "Public signing-key set publication."},
    {"name": OpenAPITag.USERS, "description": "Human account registration operations."},
    {"name": OpenAPITag.AUTH, "description": "Human authentication operations."},
    {
        "name": OpenAPITag.SESSIONS,
        "description": "Authenticated human session-management operations.",
    },
    {
        "name": OpenAPITag.OAUTH,
        "description": "Unified OAuth2 token grant operation.",
    },
    {"name": OpenAPITag.ACCOUNT, "description": "Authenticated account operations."},
    {"name": OpenAPITag.OPENAPI, "description": "Public JSON OpenAPI contract publication."},
    {
        "name": OpenAPITag.MASTER,
        "description": "Scope-protected identity and authorization control-plane operations.",
    },
    {
        "name": OpenAPITag.SUPPORT,
        "description": "Dedicated support-safe ordinary-user inspection operations.",
    },
]

_HTTP_OPERATION_METHODS = frozenset({"get", "post"})
_RPC_PATH_PATTERN: Final = re.compile(
    r"^/(?P<namespace>[a-z][A-Za-z0-9]*)\.(?P<method>[a-z][A-Za-z0-9]*)$"
)


def _validate_rpc_contract(path: str, method: str, operation: dict[str, Any]) -> None:
    """Require the sole root exception or one matching RPC path and operation ID."""
    operation_id = operation.get("operationId")
    if path == "/":
        if method != "get" or operation_id != "authService.root":
            raise RuntimeError("OpenAPI service root contract is invalid")
        return

    match = _RPC_PATH_PATTERN.fullmatch(path)
    if match is None:
        raise RuntimeError("OpenAPI operation path does not follow the RPC convention")
    expected_operation_id = f"authService.{match.group('namespace')}.{match.group('method')}"
    if operation_id != expected_operation_id:
        raise RuntimeError("OpenAPI operation ID does not match its RPC path")


def _validate_authorization_contract(schema: dict[str, Any]) -> None:
    """Require final explicit public or exact canonical OAuth2 operation security."""
    components = schema.get("components")
    if not isinstance(components, dict):
        raise RuntimeError("OpenAPI components are missing")
    security_schemes = components.get("securitySchemes")
    if not isinstance(security_schemes, dict):
        raise RuntimeError("OpenAPI security schemes are missing")
    oauth2 = security_schemes.get("OAuth2")
    if not isinstance(oauth2, dict) or oauth2.get("type") != "oauth2":
        raise RuntimeError("Canonical OAuth2 security scheme is invalid")
    flows = oauth2.get("flows")
    if not isinstance(flows, dict) or not {"password", "clientCredentials"}.issubset(flows):
        raise RuntimeError("Canonical OAuth2 flows are missing")
    paths = schema.get("paths")
    if not isinstance(paths, dict):
        raise RuntimeError("OpenAPI paths are missing")

    for path, path_item in paths.items():
        if not isinstance(path, str):
            raise RuntimeError("OpenAPI path is malformed")
        if not isinstance(path_item, dict):
            raise RuntimeError("OpenAPI path item is malformed")
        for method, operation in path_item.items():
            if method not in _HTTP_OPERATION_METHODS:
                continue
            if not isinstance(operation, dict):
                raise RuntimeError("OpenAPI operation is malformed")
            _validate_rpc_contract(path, method, operation)
            if "x-pokerlost-authz" in operation:
                raise RuntimeError("Legacy authorization metadata is forbidden")
            operation_id = operation.get("operationId")
            if operation_id not in AUTH_SERVICE_OPERATION_IDS:
                raise RuntimeError("Unknown authService operation ID")
            security = operation.get("security")
            if operation_id in AUTH_SERVICE_PUBLIC_OPERATION_IDS:
                if security != []:
                    raise RuntimeError("Public OpenAPI operation security is not empty")
                continue
            if operation_id not in AUTH_SERVICE_PROTECTED_SCOPE_IDS or security != [
                {"OAuth2": [operation_id]}
            ]:
                raise RuntimeError("Protected OpenAPI operation scope is invalid")


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
        paths = schema.get("paths")
        if isinstance(paths, dict):
            for path_item in paths.values():
                if not isinstance(path_item, dict):
                    continue
                for method, operation in path_item.items():
                    if method not in _HTTP_OPERATION_METHODS or not isinstance(operation, dict):
                        continue
                    if operation.get("operationId") in AUTH_SERVICE_PUBLIC_OPERATION_IDS:
                        operation["security"] = []
        components = schema.get("components")
        if isinstance(components, dict):
            security_schemes = components.get("securitySchemes")
            if isinstance(security_schemes, dict):
                security_schemes.pop("OAuth2ClientAuthentication", None)
        schema["x-pokerlost-service"] = {"id": "authService"}
        _validate_authorization_contract(schema)
        self.openapi_schema = schema
        return schema
