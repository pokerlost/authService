# Project status

This page records the intentional current state of `authService`.

## Ready foundation

The repository provides the FastAPI composition root, typed configuration, request context, safe
error mapping, Logfire instrumentation foundations, PostgreSQL transaction ownership,
authorization domain and persistence foundations, Alembic integration, Docker packaging, Helm
resources, and the locked local quality workflow. It also constructs one process-owned keyed
business-operation fingerprinter and one process-owned RS256 signer from required runtime
configuration.

The two base endpoints are ready with the `.env.example` values:

- `GET /` returns the service root envelope;
- `GET /openapi.get` publishes the wrapped FastAPI OpenAPI document.

Their operation IDs and the OpenAPI publication path are settings-driven; the root HTTP path is
always `/`. Their exact contract is listed in `docs/api/public-surface.md`.

The current service-client flow adds transactional operator bootstrap and `POST /oauth.token` for
HTTP Basic authenticated `client_credentials`. It authorizes only the exact intersection of direct
service and client scope and audience grants, stores client credentials only as digests, and issues
short-lived service-only RS256 access tokens. Token success is
`ApplicationResponse[OAuthTokenResponse]`, and every handled failure is
`ApplicationResponse[None]`.

## Intentionally absent

Human principal HTTP management, login-grant exchange, refresh tokens, sessions, logout, JWKS,
retained signing keys, and signing-key rotation are not implemented. The repository also defines no
persisted idempotency record or remote-service client. Operation identifiers listed in `SERVICE.md`
outside the current public surface are service responsibilities, not callable endpoints.

The SDK transport/shared-contract boundary, service-owned token port and adapter, and explicit
`PokerLostRetryPolicy` opt-in are documented in
`docs/architecture/inter-service-clients.md`. They are extension points rather than current
runtime resources: authService has no outbound target URL, token-acquisition port, token cache, or
unused client.

`SERVICE.md` defines the concrete service purpose, responsibilities, and service-specific rules.
Future documentation must describe only implemented current behavior and be listed in
`docs/index.md` when introduced.

See `docs/architecture/overview.md` for layer ownership and
`docs/development/contributing.md` for change discipline.
