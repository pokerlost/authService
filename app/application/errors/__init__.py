"""Transport-independent application error facade."""

from __future__ import annotations

from .authentication_required import AuthenticationRequiredError
from .base import ApplicationError
from .conflict import ConflictError
from .insufficient_scope import InsufficientScopeError
from .integrity import IntegrityError
from .invalid_access_token import InvalidAccessTokenError
from .invalid_operation import InvalidOperationError
from .invalid_principal_binding import InvalidPrincipalBindingError
from .invalid_principal_role import InvalidPrincipalRoleError
from .invalid_scope_name import InvalidScopeNameError
from .not_found import NotFoundError
from .oauth_client_conflict import OAuthClientConflictError
from .principal_conflict import PrincipalConflictError
from .role_not_found import RoleNotFoundError
from .scope_not_found import ScopeNotFoundError

__all__ = (
    "ApplicationError",
    "AuthenticationRequiredError",
    "ConflictError",
    "InsufficientScopeError",
    "IntegrityError",
    "InvalidAccessTokenError",
    "InvalidOperationError",
    "InvalidPrincipalBindingError",
    "InvalidPrincipalRoleError",
    "InvalidScopeNameError",
    "NotFoundError",
    "OAuthClientConflictError",
    "PrincipalConflictError",
    "RoleNotFoundError",
    "ScopeNotFoundError",
)
