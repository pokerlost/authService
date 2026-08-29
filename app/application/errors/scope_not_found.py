"""OAuth2 scope lookup failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .not_found import NotFoundError


class ScopeNotFoundError(NotFoundError):
    """At least one requested OAuth2 scope does not exist."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_SCOPE_NOT_FOUND"
    public_message: ClassVar[str] = "OAuth2 scope was not found."
