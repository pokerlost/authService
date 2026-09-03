"""Registration facade for concrete SQLAlchemy models."""

from __future__ import annotations

from .authorization_principal_model import AuthorizationPrincipalModel
from .client_audience_grant_model import ClientAudienceGrantModel
from .client_credential_model import ClientCredentialModel
from .client_scope_grant_model import ClientScopeGrantModel
from .oauth_client_grant_type_model import OAuthClientGrantTypeModel
from .oauth_client_model import OAuthClientModel
from .principal_audience_grant_model import PrincipalAudienceGrantModel
from .principal_scope_grant_model import PrincipalScopeGrantModel
from .scope_definition_model import ScopeDefinitionModel

__all__ = (
    "AuthorizationPrincipalModel",
    "ClientAudienceGrantModel",
    "ClientCredentialModel",
    "ClientScopeGrantModel",
    "OAuthClientGrantTypeModel",
    "OAuthClientModel",
    "PrincipalAudienceGrantModel",
    "PrincipalScopeGrantModel",
    "ScopeDefinitionModel",
)
