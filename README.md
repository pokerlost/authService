# authService

`authService` is the centralized identity and authentication system and the coarse-grained
authorization control plane for PokerLost. PostgreSQL is the authoritative store owned by this
service.

AUTH-01 contains infrastructure only. Registration, login, principals, users, credentials,
sessions, JWT, JWKS, refresh rotation, roles, permissions, policy registries, and audit business
events are intentionally absent.

The service is not an API gateway or reverse proxy. Other services will verify signed access
tokens locally through the future public JWKS contract. Integrations must use versioned contracts;
implementation imports and service-specific authorization branches are forbidden.

## Architecture

The source root is `app/` and is placed directly on `PYTHONPATH`:

```text
api -> application + persistence
configuration + observability -> API composition root
persistence -> domain
```

`api.application.create_application()` creates typed settings, the async SQLAlchemy engine,
session factory, lifespan, routes, exception handlers, request context, and Logfire
instrumentation. `api.asgi:application` is the ASGI runtime entrypoint.

Future RPC operations follow this flow:

```text
FastAPI router -> Request -> Command/Query -> Handler -> Repository/Read query -> PostgreSQL
```

HTTP routers remain transport-only. ORM entities remain in persistence. Application and domain
code do not depend on FastAPI or SQLAlchemy.

## Infrastructure API

| Method | Path | Operation ID | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health.checkLiveness` | `health.checkLiveness` | Process liveness; never queries PostgreSQL. |
| `GET` | `/health.checkReadiness` | `health.checkReadiness` | Readiness using one lightweight PostgreSQL `SELECT 1`. |

Responses use one public envelope. Success:

```json
{
  "ok": true,
  "result": {
    "status": "healthy"
  }
}
```

Failure:

```json
{
  "ok": false,
  "result": null,
  "error": "AUTH_INTERNAL_ERROR",
  "errorMessage": "Internal server error",
  "requestId": "3a0424e1-1058-40db-b50d-56536042c3ff"
}
```

The server always generates `X-Request-ID`. A syntactically valid `X-Correlation-ID` is preserved;
otherwise correlation defaults to the request ID. Both values are returned in response headers.
Client-provided request IDs are ignored.

OpenAPI is available at `/openapi.json` when `AUTH_HTTP__OPENAPI_ENABLED=true`. Dotted camelCase
paths, explicit operation IDs, field aliases, result schemas, and error codes are compatibility
contracts for future SDK generation.

## Configuration

Configuration is loaded once through `configuration.Settings`. Environment variables use the
`AUTH_` prefix and `__` for nesting. The PostgreSQL URL is mandatory and must use
`postgresql+asyncpg`. It is held as `SecretStr` and is never printed by application code.

Copy `.env.example` for local development and replace its local-only placeholder. Production must
set `AUTH_APPLICATION__ENVIRONMENT=production`, enable remote Logfire delivery, and supply
`AUTH_LOGFIRE__TOKEN`; invalid combinations fail during application construction.

Gunicorn process settings are intentionally separate from application settings:

```text
GUNICORN_WORKERS
GUNICORN_TIMEOUT
GUNICORN_GRACEFUL_TIMEOUT
GUNICORN_KEEPALIVE
GUNICORN_FORWARDED_ALLOW_IPS
```

Only explicitly trusted proxy addresses should be placed in `GUNICORN_FORWARDED_ALLOW_IPS`.

## Transactions and persistence

The shared FastAPI database dependency uses:

```python
async with session_factory.begin() as session:
    yield session
```

Each future parameterized HTTP request therefore owns exactly one transaction. Dependency exit
commits success, rolls back exceptions, and closes the session. Handlers, services, repositories,
and query adapters must never call `commit()`, `rollback()`, or `begin()`. No Unit of Work wrapper
is used.

Repositories will return ORM entities. Optimized read adapters will return immutable typed
projections. No repositories exist in AUTH-01 because there are no persisted business entities.

## Observability and security

Logfire is configured once at composition time and instruments FastAPI and the concrete
SQLAlchemy async engine. Request headers and validated endpoint arguments are not captured.
Scrubbing extends Logfire defaults for authorization headers, cookies, passwords, tokens, private
keys, client secrets, DSNs, and database URLs. SQLAlchemy parameter display is disabled.

Request and correlation IDs are attached as safe Logfire baggage so request, database, error, and
future audit telemetry can be correlated. Public exception handlers never expose exception text,
tracebacks, SQL, constraint names, or connection details.

## Local development

Requirements are Python 3.12+, `uv`, and PostgreSQL.

```bash
make install
make run
```

The Typer command behind `make run` starts one local Uvicorn worker. Production starts Gunicorn
directly with `uvicorn_worker.UvicornWorker`:

```bash
make run-production
```

Static checks are available through `make lint`, `make format-check`, and `make typecheck`.
No automated tests or CI/CD configuration belong to AUTH-01.

## Migrations

Alembic reads the same typed database configuration and uses `Base.metadata` for autogeneration:

```bash
make migration-upgrade
make migration-create message="describe change"
make migration-downgrade
```

AUTH-01 has no business or infrastructure tables, so it deliberately has no empty baseline
revision. The first real persistence feature must import its ORM mappings before autogeneration
and create the first meaningful revision.

## Docker and Helm

The multi-stage image installs the locked runtime dependency set, runs as UID/GID `10001`, and
starts Gunicorn without migrations. Build and run it only with externally supplied configuration
and secrets.

The Helm chart lives at `deploy/helm/authservice`. It references existing Kubernetes Secrets for
the database URL and Logfire token; it never creates secret material or PostgreSQL. The chart uses
RPC health probes, a read-only root filesystem, dropped capabilities, no service-account token,
and a writable in-memory `/tmp` for Gunicorn. `values-kind.yaml` is a local kind override and still
expects an externally created database Secret.

## Recovery and limitations

PostgreSQL outages leave liveness healthy and make readiness return `503`. Kubernetes can stop
routing traffic while the process remains observable; readiness recovers automatically when the
database is reachable. In-flight transaction exceptions roll back through the session dependency.

AUTH-01 does not yet define identity invariants, idempotency rules, authentication contracts,
signing-key recovery, authorization policy behavior, or authentication audit events. Those must be
introduced with the corresponding domain stages rather than guessed in the foundation.
