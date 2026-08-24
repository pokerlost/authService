"""Master control-plane request facade."""

from __future__ import annotations

from .account_status import AccountStatusRequest
from .audit_events import ListAuditEventsRequest
from .create_staff_account import CreateStaffAccountRequest
from .openapi_registry import (
    ActivateOpenAPIContractRequest,
    ListOpenAPIContractsRequest,
    OpenAPIContractRequest,
    RegisteredServiceRequest,
    RegisterOpenAPIContractRequest,
)
from .reset_human_password import ResetHumanPasswordRequest
from .scope_grant import ListServiceScopesRequest, RoleScopeRequest, ServiceScopeRequest
from .service_audience import ServiceAudienceRequest
from .service_credential import ServiceCredentialRequest
from .service_identity import ServiceIdentityRequest

__all__ = (
    "AccountStatusRequest",
    "ActivateOpenAPIContractRequest",
    "CreateStaffAccountRequest",
    "ListAuditEventsRequest",
    "ListOpenAPIContractsRequest",
    "ListServiceScopesRequest",
    "OpenAPIContractRequest",
    "RegisterOpenAPIContractRequest",
    "RegisteredServiceRequest",
    "ResetHumanPasswordRequest",
    "RoleScopeRequest",
    "ServiceAudienceRequest",
    "ServiceCredentialRequest",
    "ServiceIdentityRequest",
    "ServiceScopeRequest",
)
