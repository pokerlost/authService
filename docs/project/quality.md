# Quality model

This page describes the independent checks available in the generated service and the limits of the evidence they provide.

## Regular source checks

- Ruff formatting checks enforce the configured Python layout without rewriting source in `make check`.
- Ruff lint checks enforce the selected rules in `pyproject.toml`.
- Strict mypy checks the project-owned application and documentation-checker source with Python
  3.14 semantics.
- `compileall` checks that application modules, the Alembic entry point, and documentation
  checker compile.
- Pre-commit applies standard file hygiene and runs project Ruff, mypy, and documentation
  hooks through the locked environment.
- The documentation audit rejects relative inter-file links and checks the index inventory,
  same-document anchors, H1 ownership, opening paragraphs, fenced-block languages, and prohibited
  local or temporary text.

Run the regular layers through `make check` and the expanded hook set through `make check-full`.
Their exact composition is documented in `docs/development/commands.md`.

## Persistence and packaging checks

- `alembic history` checks the five historical revision IDs and parent links without a database; real upgrade requires disposable PostgreSQL.
- Docker build and an explicit runtime `GET /` smoke check packaging and process startup when that environment-dependent workflow is run.
- `helm lint` and `helm template` check chart structure and rendered Kubernetes resources.
- The authoritative OpenAPI generator and installed-SDK end-to-end probe check `pypokerlost` compatibility when an API wire contract changes.
- The technical HTTP suite checks the active infrastructure contract. Positive PostgreSQL
  readiness is a separate integration check against disposable storage.

Docker, Helm, PostgreSQL, and SDK/OpenAPI workflows remain explicit because they can require local
daemons, credentials, network access, or external checkouts. See
`docs/development/database-migrations.md`, `docs/development/containers-and-kubernetes.md`, and
`docs/api/openapi-and-sdk.md`.

## Interpretation

These checks detect specific formatting, typing, syntax, documentation, metadata, packaging, rendering, and compatibility failures. They are not proof of business correctness, production readiness, or security.

This repository does not claim a security audit, performance measurements, or production
readiness. The private SDK build requires the reviewed-SHA environment and repository-scoped
secrets; a workflow definition alone is not a passed hosted run.
