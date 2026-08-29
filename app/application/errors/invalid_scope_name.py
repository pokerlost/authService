"""Invalid OAuth2 scope name failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .invalid_operation import InvalidOperationError


class InvalidScopeNameError(InvalidOperationError):
    """OAuth2 scope identifier does not satisfy the stable format."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_SCOPE_NAME"
    public_message: ClassVar[str] = "OAuth2 scope name is invalid."
