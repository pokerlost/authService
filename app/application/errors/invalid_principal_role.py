"""Invalid authorization principal role failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .invalid_operation import InvalidOperationError


class InvalidPrincipalRoleError(InvalidOperationError):
    """Principal category and assigned role are incompatible."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_PRINCIPAL_ROLE"
    public_message: ClassVar[str] = "Authorization principal role is invalid."
