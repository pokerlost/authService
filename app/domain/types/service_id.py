"""Canonical PokerLost platform service identifier."""

from __future__ import annotations

import re
from typing import Annotated, Final

from pydantic import BeforeValidator

_SERVICE_ID_PATTERN: Final = re.compile(r"[a-z][A-Za-z0-9]{1,62}\Z")


def validate_service_id(value: object) -> str:
    """Require a bounded case-sensitive ASCII PokerLost service name."""
    if not isinstance(value, str) or _SERVICE_ID_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "Service ID must contain 2 to 63 ASCII letters or digits and start lowercase"
        )
    return value


type ServiceId = Annotated[str, BeforeValidator(validate_service_id)]
