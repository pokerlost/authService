"""Public request schema facade."""

from __future__ import annotations

from .account import ChangePasswordRequest
from .master import (
    AccountStatusRequest,
    ActivateOpenAPIContractRequest,
    CreateStaffAccountRequest,
    ListAuditEventsRequest,
    ListOpenAPIContractsRequest,
    ListServiceScopesRequest,
    OpenAPIContractRequest,
    RegisteredServiceRequest,
    RegisterOpenAPIContractRequest,
    ResetHumanPasswordRequest,
    RoleScopeRequest,
    ServiceAudienceRequest,
    ServiceCredentialRequest,
    ServiceIdentityRequest,
    ServiceScopeRequest,
)
from .oauth import OAuthTokenRequest
from .sessions import RevokeSessionRequest
from .support import GetUserAccountRequest
from .users import RegisterUserRequest

__all__ = (
    "AccountStatusRequest",
    "ActivateOpenAPIContractRequest",
    "ChangePasswordRequest",
    "CreateStaffAccountRequest",
    "GetUserAccountRequest",
    "ListAuditEventsRequest",
    "ListOpenAPIContractsRequest",
    "ListServiceScopesRequest",
    "OAuthTokenRequest",
    "OpenAPIContractRequest",
    "RegisterOpenAPIContractRequest",
    "RegisterUserRequest",
    "RegisteredServiceRequest",
    "ResetHumanPasswordRequest",
    "RevokeSessionRequest",
    "RoleScopeRequest",
    "ServiceAudienceRequest",
    "ServiceCredentialRequest",
    "ServiceIdentityRequest",
    "ServiceScopeRequest",
)
