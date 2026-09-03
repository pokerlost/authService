# Project status

This page records the intentional current state of `authService`.

## Ready foundation

The repository provides the FastAPI composition root, typed configuration, a server-generated
request ID, safe response errors, Logfire instrumentation, PostgreSQL transaction ownership,
authorization/client persistence, Alembic, Docker, Helm, and the locked quality workflow. Lifespan
also constructs one process-owned RS256 signer from required configuration.

The two base endpoints are ready with the `.env.example` values:

- `GET /` returns the service root envelope;
- `GET /getOpenApi` publishes the raw FastAPI OpenAPI document.

Their operation IDs are `getRoot` and `getOpenApi`; the root HTTP path is always `/`.

Their exact contract is listed in `docs/api/public-surface.md`.

Transactional operator bootstrap and public JSON `POST /getToken` are implemented. Token issuance
uses the exact intersection of direct principal/client scope and audience grants, stores
credentials only as digests, and returns a short-lived service access token in
`PokerlostResponse[PokerlostToken]`.

## Intentionally absent

Human principal HTTP management, login-grant exchange, refresh tokens, sessions, logout, JWKS,
retained signing keys, and signing-key rotation remain absent. authService has no outbound client,
concrete token verifier, token store, or service-specific retry configuration. The local auth scope
catalog and fail-closed verifier seam are foundation for future protected routes.

The SDK transport/middleware boundary and explicit `PokerlostRetryPolicy` opt-in are documented in
`docs/architecture/inter-service-clients.md`. These are extension points, not default runtime
resources: authService has no target URL, outbound scope bundle, token cache, or unused client.

`SERVICE.md` defines the service purpose, responsibilities, and service-specific rules. Future
documentation must describe only implemented behavior and be listed in `docs/index.md`.

See `docs/architecture/overview.md` for layer ownership and
`docs/development/contributing.md` for change discipline.
