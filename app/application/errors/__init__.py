"""Transport-independent application error facade."""

from __future__ import annotations

from .access_token_expired import AccessTokenExpiredError
from .authentication_required import AuthenticationRequiredError
from .base import ApplicationError
from .conflict import ConflictError
from .insufficient_scope import InsufficientScopeError
from .integrity import IntegrityError
from .invalid_access_token import InvalidAccessTokenError
from .invalid_operation import InvalidOperationError
from .invalid_principal_binding import InvalidPrincipalBindingError
from .invalid_request import InvalidRequestError
from .invalid_scope_name import InvalidScopeNameError
from .not_found import NotFoundError
from .oauth_client_conflict import OAuthClientConflictError
from .principal_conflict import PrincipalConflictError
from .scope_not_found import ScopeNotFoundError
from .temporarily_unavailable import TemporarilyUnavailableError

__all__ = (
    "AccessTokenExpiredError",
    "ApplicationError",
    "AuthenticationRequiredError",
    "ConflictError",
    "InsufficientScopeError",
    "IntegrityError",
    "InvalidAccessTokenError",
    "InvalidOperationError",
    "InvalidPrincipalBindingError",
    "InvalidRequestError",
    "InvalidScopeNameError",
    "NotFoundError",
    "OAuthClientConflictError",
    "PrincipalConflictError",
    "ScopeNotFoundError",
    "TemporarilyUnavailableError",
)
