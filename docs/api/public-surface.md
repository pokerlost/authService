# Public surface

This is the authoritative manifest of endpoints currently exposed by `authService`.

| Method and path | `operation_id` | Request | Response |
| --- | --- | --- | --- |
| `GET /` | `getRoot` | No body or authentication | `PokerlostResponse[None]` |
| `GET /getOpenApi` | `getOpenApi` | No body or authentication | OpenAPI 3.1 document |
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

The operation has no access-token `Authorization` header because its generated method declares
`__scopes__ = None`; its client credentials are operation-specific payload fields. Pydantic parses
the client ID as a UUID, stores the client secret as `SecretStr`, and rejects empty or duplicate
scope lists before the route runs. Audience is the same exact service name in request, persisted
grants, response, and JWT. Every requested scope must exist and be granted independently to the
principal and client.

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
`provisionHuman`, `setPrincipalStatus`, `replacePrincipalScopes`, and `issueLoginGrant` are not
active authService endpoints.
