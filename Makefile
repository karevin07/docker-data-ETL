IMAGE_NAME=data-etl
DOCKER_FILE_DIR=docker
DOCKER_FILE_NAME=Dockerfile.new
DOCKER_FILE_NAME_TMP=Dockerfile
DOCKERC_COMPOSE_FILE=docker-compose-new.yml

##@ Docker build images
.PHONY: build-all build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres

build-all:| build-base  build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres ## build all

build-base: ## build base image
	@echo "docker build -t $(IMAGE_NAME)-base -f $(DOCKER_FILE_DIR)/docker-base/$(DOCKER_FILE_NAME) ."
	@docker build -t $(IMAGE_NAME)-base -f $(DOCKER_FILE_DIR)/docker-base/$(DOCKER_FILE_NAME) .

build-spark-base: ## build spark base image
	@echo "docker build -t $(IMAGE_NAME)-spark-base -f $(DOCKER_FILE_DIR)/docker-spark-base/$(DOCKER_FILE_NAME_TMP) ."
	@docker build -t $(IMAGE_NAME)-spark-base -f $(DOCKER_FILE_DIR)/docker-spark-base/$(DOCKER_FILE_NAME_TMP) .

build-spark-master: ## build spark master image
	@echo "docker build -t $(IMAGE_NAME)-spark-master -f $(DOCKER_FILE_DIR)/docker-spark-master/$(DOCKER_FILE_NAME_TMP) ."
	@docker build -t $(IMAGE_NAME)-spark-master -f $(DOCKER_FILE_DIR)/docker-spark-master/$(DOCKER_FILE_NAME_TMP) .

build-spark-worker: ## build spark worker image
	@echo "docker build -t $(IMAGE_NAME)-spark-worker -f $(DOCKER_FILE_DIR)/docker-spark-worker/$(DOCKER_FILE_NAME_TMP) ."
	@docker build -t $(IMAGE_NAME)-spark-worker -f $(DOCKER_FILE_DIR)/docker-spark-worker/$(DOCKER_FILE_NAME_TMP) .

build-airflow: ## build airflow image
	@echo "docker build -t $(IMAGE_NAME)-airflow -f $(DOCKER_FILE_DIR)/docker-airflow/$(DOCKER_FILE_NAME) ."
	@docker build -t $(IMAGE_NAME)-airflow -f $(DOCKER_FILE_DIR)/docker-airflow/$(DOCKER_FILE_NAME) .

build-notebook: ## build notebook image
	@echo "docker build -t $(IMAGE_NAME)-notebook -f $(DOCKER_FILE_DIR)/docker-notebook/$(DOCKER_FILE_NAME_TMP) ."
	@docker build -t $(IMAGE_NAME)-notebook -f $(DOCKER_FILE_DIR)/docker-notebook/$(DOCKER_FILE_NAME_TMP) .

build-postgres: ## build postgres image
	@echo "docker build -t $(IMAGE_NAME)-postgres -f $(DOCKER_FILE_DIR)/docker-postgres/$(DOCKER_FILE_NAME_TMP) ."
	@docker build -t $(IMAGE_NAME)-postgres -f $(DOCKER_FILE_DIR)/docker-postgres/$(DOCKER_FILE_NAME_TMP) .

##@ Docker run containers

.PHONY: run-all run-spark run-airflow run-notebook

run-all:| run-spark run-airflow run-notebook ## run all

run-spark: ## run spark cluster
	@echo "docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d spark-master spark-worker"
	@docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d spark-master spark-worker

run-airflow: ## run airflow
	@echo "docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d airflow-web"
	@docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d airflow-web

run-notebook: ## run notebook
	@echo "docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d notebook"
	@docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} up -d notebook

##@ Docker stop containers

.PHONY: down

down: ## stop all service
	@echo "docker-compose -p ${IMAGE_NAME} ${DOCKERC_COMPOSE_FILE} down"
	@docker-compose -p ${IMAGE_NAME} -f ${DOCKERC_COMPOSE_FILE} down

.PHONY: help
##@ Help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
