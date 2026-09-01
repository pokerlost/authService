"""Service access-token signing port."""

from __future__ import annotations

from typing import Protocol

from pypokerlost.types import PokerlostAccessTokenClaims


class ServiceAccessTokenSigner(Protocol):
    """Sign validated shared access-token claims without exposing key material."""

    def sign(self, claims: PokerlostAccessTokenClaims) -> str:
        """Return one compact signed JWT."""
        ...
