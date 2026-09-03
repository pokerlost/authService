# Operation contract

Pokerlost business APIs use one private JSON operation protocol over HTTPS.

## Operations and paths

Every business operation matches:

```text
operation_id = lowerCamelCase verb name
path         = "/" + operation_id
HTTP method  = POST
```

The exact identifier pattern is `^[a-z][A-Za-z0-9]*$`. Valid examples include `getMe`,
`registerAccount`, and `provisionHuman`. Dots, underscores, hyphens, and uppercase initials are
invalid. The generator validates all source documents together and rejects global operation or
schema collisions before writing.

`GET /`, `GET /getOpenApi`, and existing health probes are public bodyless infrastructure
exceptions. Business GET bodies and other business HTTP methods are unsupported.

Each router is one flat module with a module-level `router = APIRouter(...)` and module-level
decorated endpoints. Do not use static router factories, nested endpoints, nested router
directories, imperative registration, route constants used once, or post-hoc mutation.

## Requests

A public operation accepts `PokerlostRequest[Payload]`:

```json
{
  "payload": {
    "username": "alice"
  }
}
```

A protected operation uses the same request envelope:

```json
{
  "payload": {}
}
```

It additionally receives `Authorization: Bearer <access-token>`. Service/application code never
constructs a generic header map, and access-token authentication never enters the JSON body.

Payload types are named closed Pydantic models with snake_case wire fields. Pydantic owns UUID,
enum, credential, audience, and primitive wire parsing plus cross-field wire invariants. Route
modules do not duplicate that work in `_parse_*` or `_validate_*` helpers. Requests do not use
business path/query parameters, cookies, form data, caller-supplied transport metadata, embedded
anonymous bodies, or manual content negotiation.

## Responses

Every business success and handled failure uses `PokerlostResponse`. Normal routes declare the
typed envelope as `response_model` and return plain mappings or data for FastAPI to validate and
serialize. Central exception handlers alone construct `PokerlostResponse[None]` explicitly before
returning `JSONResponse`. The five-field invariant is documented in
`docs/api/pokerlost-response.md`.

## Scopes

Scope IDs are separate from operation IDs. Protected routes declare exact values through FastAPI
`Security`; standard OpenAPI then drives the generated method's explicit `__scopes__` metadata.
No access-token scope requirement is represented only by `None`; an empty tuple is invalid. See
`docs/api/header-authorization.md`.
