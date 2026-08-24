"""Secret-safe issued human session tokens."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class IssuedSessionTokens:
    """One access and refresh credential pair."""

    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    scopes: frozenset[str]
