"""Human account control-plane not-found error."""

from __future__ import annotations

from application.errors.not_found import NotFoundError


class HumanAccountNotFound(NotFoundError):
    """Target is absent or is not a human principal."""

    error_code = "AUTH_HUMAN_ACCOUNT_NOT_FOUND"
    public_message = "Human account not found."
