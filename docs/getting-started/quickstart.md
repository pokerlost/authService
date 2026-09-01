# Quickstart

This page starts authService locally, exercises its base endpoints, and identifies the service-client
bootstrap and token boundaries.

Complete `docs/getting-started/installation.md`, provide valid required configuration and an RSA
private key at the configured path, and start the development server:

```bash
make run
```

The server listens on the configured `http.host` and `http.port`; the example `.env` uses `127.0.0.1:8000`.

## Service root

Call the service root path:

```bash
curl --fail-with-body http://127.0.0.1:8000/
```

The response is the exact successful `ApplicationResponse[None]` envelope:

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "error_message": null
}
```

## OpenAPI document

Retrieve the public OpenAPI document through the `.env.example` publication operation path:

```bash
curl --fail-with-body http://127.0.0.1:8000/openapi.get
```

That path reflects the `.env.example` value
`AUTHSERVICE_OPENAPI_OPERATION=openapi.get`. If configuration uses
`contract.getOpenAPI`, request `/contract.getOpenAPI` instead.

The response uses the same four-field envelope. Its `result` is the complete FastAPI-generated OpenAPI object; the object includes the following stable service metadata:

```json
{
  "ok": true,
  "result": {
    "openapi": "3.1.0",
    "info": {
      "title": "authService",
      "version": "0.1.0"
    },
    "x-pokerlost-service": {
      "id": "authService"
    }
  },
  "error": null,
  "error_message": null
}
```

The displayed `result` focuses on stable metadata; the actual object also contains the generated
`paths` and schemas, including the OAuth2 form and HTTP Basic contract at `/oauth.token`. See
`docs/api/openapi-and-sdk.md` for publication rules and
`docs/api/public-surface.md` for the exact current endpoint inventory.

## Service-client flow

Before requesting a service token, an operator runs `authservice bootstrap-service-client` with
exact scopes and resources against the configured PostgreSQL database. The command emits the raw
client secret once after commit; it must be transferred through an operator-approved secret
channel because authService cannot recover it from the persisted digest.

The client then submits HTTP Basic credentials and an `application/x-www-form-urlencoded` request
to `POST /oauth.token`. The response uses `ApplicationResponse`; a successful access token appears
only at `result.access_token`. See `docs/architecture/service-client-credentials.md` for
authorization and credential rules and `docs/api/public-surface.md` for the exact wire contract.
