"""Registration facade for concrete SQLAlchemy models."""

from __future__ import annotations

from .authorization_principal_model import AuthorizationPrincipalModel
from .authorization_role_model import AuthorizationRoleModel
from .oauth_client_audience_grant_model import OAuthClientAudienceGrantModel
from .oauth_client_grant_type_model import OAuthClientGrantTypeModel
from .oauth_client_model import OAuthClientModel
from .oauth_client_scope_grant_model import OAuthClientScopeGrantModel
from .oauth_client_secret_model import OAuthClientSecretModel
from .oauth_scope_model import OAuthScopeModel
from .role_scope_grant_model import RoleScopeGrantModel
from .service_audience_grant_model import ServiceAudienceGrantModel
from .service_scope_grant_model import ServiceScopeGrantModel

__all__ = (
    "AuthorizationPrincipalModel",
    "AuthorizationRoleModel",
    "OAuthClientAudienceGrantModel",
    "OAuthClientGrantTypeModel",
    "OAuthClientModel",
    "OAuthClientScopeGrantModel",
    "OAuthClientSecretModel",
    "OAuthScopeModel",
    "RoleScopeGrantModel",
    "ServiceAudienceGrantModel",
    "ServiceScopeGrantModel",
)
