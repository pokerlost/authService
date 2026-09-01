# Public surface

This page is the authoritative manifest of HTTP endpoints currently exposed by `authService`.

## Endpoint manifest

| Method and path | `operation_id` | Request | `response_model` |
| --- | --- | --- | --- |
| `GET /` | `getRoot` | No parameters or body | `PokerlostResponse[None]` |
| `GET /getOpenApi` | `getOpenApi` | No parameters or body | `PokerlostResponse[dict[str, JSONValue]]` |
| `POST /getToken` | `getToken` | JSON `PokerlostRequest[GetTokenRequest]` | `PokerlostResponse[PokerlostToken]` |

The base identifiers shown are the `.env.example` values. Root, OpenAPI publication, and existing
probe routes are public infrastructure exceptions. Every business operation uses `POST` at the
path `/<operationId>`.

## `getToken`

`POST /getToken` accepts this private Pokerlost JSON request over HTTPS:

```json
{
  "payload": {
    "client_id": "5dfd4999-ab70-4d6c-b31d-ef855fa98320",
    "client_secret": "<secret>",
    "scopes": ["auth.internal.provisionHuman"],
    "audience": "authService"
  }
}
```

No authentication header, cookie, query parameter, form encoding, grant type, token type, or
caller-supplied generic header is part of the protocol. `getToken` is public at the transport
level and therefore has no `authorization` field.

The client ID must be a canonical lowercase hyphenated UUID. The logical audience is one exact
service identifier and is mapped internally to the existing persisted service resource. Every
requested scope must exist and be granted independently to both the service principal and bound
client. Role `auto` grants no scope.

A successful response is:

```json
{
  "ok": true,
  "result": {
    "access_token": "<secret>",
    "refresh_token": null,
    "expires_in": 600,
    "scopes": ["auth.internal.provisionHuman"],
    "audience": "authService"
  },
  "error": null,
  "error_message": null,
  "retry_after": null
}
```

The current service-client stage issues no refresh token. Failures use
`PokerlostResponse[None]`; any retry delay exists only in `retry_after`, never an HTTP header.
Secrets and submitted bodies are excluded from representations, validation messages, logs, and
traces.

## Deferred operations

`refreshToken`, `getJwks`, `provisionHuman`, `setPrincipalStatus`, `assignPrincipalRole`, and
`issueLoginGrant` may exist as future-facing SDK stubs, but authService does not currently expose
those endpoints.
