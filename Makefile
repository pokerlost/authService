ifeq ($(CONTAINERIZED),1)
RUFF ?= ruff
else
RUFF ?= uvx --from ruff==0.16.4 ruff
endif
# Quick dev commands never prepare a product/build image.
ifneq ($(filter lint format format-check check,$(MAKECMDGOALS)),)
override CONTAINERIZED := 1
endif
ifneq ($(CONTAINERIZED),1)
QUALITY_IMAGE := authservice:quality
# Generated check owns its complete graph; opt into extras only when defined.
QUALITY_EXTRA_TARGETS :=
BUILD_DOCKERFILE := Dockerfile.quality
QUALITY_RUN_ARGS += --env TEST_DATABASE_URL --env DATABASE_URL
INSTALLED_TEST_IMAGE := authservice:test
# Keep prior rollback artifacts; every checked source owns a separate directory.
PYTHON_ARTIFACT_DIR = dist/$(shell sed -n 's/.*"contentSha256":"\([a-f0-9]*\)".*/\1/p' $(REPORT_DIR)/source.json)
ifeq ($(OFFLINE),1)
BUILD_COMMAND = $(RELEASE_CHECK_COMMAND)
else
BUILD_COMMAND = $(DOCKER) buildx build --file $(BUILD_DOCKERFILE) $(DOCKER_BUILD_ARGS) $(LOCAL_BUILD_NETWORK) --target $(ARTIFACT_TARGET) --output type=local,dest=$(PYTHON_ARTIFACT_DIR) .
endif
BUILD_RECEIPT_COMMAND = $(QUALITY_RUN) python docker/release.py capture-build --artifact-dir "$(PYTHON_ARTIFACT_DIR)"
RELEASE_CHECK_COMMAND = $(QUALITY_RUN) python docker/release.py release-check --artifact-dir "$(PYTHON_ARTIFACT_DIR)"
OFFLINE_PREFLIGHT_COMMAND = $(MAKE) python-offline-preflight database-offline-preflight
.PHONY: database-offline-preflight
database-offline-preflight:
	@images="$$(docker compose --env-file /dev/null -f compose.test.yaml config --images)" || exit 2; \
	  test -n "$$images" || exit 2; \
	  printf "%s\n" "$$images" | while IFS= read -r image; do docker image inspect "$$image" >/dev/null || { echo "BLOCKED: prepare the Compose images online first." >&2; exit 2; }; done
QUALITY_TEST_COMMAND = $(MAKE) source-tests QUALITY_TEST="$(QUALITY_TEST)"
.PHONY: source-tests
source-tests: ## Run source checks against a unique disposable Compose database.
	@set -eu; project="authservicesource$$(date +%s)$$$$"; \
	trap 'docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" down --volumes --remove-orphans' EXIT HUP INT TERM; \
	UV_OFFLINE="$(if $(filter 1,$(OFFLINE)),true,false)" TEST_UID="$$(id -u)" TEST_GID="$$(id -g)" QUALITY_TEST="$(QUALITY_TEST)" docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" up $(if $(filter 1,$(OFFLINE)),--pull never,) --abort-on-container-exit --exit-code-from quality quality

.PHONY: run
run:
	$(MAKE) CONTAINERIZED=1 run
QUALITY_EXTRA_TARGETS := chart-check
CI_LOCAL_TARGETS := acceptance coverage build verify chart release-check
VERSION_COMMAND = $(QUALITY_RUN) python -m docker.chart_release version
RELEASE_CHECK_COMMAND = $(QUALITY_RUN) python -m docker.chart_release release-check --artifact-dir "$(PYTHON_ARTIFACT_DIR)"
.PHONY: chart
chart: quality-image
	$(QUALITY_RUN) make chart ARTIFACT_DIR="$(PYTHON_ARTIFACT_DIR)"

QUALITY_DOCKERFILE := Dockerfile
BUILD_DOCKERFILE := $(QUALITY_DOCKERFILE)
RUNTIME_IMAGE := authservice:candidate

VERIFY_COMMAND = $(if $(filter 1,$(OFFLINE)),$(OFFLINE_PREFLIGHT_COMMAND) &&,) $(MAKE) CONTAINERIZED=1 test-image && $(QUALITY_RUN) python docker/coverage_report.py coverage/installed/coverage.json --after coverage/installed/.started --output coverage/installed/summary.md
verify: quality-image
.PHONY: chart deploy-local undeploy-local
deploy-local undeploy-local:
	$(MAKE) CONTAINERIZED=1 $@


SOURCE_REQUIRE_LOCK ?= true
.PHONY: source
source:
	$(DOCKER) buildx build --file Dockerfile.source --build-arg REQUIRE_LOCK=$(SOURCE_REQUIRE_LOCK) --target source --load --tag authservice:source $(QUALITY_BUILD_ARGS) .
	$(DOCKER) run --init --rm --read-only --network none --tmpfs /tmp:rw,mode=1777 --user "$$(id -u):$$(id -g)" authservice:source

QUALITY_EXTRA_TARGETS += acceptance
CI_LOCAL_TARGETS ?= acceptance coverage build verify release-check
include docker/quality-python.mk
else
.DEFAULT_GOAL := help
UV ?= uv

.PHONY: help install format lint typecheck test test-unit check build

help: ## Show the supported development commands.
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_-]+:.*## / {printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the locked development environment.
	$(UV) sync --locked

format: ## Format owned Python sources.
	$(RUFF) check --fix .
	$(RUFF) format .

lint: ## Check formatting and lint without modifying files.
	$(RUFF) check .
	$(RUFF) format --check .

typecheck: ## Check strict Python types.
	$(UV) run --locked mypy

test-unit: ## Run isolated tests and complete Python coverage.
	$(UV) run --locked pytest --junitxml=coverage/junit.xml --cov --cov-report=term-missing --cov-report=json --cov-report=xml

test: ## Measure integration and isolated tests together without stale coverage.
	$(UV) run --locked python -m coverage run -m pytest --junitxml=coverage/integration.xml tests/foundation/database_integration.py $(wildcard tests/*_integration.py) $(INTEGRATION_TEST_PATHS)
	$(UV) run --locked pytest --junitxml=coverage/junit.xml --cov --cov-append --cov-report=term-missing --cov-report=json --cov-report=xml


check: lint ## Fast lint-only gate; no tests/build.

acceptance: lint typecheck test ## Run the mandatory non-mutating checks.
	$(UV) lock --check

build: ## Export the wheel and sdist from the canonical container build.
	$(UV) build --no-build-isolation --wheel --sdist

.PHONY: image
image: ## Build and load the immutable runtime candidate locally.
	@mkdir -p dist
	docker buildx build $(DOCKER_BUILD_ARGS) $(LOCAL_BUILD_NETWORK) --target runtime --load --tag authservice:candidate --metadata-file dist/image-build.json .

.PHONY: run

HTTP_HOST ?= 127.0.0.1
HTTP_PORT ?= 8000
UVICORN_FLAGS ?=

run: ## Run the application on loopback without rebuilding.
	$(UV) run --locked uvicorn authservice.app:create_app --factory --host "$(HTTP_HOST)" --port "$(HTTP_PORT)" --no-server-header --no-access-log --log-config app_logging.json --workers 1 $(UVICORN_FLAGS)

.PHONY: test-integration
test-integration: ## Verify real PostgreSQL; TEST_DATABASE_URL must point to a disposable DB.
	$(UV) run --locked pytest tests/foundation/database_integration.py $(wildcard tests/*_integration.py) $(INTEGRATION_TEST_PATHS)

.PHONY: test-image
test-image: ## Run installed-wheel tests in a disposable container and, when enabled, PostgreSQL.
	@mkdir -p coverage/installed
ifneq ($(OFFLINE),1)
	docker buildx build $(DOCKER_BUILD_ARGS) $(LOCAL_BUILD_NETWORK) --file Dockerfile --target test --load --tag authservice:test .
endif
	@touch coverage/installed/.started
	@set -eu; project="authservicetest$$(date +%s)$$$$"; \
	trap 'docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" down --volumes --remove-orphans' EXIT HUP INT TERM; \
	UV_OFFLINE="$(if $(filter 1,$(OFFLINE)),true,false)" TEST_UID="$$(id -u)" TEST_GID="$$(id -g)" docker compose --env-file /dev/null -f compose.test.yaml -p "$$project" up $(if $(filter 1,$(OFFLINE)),--pull never,) --abort-on-container-exit --exit-code-from tests tests
	@cp coverage/source.json coverage/installed/source.json
	@docker image inspect authservice:test --format '{{.Id}}' > coverage/installed/test-image-id.txt

ARTIFACT_DIR ?= dist
HELM ?= helm
KIND ?= kind
KUBECTL ?= kubectl
KUBECONFIG_LOCAL ?= $(CURDIR)/.local/kubeconfig
KIND_IMAGE := kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5

.PHONY: chart chart-check
acceptance: chart-check
chart: ## Package the managed shared chart as a deployable artifact.
	$(HELM) package deploy/chart --destination "$(ARTIFACT_DIR)/charts" --app-version "$$($(UV) run --locked python -m docker.chart_release app-version)"
	$(UV) run --locked python -m docker.chart_release capture --artifact-dir "$(ARTIFACT_DIR)"

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

.PHONY: dev-policy-help
help: dev-policy-help
dev-policy-help:
	@printf '%s\n' 'Daily: make lint; explicit git push origin dev.' \
	  'Manual only: test, typecheck, coverage, build, acceptance, ci-local.' \
	  'Native lint tools must be installed; lint never syncs/builds the application.'
