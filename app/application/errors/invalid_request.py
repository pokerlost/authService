"""Invalid application request category."""

from __future__ import annotations

from typing import ClassVar

from service import SERVICE_ERROR_PREFIX

from .base import ApplicationError


class InvalidRequestError(ApplicationError):
    """Validated transport input is invalid for the requested application operation."""

    error_code: ClassVar[str] = f"{SERVICE_ERROR_PREFIX}_INVALID_REQUEST"
    public_message: ClassVar[str] = "The request is invalid."
