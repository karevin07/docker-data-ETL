IMAGE_NAME=data-etl
DOCKER_FILE_DIR=docker
DOCKER_FILE_NAME=Dockerfile
DOCKER_COMPOSE_FILE=docker-compose.yml

##@ Build Images

.PHONY: build-all build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres

build-all: build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres ## build all images

build-base: ## build base image
	@docker build -t $(IMAGE_NAME)-base -f $(DOCKER_FILE_DIR)/docker-base/$(DOCKER_FILE_NAME) .

build-spark-base: ## build spark base image
	@docker build -t $(IMAGE_NAME)-spark-base -f $(DOCKER_FILE_DIR)/docker-spark-base/$(DOCKER_FILE_NAME) .

build-spark-master: ## build spark master image
	@docker build -t $(IMAGE_NAME)-spark-master -f $(DOCKER_FILE_DIR)/docker-spark-master/$(DOCKER_FILE_NAME) .

build-spark-worker: ## build spark worker image
	@docker build -t $(IMAGE_NAME)-spark-worker -f $(DOCKER_FILE_DIR)/docker-spark-worker/$(DOCKER_FILE_NAME) .

build-airflow: ## build airflow image
	@docker build -t $(IMAGE_NAME)-airflow -f $(DOCKER_FILE_DIR)/docker-airflow/$(DOCKER_FILE_NAME) .

build-notebook: ## build notebook image
	@docker build -t $(IMAGE_NAME)-notebook -f $(DOCKER_FILE_DIR)/docker-notebook/$(DOCKER_FILE_NAME) .

build-postgres: ## build postgres image
	@docker build -t $(IMAGE_NAME)-postgres -f $(DOCKER_FILE_DIR)/docker-postgres/$(DOCKER_FILE_NAME) .

##@ Start Services

.PHONY: start up setup-connections

start: ## start all services with automatic connection setup (recommended)
	@bash scripts/start.sh

up: ## start all services without connection setup
	@docker-compose up -d

setup-connections: ## setup Airflow connections (Spark & PostgreSQL)
	@bash scripts/setup-airflow-connections.sh

##@ Manage Services

.PHONY: down restart logs status

down: ## stop all services
	@docker-compose down

restart: ## restart all services
	@docker-compose restart

logs: ## view logs from all services (ctrl+c to exit)
	@docker-compose logs -f

status: ## show status of all services
	@docker-compose ps

##@ Help

.PHONY: help

help: ## display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
