# Public surface

This is the endpoint manifest for a pristine generated `authService` service.

| Method and path | `operation_id` | Request | Response |
| --- | --- | --- | --- |
| `GET /` | `getRoot` | No body or authentication | `PokerlostResponse[None]` |
| `GET /getOpenApi` | `getOpenApi` | No body or authentication | OpenAPI JSON document |
| `GET /health/live` | Excluded from OpenAPI | No body or authentication | Process liveness |
| `GET /health/ready` | Excluded from OpenAPI | No body or authentication | Required dependency readiness or 503 |

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

The root and liveness endpoints do not prove database readiness. `/health/ready` checks the
required database with a bounded timeout and returns 503 when it is unavailable.

A concrete service records every implemented business route here with its exact POST path,
operation ID, typed body/result, statuses, and exact required scopes. Planned SDK stubs are not
documented as active server endpoints.
