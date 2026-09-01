# Public surface

This is the authoritative manifest of endpoints currently exposed by `authService`.

| Method and path | `operation_id` | Request | Response |
| --- | --- | --- | --- |
| `GET /` | `getRoot` | No body or authentication | `PokerlostResponse[None]` |
| `GET /getOpenApi` | `getOpenApi` | No body or authentication | `PokerlostResponse[dict[str, JSONValue]]` |
| `POST /getToken` | `getToken` | JSON `PokerlostRequest[GetTokenRequest]` | `PokerlostResponse[PokerlostToken]` |

The root response is:

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "error_message": null,
  "retry_after": null
}
```

The two infrastructure endpoints do not prove database readiness. Liveness/readiness probes use
`/` only as process availability.

## getToken

`POST /getToken` accepts the following public transport-level request over HTTPS:

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

Authentication material has no alternate HTTP transport. The operation has no `authorization`
field because it is public at transport level. The client ID is a canonical lowercase UUID; the
audience is a single service identifier mapped internally to the persisted resource value. Every
requested scope must exist and be granted independently to the service principal and client.

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

The current stage creates no refresh token. Deferred SDK stubs `refreshToken`, `getJwks`,
`provisionHuman`, `setPrincipalStatus`, `assignPrincipalRole`, and `issueLoginGrant` are not active
authService endpoints.
