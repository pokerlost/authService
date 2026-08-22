"""Transport-independent application error base."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base for expected application failures with safe public metadata."""

    error_code = "AUTH_APPLICATION_ERROR"
    public_message = "Application operation failed"
