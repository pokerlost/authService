"""Typed OpenAPI registry read-projection facade."""

from __future__ import annotations

from .active_scope import ActiveScopeProjection
from .openapi_contract_list_item import OpenAPIContractListItemProjection
from .operation_authorization import OperationAuthorizationProjection
from .registered_service_list_item import RegisteredServiceListItemProjection
from .security_rate_limit_key import SecurityRateLimitKeyProjection

__all__ = (
    "ActiveScopeProjection",
    "OpenAPIContractListItemProjection",
    "OperationAuthorizationProjection",
    "RegisteredServiceListItemProjection",
    "SecurityRateLimitKeyProjection",
)
