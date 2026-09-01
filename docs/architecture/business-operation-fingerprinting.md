# Business-operation fingerprinting

This page defines the shared keyed fingerprint primitive used by authService and the boundary that
future concrete idempotent operations must complete.

## Canonical primitive

`application/idempotency/business_operation_fingerprinting.py` provides
`BusinessOperationFingerprinter`, `BusinessOperationFingerprint`, and `FingerprintComparison`.
The fingerprinter computes a deterministic HMAC-SHA-256 digest using a dedicated versioned secret,
a versioned domain separator, sorted field names, and length-prefixed names and values. Field names
use ASCII `snake_case`; values are exact `str` UTF-8 bytes or exact `bytes` values. The component
does not use JSON, `repr()`, Unicode normalization, or ambiguous concatenation.

The immutable fingerprint stores only a 32-byte digest and a positive key version. Its instance
`compare()` method uses `hmac.compare_digest` for digest bytes and requires the same key version.
It returns `MATCH` only when both match; all other candidates return `CONFLICT`. Encoding helpers
are private module functions, and the implementation has no static methods.

## authService composition

authService requires the dedicated fingerprint secret during `Settings` validation because
idempotent authorization-state mutations are a declared service responsibility. Application
lifespan constructs one process-owned `BusinessOperationFingerprinter` and stores it in immutable
`ApplicationResources`. The current OAuth2 token operation is intentionally non-idempotent, and
the operator bootstrap is a one-shot local command; neither uses this primitive or persists an
idempotency record.

A future concrete idempotent operation must:

1. inject the lifespan-owned fingerprinter into its application handler;
2. define a small explicit semantic field mapping for that operation;
3. include an operation discriminator when multiple operation types share one persistence key
   namespace;
4. persist the digest and key version together inside the operation transaction boundary;
5. make same-key and same-payload replay distinct from same-key and different-payload conflict.

Sensitive exact values may be fingerprint inputs when retry equivalence requires them because only
the keyed digest is persisted. Canonical plaintext, fingerprint fields, secrets, and digest bytes
must never be persisted separately, logged, or exposed through an API. A randomized password hash,
model `repr()`, or unframed manual concatenation is not a semantic fingerprint input.

## Key lifecycle

The first-version policy does not implement a speculative keyring. Do not rotate the active
fingerprint key until all retained idempotency records produced with the old key have expired or
been deleted. The key version identifies the secret that produced a digest; removing that secret
means old records cannot be recomputed for replay. Without an explicit version-aware keyring, a
candidate produced with another key version is a conflict.

Settings and Kubernetes secret handling are documented in
`docs/getting-started/configuration.md` and
`docs/development/containers-and-kubernetes.md`.
