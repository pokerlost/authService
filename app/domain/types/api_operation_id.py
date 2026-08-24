"""Stable semantic OpenAPI operation identifier."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import BeforeValidator

_API_OPERATION_ID_PATTERN: Final = re.compile(
    r"[a-z][A-Za-z0-9]{1,62}(?:\.[a-z][A-Za-z0-9]{0,62}){1,2}\Z"
)


def validate_api_operation_id(value: object) -> str:
    """Require a bounded dotted ASCII semantic operation identifier."""
    if not isinstance(value, str) or _API_OPERATION_ID_PATTERN.fullmatch(value) is None:
        raise ValueError("API operation ID must be a bounded dotted ASCII identifier")
    return value


type APIOperationId = Annotated[str, BeforeValidator(validate_api_operation_id)]
