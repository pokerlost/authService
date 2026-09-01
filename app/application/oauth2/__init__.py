"""OAuth client application operations and protocol-safe failures."""

from __future__ import annotations

from .errors import GetTokenError, GetTokenErrorCode

__all__ = ("GetTokenError", "GetTokenErrorCode")
