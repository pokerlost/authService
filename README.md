# authService

`authService` is a Pokerlost FastAPI foundation installed from `src/authService/`. It retains
PostgreSQL wiring and historical revisions, but token and grant operations are planned in
[SERVICE.md](SERVICE.md) and absent from the current runtime.

Read `docs/index.md` for the complete guide and `AGENTS.md` for normative engineering rules. Python
3.14 or newer is required.

## 🚀 Install and run

The mandatory private `pypokerlost` dependency requires GitHub SSH read access:

```bash
uv sync --locked
make run
```

Supply `DATABASE_URL` through the process environment or a managed secret before startup. The
service validates the URL at factory creation; it does not load `.env` at import or connect until
its lifespan/readiness path. The lock pins the private SDK source; installation requires access
to that source. Do not place credentials or private keys in this repository.

## Base endpoints

| method | path | operation_id | response |
| --- | --- | --- | --- |
| `GET` | `/` | `getRoot` | `PokerlostResponse[None]` |
| `GET` | `/getOpenApi` | `getOpenApi` | OpenAPI JSON document |
| `GET` | `/health/live` | infrastructure | process liveness |
| `GET` | `/health/ready` | infrastructure | required database readiness |

These public infrastructure endpoints accept no body or authentication. Every business operation
uses `POST /<operationId>` and a typed `PokerlostRequest` JSON body. Protected calls add only the
standard `Authorization: Bearer <access-token>` header.

The pristine service includes an empty exact-scope catalog and a local-verifier port, but no fake
verifier, outbound client, credential, token store, or retry configuration. See
[header authorization](docs/api/header-authorization.md) and
[inter-service clients](docs/architecture/inter-service-clients.md).

## 🛠 Development and deployment

Run `make help` for the local tool interface. Regular quality entry points are:

```bash
make check
make pre-commit
```

Production access requires HTTPS/TLS. The generated Helm ClusterIP is an internal target and must
remain behind trusted TLS termination.

Historical revisions moved unchanged from `alembic/versions/` to `migrations/versions/`. They can
still create old authorization tables on a fresh database; this code migration does not remove
storage or prove a live database upgrade. See [migration guidance](docs/development/database-migrations.md).
