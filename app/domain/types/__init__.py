"""Semantic validated type facade."""

from __future__ import annotations

from .email_address import EmailAddress
from .password_value import PasswordValue

__all__ = ("EmailAddress", "PasswordValue")
