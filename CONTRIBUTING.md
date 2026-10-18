# Contributing to authService

Review HTTP paths, operation IDs, environment names and migration effects. Preserve application-owned documents, settings, historical migrations, seed tests and deployment values during Copier updates.

After a fresh render, resolve and commit `uv.lock`. Existing checkouts use `make install` with that lock. Run `make lint`, `make typecheck`, `make test-unit` and `make test`, then `make build`. Full tests require `TEST_DATABASE_URL` for disposable PostgreSQL; missing access is a failure, not a skip. `make test-image` also tests the installed wheel in the canonical container. Run `make chart-check chart` and test the packaged deployment in a disposable cluster.

Record actual statement/branch counts, artifact identities and failed or unavailable checks in the PR. A build does not authorize registry publication, release or production deployment.

The shared Markdown checker and its tests are maintained in `serrja/pythonTemplate`.
`documentation-tool.lock.json` pins the reviewed source and file hashes. Refresh these
managed snapshots from that owner; the checker retains Python 3.12 syntax so all consumers
use the same implementation. This tooling is separate from the generated Copier tree.
