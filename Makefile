# =============================================================================
# Data ETL Platform - Makefile (Optimized)
# =============================================================================
# This Makefile provides convenient targets for building, running, and
# managing the Data ETL Docker platform.
# =============================================================================

# Project configuration
IMAGE_NAME := data-etl
DOCKER_FILE_DIR := docker
DOCKER_FILE_NAME := Dockerfile
DOCKER_COMPOSE_FILE := docker-compose.yml

# Build configuration
VERSION ?= latest
IMAGE_TAG ?= $(VERSION)
DOCKER_BUILD_FLAGS ?=
DOCKER_PROGRESS ?= auto

# Enable Docker BuildKit for faster builds with cache mount
export DOCKER_BUILDKIT=1

# Default target
.DEFAULT_GOAL := help

# =============================================================================
# Build Images
# =============================================================================

.PHONY: build-all build-all-parallel build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres

build-all: build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres ## build all images (sequential)

build-all-parallel: build-base ## build all images in parallel (faster, requires make -j)
	@echo "Building independent images in parallel..."
	@$(MAKE) -j3 build-notebook build-postgres build-spark-base
	@echo "Building dependent images..."
	@$(MAKE) -j3 build-spark-master build-spark-worker build-airflow

build-base: ## build base Python image
	@echo "Building base image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-base:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-base/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-base:$(IMAGE_TAG) $(IMAGE_NAME)-base:latest; \
	fi

build-spark-base: build-base ## build Spark base image (requires base)
	@echo "Building Spark base image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-spark-base:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-spark-base/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-spark-base:$(IMAGE_TAG) $(IMAGE_NAME)-spark-base:latest; \
	fi

build-spark-master: build-spark-base ## build Spark master image (requires spark-base)
	@echo "Building Spark master image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-spark-master:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-spark-master/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-spark-master:$(IMAGE_TAG) $(IMAGE_NAME)-spark-master:latest; \
	fi

build-spark-worker: build-spark-base ## build Spark worker image (requires spark-base)
	@echo "Building Spark worker image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-spark-worker:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-spark-worker/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-spark-worker:$(IMAGE_TAG) $(IMAGE_NAME)-spark-worker:latest; \
	fi

build-airflow: build-spark-base ## build Airflow image (requires spark-base)
	@echo "Building Airflow image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-airflow:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-airflow/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-airflow:$(IMAGE_TAG) $(IMAGE_NAME)-airflow:latest; \
	fi

build-notebook: ## build JupyterLab notebook image
	@echo "Building JupyterLab notebook image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-notebook:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-notebook/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-notebook:$(IMAGE_TAG) $(IMAGE_NAME)-notebook:latest; \
	fi

build-postgres: ## build PostgreSQL database image
	@echo "Building PostgreSQL image..."
	@docker build $(DOCKER_BUILD_FLAGS) --progress=$(DOCKER_PROGRESS) \
		-t $(IMAGE_NAME)-postgres:$(IMAGE_TAG) \
		-f $(DOCKER_FILE_DIR)/docker-postgres/$(DOCKER_FILE_NAME) .
	@if [ "$(IMAGE_TAG)" != "latest" ]; then \
		docker tag $(IMAGE_NAME)-postgres:$(IMAGE_TAG) $(IMAGE_NAME)-postgres:latest; \
	fi

# =============================================================================
# Rebuild Optimization
# =============================================================================

.PHONY: rebuild-airflow rebuild-notebook rebuild-spark-images

rebuild-airflow: ## rebuild only Airflow (faster if base unchanged)
	@docker build --progress=$(DOCKER_PROGRESS) -t $(IMAGE_NAME)-airflow \
		-f $(DOCKER_FILE_DIR)/docker-airflow/$(DOCKER_FILE_NAME) .

rebuild-notebook: ## rebuild only JupyterLab (faster if base unchanged)
	@docker build --progress=$(DOCKER_PROGRESS) -t $(IMAGE_NAME)-notebook \
		-f $(DOCKER_FILE_DIR)/docker-notebook/$(DOCKER_FILE_NAME) .

rebuild-spark-images: ## rebuild Spark master and workers only
	@$(MAKE) build-spark-master build-spark-worker

# =============================================================================
# Start Services
# =============================================================================

.PHONY: start up setup-connections

start: ## start all services with automatic connection setup (recommended)
	@echo "Starting all services with connection setup..."
	@bash scripts/start.sh

up: ## start all services without connection setup
	@echo "Starting all services..."
	@docker-compose up -d

setup-connections: ## setup Airflow connections (Spark & PostgreSQL)
	@echo "Setting up Airflow connections..."
	@bash scripts/setup-airflow-connections.sh

# =============================================================================
# Individual Services
# =============================================================================

.PHONY: up-postgres up-spark up-airflow up-notebook stop-postgres stop-spark stop-airflow stop-notebook

up-postgres: ## start only PostgreSQL
	@docker-compose up -d postgres

up-spark: ## start Spark cluster (master + 3 workers)
	@docker-compose up -d spark-master spark-worker-1 spark-worker-2 spark-worker-3

up-airflow: ## start Airflow (webserver + scheduler)
	@docker-compose up -d airflow airflow-scheduler

up-notebook: ## start JupyterLab
	@docker-compose up -d jupyterlab

stop-postgres: ## stop PostgreSQL
	@docker-compose stop postgres

stop-spark: ## stop Spark cluster
	@docker-compose stop spark-master spark-worker-1 spark-worker-2 spark-worker-3

stop-airflow: ## stop Airflow
	@docker-compose stop airflow airflow-scheduler

stop-notebook: ## stop JupyterLab
	@docker-compose stop jupyterlab

# =============================================================================
# Manage Services
# =============================================================================

.PHONY: down restart logs status ps

down: ## stop all services (keeps volumes)
	@docker-compose down

restart: ## restart all services
	@docker-compose restart

logs: ## view logs from all services (ctrl+c to exit)
	@docker-compose logs -f

status: ## show status of all services
	@docker-compose ps

ps: status ## alias for status

# =============================================================================
# Individual Service Logs
# =============================================================================

.PHONY: logs-airflow logs-spark logs-postgres logs-notebook logs-all

logs-airflow: ## view Airflow logs (webserver + scheduler)
	@docker-compose logs -f airflow airflow-scheduler

logs-spark: ## view Spark cluster logs
	@docker-compose logs -f spark-master spark-worker-1 spark-worker-2 spark-worker-3

logs-postgres: ## view PostgreSQL logs
	@docker-compose logs -f postgres

logs-notebook: ## view JupyterLab logs
	@docker-compose logs -f jupyterlab

logs-all: logs ## alias for logs

# =============================================================================
# Shell Access
# =============================================================================

.PHONY: shell-airflow shell-spark shell-notebook shell-postgres

shell-airflow: ## open bash shell in Airflow container
	@docker exec -it data-etl-airflow bash

shell-spark: ## open bash shell in Spark master container
	@docker exec -it data-etl-spark-master bash

shell-notebook: ## open bash shell in JupyterLab container
	@docker exec -it data-etl-jupyterlab bash

shell-postgres: ## open psql in PostgreSQL container
	@docker exec -it data-etl-postgres psql -U airflow -d airflow

# =============================================================================
# Validation & Health
# =============================================================================

.PHONY: validate health check-env check-images

validate: ## validate docker-compose configuration
	@docker-compose config > /dev/null && echo "✅ docker-compose.yml is valid"

health: ## check health status of all services
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "Detailed health checks:"
	@docker inspect --format='{{.Name}}: {{.State.Health.Status}}' $$(docker-compose ps -q) 2>/dev/null || echo "Some services don't have health checks"

check-env: ## check required environment variables
	@echo "Checking environment configuration..."
	@test -f .env && echo "✅ .env file exists" || echo "❌ .env file missing (create from .env.example)"
	@bash -c 'source .env 2>/dev/null && test -n "$$AIRFLOW_ADMIN_USERNAME" && echo "✅ AIRFLOW_ADMIN_USERNAME set" || echo "⚠️  AIRFLOW_ADMIN_USERNAME not set"'
	@bash -c 'source .env 2>/dev/null && test -n "$$AIRFLOW_ADMIN_PASSWORD" && echo "✅ AIRFLOW_ADMIN_PASSWORD set" || echo "⚠️  AIRFLOW_ADMIN_PASSWORD not set"'

check-images: ## check if all required images exist
	@echo "Checking if all images are built..."
	@docker image inspect $(IMAGE_NAME)-base:latest > /dev/null 2>&1 && echo "✅ base" || echo "❌ base (run: make build-base)"
	@docker image inspect $(IMAGE_NAME)-spark-base:latest > /dev/null 2>&1 && echo "✅ spark-base" || echo "❌ spark-base (run: make build-spark-base)"
	@docker image inspect $(IMAGE_NAME)-spark-master:latest > /dev/null 2>&1 && echo "✅ spark-master" || echo "❌ spark-master (run: make build-spark-master)"
	@docker image inspect $(IMAGE_NAME)-spark-worker:latest > /dev/null 2>&1 && echo "✅ spark-worker" || echo "❌ spark-worker (run: make build-spark-worker)"
	@docker image inspect $(IMAGE_NAME)-airflow:latest > /dev/null 2>&1 && echo "✅ airflow" || echo "❌ airflow (run: make build-airflow)"
	@docker image inspect $(IMAGE_NAME)-notebook:latest > /dev/null 2>&1 && echo "✅ notebook" || echo "❌ notebook (run: make build-notebook)"
	@docker image inspect $(IMAGE_NAME)-postgres:latest > /dev/null 2>&1 && echo "✅ postgres" || echo "❌ postgres (run: make build-postgres)"

# =============================================================================
# Cache Management
# =============================================================================

.PHONY: prune prune-all cache-size

prune: ## prune dangling build cache
	@echo "Pruning dangling build cache..."
	@docker builder prune -f

prune-all: ## prune all build cache (aggressive, requires confirmation)
	@echo "⚠️  WARNING: This will remove ALL build cache!"
	@echo "This will significantly slow down the next build."
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker builder prune -a -f; \
		echo "✅ All build cache removed"; \
	else \
		echo "❌ Cancelled"; \
	fi

cache-size: ## show BuildKit cache usage
	@echo "BuildKit cache usage:"
	@docker buildx du

# =============================================================================
# Cleanup
# =============================================================================

.PHONY: clean clean-images clean-containers clean-volumes clean-all

clean: down ## stop and remove containers (keeps images and volumes)
	@echo "✅ Containers stopped and removed"

clean-images: ## remove all project images
	@echo "Removing all project images..."
	@docker rmi -f \
		$(IMAGE_NAME)-base:latest \
		$(IMAGE_NAME)-spark-base:latest \
		$(IMAGE_NAME)-spark-master:latest \
		$(IMAGE_NAME)-spark-worker:latest \
		$(IMAGE_NAME)-airflow:latest \
		$(IMAGE_NAME)-notebook:latest \
		$(IMAGE_NAME)-postgres:latest \
		2>/dev/null || true
	@echo "✅ Images removed"

clean-containers: ## remove all stopped containers
	@echo "Removing stopped containers..."
	@docker container prune -f
	@echo "✅ Stopped containers removed"

clean-volumes: ## WARNING: remove all volumes (DATA LOSS!)
	@echo "⚠️  WARNING: This will DELETE ALL DATA VOLUMES!"
	@echo "This includes PostgreSQL data, Airflow metadata, and logs."
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		echo "✅ Volumes removed"; \
	else \
		echo "❌ Cancelled"; \
	fi

clean-all: clean-containers clean-images prune ## remove everything except volumes
	@echo "✅ Full cleanup complete (volumes preserved)"

# =============================================================================
# Quick Access URLs
# =============================================================================

.PHONY: urls open-airflow open-spark open-notebook notebook-token

urls: ## display service URLs
	@echo ""
	@echo "📋 Service URLs:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Airflow:    http://0.0.0.0:8282"
	@echo "  Spark UI:   http://0.0.0.0:8080"
	@echo "  JupyterLab: http://0.0.0.0:8888"
	@echo "  PostgreSQL: localhost:5432"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""

open-airflow: ## open Airflow UI in browser
	@open http://0.0.0.0:8282 2>/dev/null || xdg-open http://0.0.0.0:8282 2>/dev/null || echo "Please open http://0.0.0.0:8282 manually"

open-spark: ## open Spark UI in browser
	@open http://0.0.0.0:8080 2>/dev/null || xdg-open http://0.0.0.0:8080 2>/dev/null || echo "Please open http://0.0.0.0:8080 manually"

open-notebook: ## open JupyterLab in browser
	@open http://0.0.0.0:8888 2>/dev/null || xdg-open http://0.0.0.0:8888 2>/dev/null || echo "Please open http://0.0.0.0:8888 manually"

notebook-token: ## show JupyterLab server info and access token
	@docker exec -it data-etl-jupyterlab jupyter server list

# =============================================================================
# Help
# =============================================================================

.PHONY: help

help: ## display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n\033[1mData ETL Platform - Makefile\033[0m\n\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } END { printf "\n\033[2mTip: Use DOCKER_BUILDKIT=1 (enabled by default) for faster builds\033[0m\n\n" }' $(MAKEFILE_LIST)
