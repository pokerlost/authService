"""Application error category facade."""

from __future__ import annotations

from .accounts import SelfPasswordResetForbidden
from .authentication import (
    AuthenticationError,
    CurrentPasswordInvalidError,
    InvalidAccessToken,
    InvalidCredentials,
    InvalidOAuthClient,
    InvalidOAuthGrant,
    InvalidOAuthScope,
    InvalidRefreshToken,
    UnsupportedOAuthGrantType,
)
from .base import ApplicationError
from .conflict import ConflictError
from .forbidden import ForbiddenError
from .insufficient_scope import InsufficientScopeError
from .integrity import IntegrityError
from .invalid_operation import InvalidOperationError
from .not_found import NotFoundError
from .openapi_registry import (
    OpenAPIContractActivationConflictError,
    OpenAPIContractNotFoundError,
    OpenAPIContractNotValidatedError,
    OpenAPIContractRegistrationInvalidError,
    OpenAPIContractSecurityAcknowledgementRequiredError,
    OpenAPIContractVersionConflictError,
    OpenAPIOperationIDConflictError,
    RegisteredServiceNotFoundError,
)
from .rate_limited import RateLimitedError
from .scope_grant_invalid import ScopeGrantInvalidError
from .service_authentication import (
    InvalidServiceCredentials,
    ServiceCredentialNotFound,
    ServicePrincipalAlreadyExists,
    ServicePrincipalNotFound,
)
from .sessions import SessionNotFound

__all__ = (
    "ApplicationError",
    "AuthenticationError",
    "ConflictError",
    "CurrentPasswordInvalidError",
    "ForbiddenError",
    "InsufficientScopeError",
    "IntegrityError",
    "InvalidAccessToken",
    "InvalidCredentials",
    "InvalidOAuthClient",
    "InvalidOAuthGrant",
    "InvalidOAuthScope",
    "InvalidOperationError",
    "InvalidRefreshToken",
    "InvalidServiceCredentials",
    "NotFoundError",
    "OpenAPIContractActivationConflictError",
    "OpenAPIContractNotFoundError",
    "OpenAPIContractNotValidatedError",
    "OpenAPIContractRegistrationInvalidError",
    "OpenAPIContractSecurityAcknowledgementRequiredError",
    "OpenAPIContractVersionConflictError",
    "OpenAPIOperationIDConflictError",
    "RateLimitedError",
    "RegisteredServiceNotFoundError",
    "ScopeGrantInvalidError",
    "SelfPasswordResetForbidden",
    "ServiceCredentialNotFound",
    "ServicePrincipalAlreadyExists",
    "ServicePrincipalNotFound",
    "SessionNotFound",
    "UnsupportedOAuthGrantType",
)
