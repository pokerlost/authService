"""OAuth2 client identifier conflict failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .conflict import ConflictError


class OAuthClientConflictError(ConflictError):
    """An OAuth2 client identifier is already persisted."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_OAUTH_CLIENT_CONFLICT"
    public_message: ClassVar[str] = "OAuth2 client already exists."
