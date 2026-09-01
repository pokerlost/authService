# Quickstart

Start authService locally, inspect its infrastructure endpoints, and review the service-token
boundary.

## Run

```bash
cp .env.example .env
uv lock
uv sync --locked
make run
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

The response wraps the unmodified FastAPI OpenAPI document in `PokerlostResponse`. The document
contains no project extension or misleading header-oriented security scheme.

## Service-token flow

Before requesting a token, an operator runs `authservice bootstrap-service-client` with exact
scope and audience grants against PostgreSQL. The command emits the raw client secret once after
commit; authService persists only its digest.

The client submits `PokerlostRequest[GetTokenRequest]` JSON to `POST /getToken`. Credentials,
scopes, and logical audience exist only in `payload`; a successful access token appears only in
`result.access_token`. See `docs/architecture/service-client-credentials.md` and
`docs/api/public-surface.md` for the exact contract.
