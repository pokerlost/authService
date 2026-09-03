# Service client credentials

This page defines authService ownership of confidential service clients, direct grants, credential
storage, and scope-only RS256 access-token issuance.

## Operator bootstrap

`authservice bootstrap-service-client` creates one complete service-client bundle in a caller-owned
PostgreSQL transaction. The command requires a non-empty service slug, one or more exact scopes,
and one or more exact service-name audiences. It rejects duplicates, unknown scopes, invalid
audiences, and an existing service binding instead of widening an existing grant set.

The bundle contains:

- one active authorization principal with `principal_type=service`;
- one active confidential OAuth client bound to that principal;
- explicit `client_credentials` permission;
- identical requested rows in `principal_scope_grants` and `client_scope_grants`;
- identical requested rows in `principal_audience_grants` and `client_audience_grants`;
- one active `client_credentials` row containing only a secret digest.

The client ID is a service-generated UUID. The raw secret encodes exactly 32 cryptographically
random bytes as URL-safe unpadded text. The command prints the ID and raw secret only after commit.
Persistence stores only a 32-byte domain-separated SHA-256 digest.

## Credential acceptance

The focused security component owns secret generation, digest calculation, and verification. Its
code-level domain separator is `pokerlost.oauth-client-secret.v1\x00`, and verification uses a
constant-time digest comparison. It does not use password hashing, recoverable encryption, or a
bare unseparated hash.

An active credential is accepted until its optional expiry. A retiring credential is accepted
only while it is not revoked and has not expired. A revoked or expired credential is never
accepted. Digest bytes do not enter API models, CLI output, exception messages, or logs.

## Scope-only machine authorization

Token issuance requires an active confidential client bound to the same active service principal,
an accepted credential, and explicit client permission for `client_credentials`. Service identity
is determined by `principal_type=service`.

Every request supplies a non-empty, duplicate-free exact scope set. Each requested scope must
exist in `scope_definitions` and be present in both the principal and client grant sets. The exact
audience must be present in both audience grant sets and match `^[a-z][A-Za-z0-9]*$`. There is no
default authority, wildcard, inheritance, normalization, or identity-category bypass.

## Token issuance

`POST /getToken` receives `PokerlostRequest[GetTokenRequest]`. The Pydantic request model parses the
client ID as `UUID`, stores the credential as `SecretStr`, validates the non-empty duplicate-free
scope tuple, and validates the exact `PokerlostAudience` before route entry. The route maps those
typed values to an application command. The handler loads one immutable authorization context,
authenticates the operation credential without revealing why a candidate failed, evaluates both
grant intersections, builds service claims, and calls the signer port.

The process-owned security adapter loads the configured PEM key once during application lifespan,
requires an RSA private key of at least 2048 bits, and signs with fixed RS256. Every JWT header
contains `typ: JWT` and the configured `kid`. Claims contain `iss`, principal `sub`, exact
service-name `aud`, `iat`, `nbf`, `exp`, fresh UUID `jti`, `client_id`, exact `scopes`, and
`principal_type=service`. They contain no authorization classification or internal service slug.

Numeric dates use UTC semantics. `nbf` is not later than `iat`, and `exp` is exactly the configured
access-token TTL after `iat`. The handler returns an application result containing the authoritative
audience, and the route maps it to plain data. FastAPI validates and serializes that data through
`PokerlostResponse[PokerlostToken]`; the access token exists only at `result.access_token`, is not
persisted, and has no refresh token at this stage.

FastAPI instrumentation captures neither request headers nor bodies. Submitted credentials,
access tokens, secret digests, and private-key material are excluded from structured logs and
exception payloads.

## Consumer SDK boundary

Initial acquisition is explicit consumer orchestration: call generated `GetToken`, validate the
canonical response, and save shared token state. The SDK never stores client credentials and never
calls `getToken` automatically.

A protected client receives only a `PokerlostTokenStore` and `PokerlostTokenRefresher` port. The
store key includes client identity, exact audience, and exact scope set. Stored state uses an aware
UTC `expires_at` and a positive version for compare-and-swap updates. A production refresher owns
cross-process coordination and must not hold a PostgreSQL transaction during network I/O.

Authentication middleware loads that state and injects the bearer header internally. Only exact
`POKERLOST_ACCESS_TOKEN_EXPIRED` may invoke the refresher once and replay the same request once;
local expiry metadata and other authentication or authorization failures do not trigger refresh.

authService currently creates no outbound client, token store, or refresher because it has no real
outbound protected dependency.

## Current signing-key boundary

The private key is supplied only as a read-only Kubernetes Secret file or equivalent local
operator-controlled file. Environment and ConfigMap data contain only its path and key ID. The
current process signs with one configured key and publishes no JWKS endpoint or retained public-key
history. Consumer rollout, unknown-`kid` handling, key retention, and rotation control remain
outside the current implementation.
