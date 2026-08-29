# Project status

This page records the intentional current state of `authService`.

## Ready foundation

The repository provides the FastAPI composition root, typed configuration, request context, safe
error mapping, Logfire instrumentation foundations, PostgreSQL transaction ownership,
authorization domain and persistence foundations, Alembic integration, Docker packaging, Helm
resources, and the locked local quality workflow. It also constructs one process-owned keyed
business-operation fingerprinter from required runtime configuration.

The two base endpoints are ready with the `.env.example` values:

- `GET /` returns the service root envelope;
- `GET /openapi.get` publishes the wrapped FastAPI OpenAPI document.

Their operation IDs and the OpenAPI publication path are settings-driven; the root HTTP path is
always `/`. Their exact contract is listed in `docs/api/public-surface.md`.

## Intentionally absent

Public business functionality is not implemented yet. The repository defines no concrete business
route or application handler, no persisted idempotency record, no remote-service client, and no
token-issuance flow. Existing authorization models and the initial migration are foundations, not
evidence that the operations listed in `SERVICE.md` are already callable.

`SERVICE.md` defines the concrete service purpose, responsibilities, and service-specific rules.
Future documentation must describe only implemented current behavior and be listed in
`docs/index.md` when introduced.

See `docs/architecture/overview.md` for layer ownership and
`docs/development/contributing.md` for change discipline.
