"""Focused application port facade."""

from __future__ import annotations

from .authorization_principal_repository import AuthorizationPrincipalRepository
from .client_credentials_query import (
    ClientCredentialsAuthorizationContext,
    ClientCredentialsQuery,
)
from .handler import Handler
from .oauth_client_repository import OAuthClientRepository
from .oauth_client_secret_processor import (
    GeneratedOAuthClientSecret,
    OAuthClientSecretProcessor,
)
from .role_scope_query import RoleScopeQuery
from .service_access_token_signer import ServiceAccessTokenSigner

__all__ = (
    "AuthorizationPrincipalRepository",
    "ClientCredentialsAuthorizationContext",
    "ClientCredentialsQuery",
    "GeneratedOAuthClientSecret",
    "Handler",
    "OAuthClientRepository",
    "OAuthClientSecretProcessor",
    "RoleScopeQuery",
    "ServiceAccessTokenSigner",
)
