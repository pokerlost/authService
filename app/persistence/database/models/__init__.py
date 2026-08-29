"""Registration facade for concrete SQLAlchemy models."""

from __future__ import annotations

from .authorization_principal_model import AuthorizationPrincipalModel
from .authorization_role_model import AuthorizationRoleModel
from .oauth_scope_model import OAuthScopeModel
from .role_scope_grant_model import RoleScopeGrantModel

__all__ = (
    "AuthorizationPrincipalModel",
    "AuthorizationRoleModel",
    "OAuthScopeModel",
    "RoleScopeGrantModel",
)
