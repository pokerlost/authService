"""Authorization principal binding conflict."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .conflict import ConflictError


class PrincipalConflictError(ConflictError):
    """A human account or service slug is already bound to a principal."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_PRINCIPAL_CONFLICT"
    public_message: ClassVar[str] = "Authorization principal binding already exists."
