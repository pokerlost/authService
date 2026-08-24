"""Bounded canonical OAuth2 scope parsing and serialization."""

from __future__ import annotations

from domain.types import validate_api_operation_id


class OAuthScopeParser:
    """Normalize space-delimited canonical operation scopes under production limits."""

    __slots__ = ("_max_scope_count", "_max_scope_token_length", "_max_total_bytes")

    def __init__(
        self,
        *,
        max_scope_count: int,
        max_scope_token_length: int,
        max_total_bytes: int,
    ) -> None:
        self._max_scope_count = max_scope_count
        self._max_scope_token_length = max_scope_token_length
        self._max_total_bytes = max_total_bytes

    def parse_requested(self, value: str | None) -> frozenset[str]:
        """Parse an optional OAuth2 request scope string."""
        if value is None:
            return frozenset()
        return self._parse(value)

    def parse_claim(self, value: object) -> frozenset[str]:
        """Parse a required JWT scope claim without coercion."""
        if not isinstance(value, str):
            raise ValueError("JWT scope claim must be a string")
        return self._parse(value)

    def serialize(self, scopes: frozenset[str]) -> str:
        """Return a deterministic bounded space-delimited scope claim."""
        value = " ".join(sorted(scopes))
        parsed = self._parse(value)
        if parsed != scopes:
            raise ValueError("OAuth2 scopes are not canonical operation IDs")
        return value

    def _parse(self, value: str) -> frozenset[str]:
        if len(value.encode("utf-8")) > self._max_total_bytes:
            raise ValueError("OAuth2 scope value exceeds the byte limit")
        tokens = value.split()
        if len(tokens) > self._max_scope_count:
            raise ValueError("OAuth2 scope count exceeds the limit")
        scopes: set[str] = set()
        for token in tokens:
            if len(token) > self._max_scope_token_length:
                raise ValueError("OAuth2 scope token exceeds the length limit")
            scopes.add(validate_api_operation_id(token))
        return frozenset(scopes)
