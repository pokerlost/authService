"""Transport-independent application error base."""

from __future__ import annotations

from typing import ClassVar


class ApplicationError(Exception):
    """Base for expected application failures with safe public metadata."""

    error_code: ClassVar[str] = "AUTH_APPLICATION_ERROR"
    public_message: ClassVar[str] = "Application operation failed."
