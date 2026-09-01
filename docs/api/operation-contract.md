# Operation contract

authService uses the private Pokerlost JSON operation-call protocol over HTTPS. It is not an
OAuth2, Bearer, Basic, API-key, cookie, or header-authentication wire protocol.

## Operations and paths

Business operation identifiers match:

```text
^[a-z][A-Za-z0-9]*$
```

Every business operation uses `POST /<operationId>`. Business input never uses path, query, header,
or cookie parameters. `GET /`, `GET /getOpenApi`, and existing health probes are public bodyless
infrastructure exceptions.

Routers are flat modules built by `create_<feature>_router(...)` factories. Endpoints are registered
with decorators and write stable operation IDs directly in the decorator. There are no dotted
service namespaces, derived path constants, imperative route registration, or OpenAPI extras.

## Request bodies

Public and token operations use one JSON body:

```json
{"payload": {}}
```

Protected operations use the only other envelope:

```json
{
  "authorization": {"access_token": "<secret>"},
  "payload": {}
}
```

`getToken` uses the public envelope because it acquires a token. Its client credentials, scopes,
and audience are fields of `payload`; there is no form encoding or `grant_type`.

## Responses

Success and handled failure use `PokerlostResponse`, documented in
`docs/api/application-response.md`. No response header carries authentication challenges or retry
delay.

## Scopes

Scope identifiers are separate from operation IDs and match dotted lowerCamelCase segments. A
protected server route declares exact scopes with FastAPI `Security(..., scopes=[...])`, while the
matching flat SDK method declares the same `required_scopes`. OpenAPI represents body authorization
through the request schema; it does not publish a misleading OAuth2 or API-key security scheme.

authService has no implemented protected route in the current stage. `getToken` is public at the
transport level and its SDK method has empty `required_scopes`.
