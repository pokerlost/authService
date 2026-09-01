"""Focused authService security adapter facade."""

from __future__ import annotations

from .oauth_client_secret_processor import SHA256OAuthClientSecretProcessor
from .service_access_token_signer import PyJWTServiceAccessTokenSigner

__all__ = (
    "PyJWTServiceAccessTokenSigner",
    "SHA256OAuthClientSecretProcessor",
)
