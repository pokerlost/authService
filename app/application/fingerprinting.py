"""Deterministic semantic payload fingerprints."""

from __future__ import annotations

import hashlib
import json


def canonical_fingerprint(payload: dict[str, object]) -> str:
    """Return a stable SHA-256 digest of a canonical semantic payload."""
    canonical_payload = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return hashlib.sha256(canonical_payload).hexdigest()
