# Public surface

This page is the authoritative manifest of HTTP endpoints present in a pristine generated
`authService` service.

## Endpoint manifest

| Method and path | `operation_id` | Request | `response_model` | Published status and error responses |
| --- | --- | --- | --- | --- |
| `GET /` | `auth.getRoot` | No parameters or body | `RootResponse` (`ApplicationResponse[None]`) | `200`: `RootResponse`; `500`: `ApplicationResponse[None]` |
| `GET /openapi.get` | `openapi.get` | No parameters or body | `OpenAPIResponse` (`ApplicationResponse[dict[str, JSONValue]]`) | `200`: `OpenAPIResponse`; `500`: `ApplicationResponse[None]` |

The table shows the `.env.example` values. The root path remains `/` when
`AUTHSERVICE_ROOT_OPERATION` changes. The OpenAPI path changes with
`AUTHSERVICE_OPENAPI_OPERATION` and is always `"/" + operation_id`.

Both success models use the exact four-field `ApplicationResponse` envelope documented in
`docs/api/application-response.md`. The OpenAPI operation returns the generated document in
`result`; the root operation returns this exact body:

```json
{
  "ok": true,
  "result": null,
  "error": null,
  "error_message": null
}
```

The base route decorators explicitly publish only the `500` error model shown above. Global API
handlers also envelope-normalize unmatched paths, unsupported methods, validation failures, and
runtime exceptions as described in `docs/api/errors.md`; those are not additional pristine
route declarations.

## Probe meaning

`GET /` proves that the process can serve the minimal application response. It does not request a
database dependency, execute a PostgreSQL query, or prove database readiness. Deployment probes use
this application-availability endpoint with that limited meaning.

The configured OpenAPI operation publishes the current FastAPI schema as described in
`docs/api/openapi-and-sdk.md`. Neither base endpoint contains business behavior.

## Maintaining the manifest

A concrete service must add every new or changed public method here with its exact path,
`operation_id`, request model or body omission, response model, and published status/error models.
The method must also follow `docs/api/operation-contract.md`. Remove
manifest entries when their routes are removed; do not document planned endpoints as current
behavior.
