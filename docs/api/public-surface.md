# Public surface

This page is the authoritative manifest of HTTP endpoints currently exposed by `authService`.

## Endpoint manifest

| Method and path | `operation_id` | Request | `response_model` | Published status and error responses |
| --- | --- | --- | --- | --- |
| `GET /` | `auth.getRoot` | No parameters or body | `RootResponse` (`ApplicationResponse[None]`) | `200`: `RootResponse`; `500`: `ApplicationResponse[None]` |
| `GET /openapi.get` | `openapi.get` | No parameters or body | `OpenAPIResponse` (`ApplicationResponse[dict[str, JSONValue]]`) | `200`: `OpenAPIResponse`; `500`: `ApplicationResponse[None]` |
| `POST /oauth.token` | `oauth.token` | `application/x-www-form-urlencoded` `OAuthTokenRequest` and HTTP Basic | `ApplicationResponse[OAuthTokenResponse]` | `200`: `ApplicationResponse[OAuthTokenResponse]`; `400`, `401`, `500`, `503`: `ApplicationResponse[None]` |

The table shows the `.env.example` values. The root path remains `/` when
`AUTHSERVICE_ROOT_OPERATION` changes. The OpenAPI path changes with
`AUTHSERVICE_OPENAPI_OPERATION` and is always `"/" + operation_id`.

Both base success models use the exact four-field `ApplicationResponse` envelope documented in
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
runtime exceptions as described in `docs/api/errors.md`; those are not additional route
declarations.

## OAuth2 token operation

`POST /oauth.token` accepts exactly one `grant_type=client_credentials`, one non-empty
space-delimited `scope`, and one exact resource indicator matching
`urn:pokerlost:service:<serviceIdentity>`. Confidential-client credentials are accepted only as
HTTP Basic authentication. Body `client_id` or `client_secret` parameters are invalid.

The client ID is a canonical lowercase hyphenated UUID. Requested scopes are exact,
case-sensitive `OAuthScope` values with dot-delimited lowerCamelCase segments and no duplicates. A
successful request requires every scope in both the service principal's direct grants and the
bound OAuth client's grants, and requires the exact resource in both audience grant sets.

Success contains `access_token`, `token_type: "bearer"`, configured `expires_in`, and the
deterministically sorted exact scope string inside `ApplicationResponse.result`. The access token
exists only as `result.access_token`, and the result contains no refresh token. Handled failures
use `ApplicationResponse[None]` with stable `AUTHSERVICE_*` codes and safe messages. All token
success and failure responses include `Cache-Control: no-store` and `Pragma: no-cache`;
`AUTHSERVICE_INVALID_CLIENT` also includes `WWW-Authenticate: Basic`. Form, security, success, and
failure schemas are preserved in the generated OpenAPI document.

## Probe meaning

`GET /` proves that the process can serve the minimal application response. It does not request a
database dependency, execute a PostgreSQL query, or prove database readiness. Deployment probes use
this application-availability endpoint with that limited meaning.

The configured OpenAPI operation publishes the current FastAPI schema as described in
`docs/api/openapi-and-sdk.md`. Neither base endpoint contains business behavior.

## Maintaining the manifest

A service change must add every new or changed public method here with its exact path,
`operation_id`, request model or body omission, response model, and published status/error models.
The method must also follow `docs/api/operation-contract.md`. Remove
manifest entries when their routes are removed; do not document planned endpoints as current
behavior.
