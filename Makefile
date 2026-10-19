ifneq ($(CONTAINERIZED),1)
QUALITY_DOCKERFILE := Dockerfile
QUALITY_IMAGE := authservice:quality
RUNTIME_IMAGE := authservice:candidate
QUALITY_TEST := test-unit
QUALITY_EXTRA_TARGETS :=

VERIFY_COMMAND = $(MAKE) CONTAINERIZED=1 test-image && $(QUALITY_RUN) python docker/coverage_report.py coverage/installed/coverage.json --after coverage/installed/.started --output coverage/installed/summary.md
verify: quality-image
include docker/quality-python.mk
SOURCE_REQUIRE_LOCK ?= true
.PHONY: source
source:
	$(DOCKER) buildx build --file Dockerfile.source --build-arg REQUIRE_LOCK=$(SOURCE_REQUIRE_LOCK) --target source --load --tag authservice:source $(QUALITY_BUILD_ARGS) .
	$(DOCKER) run --init --rm --read-only --network none --tmpfs /tmp:rw,mode=1777 --user "$$(id -u):$$(id -g)" authservice:source
else
.DEFAULT_GOAL := help
UV ?= uv

.PHONY: help install format lint typecheck test test-unit check build

help: ## Show the supported development commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the locked development environment.
	$(UV) sync --locked

format: ## Format owned Python sources.
	$(UV) run --locked ruff check --fix .
	$(UV) run --locked ruff format .

lint: ## Check formatting and lint without modifying files.
	$(UV) run --locked ruff check .
	$(UV) run --locked ruff format --check .

typecheck: ## Check strict Python types.
	$(UV) run --locked mypy

test-unit: ## Run isolated tests and complete Python coverage.
	$(UV) run --locked pytest --cov --cov-report=term-missing --cov-report=json --cov-report=xml

test: ## Measure integration and isolated tests together without stale coverage.
	$(UV) run --locked python -m coverage run -m pytest tests/foundation/database_integration.py $(wildcard tests/*_integration.py) $(INTEGRATION_TEST_PATHS)
	$(UV) run --locked pytest --cov --cov-append --cov-report=term-missing --cov-report=json --cov-report=xml


check: lint typecheck test-unit ## Run the mandatory non-mutating checks.
	$(UV) lock --check

build: ## Export the wheel and sdist from the canonical container build.
	docker buildx build $(DOCKER_BUILD_ARGS) --target artifacts --output type=local,dest=dist .

.PHONY: image
image: ## Build and load the immutable runtime candidate locally.
	@mkdir -p dist
	docker buildx build $(DOCKER_BUILD_ARGS) --target runtime --load --tag authservice:candidate --metadata-file dist/image-build.json .

.PHONY: run

HTTP_HOST ?= 127.0.0.1
HTTP_PORT ?= 8000
UVICORN_FLAGS ?=

run: ## Run the application on loopback without rebuilding.
	$(UV) run --locked uvicorn authservice.app:create_app --factory --host "$(HTTP_HOST)" --port "$(HTTP_PORT)" $(UVICORN_FLAGS)

.PHONY: test-integration
test-integration: ## Verify real PostgreSQL; TEST_DATABASE_URL must point to a disposable DB.
	$(UV) run --locked pytest tests/foundation/database_integration.py $(wildcard tests/*_integration.py) $(INTEGRATION_TEST_PATHS)

.PHONY: test-image
test-image: ## Run installed-wheel tests in a disposable container and, when enabled, PostgreSQL.
	@mkdir -p coverage/installed
	docker buildx build $(DOCKER_BUILD_ARGS) --target test --load --tag authservice:test .
	@touch coverage/installed/.started
	@set -eu; project="authservicetest$$(date +%s)$$$$"; \
	trap 'docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" down --volumes --remove-orphans' EXIT HUP INT TERM; \
	TEST_UID="$$(id -u)" TEST_GID="$$(id -g)" docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" up --abort-on-container-exit --exit-code-from tests tests

HELM ?= helm
KIND ?= kind
KUBECTL ?= kubectl
KUBECONFIG_LOCAL ?= $(CURDIR)/.local/kubeconfig
KIND_IMAGE := kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5

.PHONY: chart chart-check
chart: ## Package the managed shared chart as a deployable artifact.
	$(HELM) package deploy/chart --destination dist

chart-check: ## Check chart templates and schema with explicit validation-only values.
	$(HELM) lint deploy/chart --strict --set image.repository=validation.invalid/application --set image.digest=sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

.PHONY: deploy-local undeploy-local
deploy-local: image ## Create a disposable Kind contour; no external kubeconfig is used.
	@mkdir -p .local
	$(KIND) create cluster --name authservice-local --image $(KIND_IMAGE) --kubeconfig $(KUBECONFIG_LOCAL) --wait 180s
	$(KIND) load docker-image authservice:candidate --name authservice-local
	$(KUBECTL) --kubeconfig $(KUBECONFIG_LOCAL) --context kind-authservice-local create namespace foundation
	docker pull postgres:17.11-trixie@sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3
	docker tag postgres:17.11-trixie@sha256:2d2b8998d31037bf721cfdf764d76ba74171b4fab3431b7f72c27c56ddbdf9e3 foundation-postgres:local-2d2b8998d310
	$(KIND) load docker-image foundation-postgres:local-2d2b8998d310 --name authservice-local
	$(KUBECTL) --kubeconfig $(KUBECONFIG_LOCAL) --context kind-authservice-local -n foundation apply -f deploy/local/postgres.yaml
	$(KUBECTL) --kubeconfig $(KUBECONFIG_LOCAL) --context kind-authservice-local -n foundation rollout status deployment/foundation-database --timeout=120s
	$(HELM) upgrade --install authservice deploy/chart --kubeconfig $(KUBECONFIG_LOCAL) --kube-context kind-authservice-local --namespace foundation --wait --timeout 120s --rollback-on-failure --values deploy/values.yaml --set image.repository=authservice --set image.tag=candidate --set localDevelopment=true --set database.secretName=foundation-database --set migration.enabled=true

undeploy-local: ## Delete only this application's disposable Kind cluster.
	$(KIND) delete cluster --name authservice-local


# Project-owned commands survive Copier updates without copying shared recipes.
-include Makefile.local

endif
