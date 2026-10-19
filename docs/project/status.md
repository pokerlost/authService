# Current status

`authService` is a template-derived infrastructure foundation. The installed package is `src/authservice/`; the old flat `app/` runtime was retired after its previous foundation cleanup. `GET /`, `GET /getOpenApi`, `/health/live`, and `/health/ready` are the only registered paths. No token issuance, principal/grant persistence, verifier implementation, business operation, or subject table is active.

The existing SDK contains future-facing client contracts; they do not prove corresponding server routes exist. The empty scope catalog and verifier boundary remain fail-closed. PostgreSQL is configured for this service; readiness returns 503 when its required connection fails.

Historical revisions are retained unchanged under `migrations/versions/` and may create old tables on a new database. The file migration and revision graph can be checked without a database; actual upgrade/readiness success requires a separate disposable PostgreSQL instance. Existing Docker/Helm files are adapted to the package path but need a permitted image/chart run before deployment claims. No release or remote publication is implied.
