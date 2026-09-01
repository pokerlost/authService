# Service client credentials

This page defines the current authService boundary for confidential service clients, exact machine
grants, credential storage, and RS256 access-token issuance.

## Operator bootstrap

`authservice bootstrap-service-client` creates one complete service-client bundle in a caller-owned
PostgreSQL transaction. The command requires a non-empty service slug, one or more exact scopes,
and one or more exact resource indicators. It rejects duplicates, unknown scopes, invalid
resources, and an existing service binding instead of modifying or widening existing grants.

The bundle contains:

- one active authorization principal with `principal_type=service` and `role=auto`;
- one active confidential OAuth client bound to that exact principal;
- explicit `client_credentials` permission;
- identical requested scope rows in the direct service and OAuth client grant tables;
- identical requested resource rows in the service and OAuth client audience tables;
- one active OAuth client credential containing only a secret digest.

The client ID is a service-generated UUID. The raw secret encodes exactly 32 cryptographically
random bytes as URL-safe unpadded text. The command prints the client ID and raw secret only after
the transaction commits. It cannot display the raw secret again because persistence stores only a
32-byte domain-separated SHA-256 digest.

## Credential acceptance

The focused security component owns secret generation, digest calculation, and verification. Its
code-level domain separator is `pokerlost.oauth-client-secret.v1\x00`, and verification uses a
constant-time digest comparison. It does not use password hashing, recoverable encryption, or a
bare unseparated hash.

An active credential is accepted until its optional expiry. A retiring credential is accepted
only while it is not revoked and has not expired. A revoked or expired credential is never
accepted. Digest bytes do not enter API models, CLI output, exception messages, or logs.

## Machine authorization

Client authentication and authorization are separate checks. Token issuance requires an active
confidential client bound to an active service principal whose role is exactly `auto`, an accepted
credential, and explicit client permission for `client_credentials`.

Role `auto` contributes no scopes. Every requested scope must exist in the scope catalog and be a
member of both the direct service grant set and the OAuth client grant set. The exact resource must
match `^urn:pokerlost:service:[a-z][A-Za-z0-9]*$` and be a member of both the service and client
audience grant sets. Comparison is exact and case-sensitive; there is no wildcard, normalization,
hostname derivation, inheritance, or `master` bypass.

## Token issuance

`POST /getToken` receives a validated `PokerlostRequest[GetTokenRequest]` JSON body. The API
boundary parses the canonical client UUID and maps the logical audience to the existing internal
resource representation. The application handler loads an immutable authorization context through
a query port, authenticates the body credential without revealing why a candidate failed,
evaluates both grant intersections, creates service-only claims, and calls the signer port. The
route does not query SQLAlchemy, compare digests, construct JWTs, or complete the transaction.

The process-owned security adapter loads the configured PEM key once during application lifespan,
requires an RSA private key of at least 2048 bits, and signs with the fixed RS256 algorithm. Every
JWT header contains `typ: JWT` and the configured non-empty `kid`. Claims contain `iss`, service
principal `sub`, exact resource `aud`, `iat`, `nbf`, `exp`, a fresh UUID `jti`, `client_id`, sorted
scope string, `principal_type=service`, `role=auto`, and `service_slug`.

Numeric dates use UTC semantics. `nbf` is not later than `iat`, and `exp` is exactly the configured
access-token TTL after `iat`. Every successful issuance generates a fresh `jti`.

The route returns `PokerlostResponse[PokerlostToken]`; the access token exists only at
`result.access_token`. Handled failures use `PokerlostResponse[None]` with stable authService error
metadata. The response has no token type or HTTP-header representation. The access token is not
persisted. It contains no account, username, nickname, session, password, refresh token, or
all-possible-scope data. A service principal receives no session or refresh token.

FastAPI instrumentation does not capture request headers or bodies. Submitted JSON credentials,
raw client secrets, access tokens, secret digests, and private-key material
are excluded from structured logs and exception payloads.

## Consumer SDK boundary

A consumer application handler delegates token acquisition to a service-owned application port.
Its focused `pypokerlost` composition uses the generated `GetToken` method and
`PokerlostAuthorizationMiddleware`; the SDK owns transport, body authorization, token lifecycle,
and shared wire models. Canonical retry is available through the middleware package.

```python
from pypokerlost import PokerlostRequestOptions
from pypokerlost.middleware import PokerlostAuthorizationMiddleware, PokerlostRetryPolicy
```

One target-specific client is created and started in the consumer's application lifespan, reused
across requests, and stopped during shutdown. A dedicated auth-target client without authorization
middleware prevents recursion. Credentials enter only the `getToken` JSON payload; required exact
scopes come from method metadata.

Retry is disabled unless one replay-safe call supplies an explicit `PokerlostRetryPolicy` through
`PokerlostRequestOptions.retry_policy`. There is no automatic replay after `401` or `403`.
Mutation replay requires the same consumer-owned `business_operation_id` and semantic payload,
and no PostgreSQL transaction may span token acquisition, an outbound attempt, or backoff sleep.
authService does not create a reverse client to accountsService or an outbound client to itself.

## Current signing-key boundary

The private key is supplied only as a read-only Kubernetes Secret file or an equivalent local
operator-controlled file. Environment and ConfigMap data contain only its path and key ID. The
current process signs with one configured key and publishes no JWKS endpoint or retained public-key
history. Consumer rollout, unknown-`kid` handling, key retention, and rotation control remain
outside the current implementation.
