"""Invalid authorization principal binding failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .invalid_operation import InvalidOperationError


class InvalidPrincipalBindingError(InvalidOperationError):
    """Principal category and cross-service binding are incompatible."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_PRINCIPAL_BINDING"
    public_message: ClassVar[str] = "Authorization principal binding is invalid."
