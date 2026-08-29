"""Authorization role lookup failure."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .not_found import NotFoundError


class RoleNotFoundError(NotFoundError):
    """Requested persisted authorization role does not exist."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_ROLE_NOT_FOUND"
    public_message: ClassVar[str] = "Authorization role was not found."
