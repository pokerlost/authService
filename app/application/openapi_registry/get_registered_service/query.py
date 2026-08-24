"""Get registered service query."""

from __future__ import annotations

from domain.types import ServiceId
from domain.value_model import ValueModel


class GetRegisteredServiceQuery(ValueModel):
    """Exact case-sensitive PokerLost service registry identity."""

    service_id: ServiceId
