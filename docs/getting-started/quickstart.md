# Quickstart

Start the foundation locally and inspect its infrastructure endpoints. Set a disposable
`DATABASE_URL` before startup; readiness will return 503 until PostgreSQL is reachable.

## Run

```bash
uv sync --locked
DATABASE_URL='postgresql+asyncpg://user:password@127.0.0.1:5432/authservice' make run
```

Local development may bind the loopback HTTP server. Production access requires HTTPS/TLS and
must not expose this development listener directly.

## Root

```bash
curl --fail-with-body http://127.0.0.1:8000/
```

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "error_message": null,
  "retry_after": null
}
```

## OpenAPI

```bash
curl --fail-with-body http://127.0.0.1:8000/getOpenApi
```

The response is the unmodified FastAPI OpenAPI document. When a concrete service has protected
operations, the document contains their standard OAuth2 security metadata. With no protected
operation, an unused security scheme may be absent.

The pristine service exposes no business operation. Before adding one, read
`docs/api/operation-contract.md`, `docs/api/header-authorization.md`, and
`docs/api/pokerlost-response.md`.
