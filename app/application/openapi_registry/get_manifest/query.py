"""Get active authorization manifest query."""

from __future__ import annotations

from domain.types import ServiceId
from domain.value_model import ValueModel


class GetAuthorizationManifestQuery(ValueModel):
    """Exact registered service whose active control-plane manifest is requested."""

    service_id: ServiceId
