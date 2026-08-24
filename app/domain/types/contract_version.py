"""Bounded OpenAPI info.version value."""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator


def validate_contract_version(value: object) -> str:
    """Require a non-empty bounded printable ASCII contract version."""
    if not isinstance(value, str) or not 1 <= len(value) <= 64:
        raise ValueError("Contract version must contain 1 to 64 characters")
    if value != value.strip() or not value.isascii() or not value.isprintable():
        raise ValueError("Contract version must be canonical printable ASCII")
    return value


type ContractVersion = Annotated[str, BeforeValidator(validate_contract_version)]
