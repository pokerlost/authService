"""SQLAlchemy database foundation facade."""

from __future__ import annotations

from .base import Base, UUIDModel
from .models import (
    ApiOperationModel,
    AuditEventModel,
    HumanAccountModel,
    OpenApiContractModel,
    OperationIdentityModel,
    PasswordCredentialModel,
    PrincipalModel,
    RefreshTokenModel,
    RegisteredServiceModel,
    RoleScopeGrantModel,
    SecurityRateLimitModel,
    ServiceAudienceGrantModel,
    ServiceCredentialModel,
    ServicePrincipalModel,
    ServiceScopeGrantModel,
    SessionModel,
    SessionScopeModel,
)
from .session import create_database_engine, create_session_factory

__all__ = (
    "ApiOperationModel",
    "AuditEventModel",
    "Base",
    "HumanAccountModel",
    "OpenApiContractModel",
    "OperationIdentityModel",
    "PasswordCredentialModel",
    "PrincipalModel",
    "RefreshTokenModel",
    "RegisteredServiceModel",
    "RoleScopeGrantModel",
    "SecurityRateLimitModel",
    "ServiceAudienceGrantModel",
    "ServiceCredentialModel",
    "ServicePrincipalModel",
    "ServiceScopeGrantModel",
    "SessionModel",
    "SessionScopeModel",
    "UUIDModel",
    "create_database_engine",
    "create_session_factory",
)
