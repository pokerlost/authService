"""Transport-independent application error facade."""

from __future__ import annotations

from .base import ApplicationError
from .conflict import ConflictError
from .integrity import IntegrityError
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
    "ConflictError",
    "IntegrityError",
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
