"""Support-safe ordinary-user account query."""

from __future__ import annotations

from domain.types import Username
from domain.value_model import ValueModel


class GetUserAccountQuery(ValueModel):
    """Canonical login identity of an ordinary user to inspect safely."""

    username: Username
