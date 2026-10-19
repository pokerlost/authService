# authService

`authService` is a Pokerlost FastAPI foundation installed from `src/authservice/`. It retains
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
make test
make pre-commit
```

Production access requires HTTPS/TLS. The generated Helm ClusterIP is an internal target and must
remain behind trusted TLS termination.

Historical revisions moved unchanged from `alembic/versions/` to `migrations/versions/`. They can
still create old authorization tables on a fresh database; this code migration does not remove
storage or prove a live database upgrade. See [migration guidance](docs/development/database-migrations.md).

The private SDK build uses owner-only manual dispatch and an exact full SHA equal to the branch SHA and `SDK_BUILD_REVIEWED_SHA`; source checks run without SDK secrets. The image uses a BuildKit `sdk_token` secret. No release or deployment is triggered by CI.

## Tested foundation commands

The shared template owns `Makefile`, `tests/foundation/` and `deploy/chart/`. Project-owned tests,
settings, scopes and migration history survive updates. `make test-unit` reports isolated
coverage; `make test` also measures enabled integration before advisory report generation. Missing owned
paths remain visible in the report. `make build image verify` uses the canonical wheel
container graph and requires the separately approved SDK-only BuildKit secret.

`make chart-check chart` validates/packages the shared chart. `make deploy-local` and
`make undeploy-local` operate only the explicit disposable Kind contour. External deployment
requires an approved destination and tested image manifest digest. Private runtime CI requires
a full reviewed SHA and the SDK-only App approval gate; skipped runtime checks do not pass.

## Docker verification

`make source` parses the required frozen lock, checks formatting/lint and compiles source using
public Docker tools without installing the SDK. It does not verify runtime types or tests.
After approved SDK access, `make check build verify image` uses the canonical Docker graph;
provide the short-lived token only with `DOCKER_BUILD_ARGS='--secret id=sdk_token,env=SDK_APP_TOKEN'`.
`check` runs strict static/unit checks once; `verify` freshly tests the installed wheel and any
enabled disposable PostgreSQL profile, with separate `coverage/installed/` reports. `make coverage`
reads current source reports without rerunning tests. Below 100% warns; assertions, types,
build/configuration/access and invalid/stale report errors fail.

Private CI is separate owner-only manual dispatch: actor and triggering actor serrja, full SHA
identical to the branch SHA and `SDK_BUILD_REVIEWED_SHA`, and the existing SDK-only App with
Contents read solely on pypokerlost. This solo-writer policy is not a server reviewer gate;
reassess before adding a writer. The owner activates the existing CI-only PR #2 and provisions
App repository secrets. Ordinary source CI success does not verify B1; a skipped/failed private
job fails manual acceptance. These commands do not merge, release or deploy to a remote cluster.
