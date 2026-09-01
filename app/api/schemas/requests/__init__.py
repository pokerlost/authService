"""Public API request schema facade."""

from __future__ import annotations

from api.schemas.base import RequestModel

from .oauth_token_request import OAuthTokenRequest

__all__ = ("OAuthTokenRequest", "RequestModel")
