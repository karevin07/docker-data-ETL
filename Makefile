IMAGE_NAME=data-etl
DOCKER_FILE_DIR=docker

##@ Docker build images
.PHONY: build-all build-base build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres

build-all:| build-base  build-spark-base build-spark-master build-spark-worker build-airflow build-notebook build-postgres ## build all

build-base: ## build base image
	@echo "docker build -t $(IMAGE_NAME)-base -f $(DOCKER_FILE_DIR)/docker-base/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-base -f $(DOCKER_FILE_DIR)/docker-base/Dockerfile .

build-spark-base: ## build spark base image
	@echo "docker build -t $(IMAGE_NAME)-spark-base -f $(DOCKER_FILE_DIR)/docker-spark-base/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-spark-base -f $(DOCKER_FILE_DIR)/docker-spark-base/Dockerfile .

build-spark-master: ## build spark master image
	@echo "docker build -t $(IMAGE_NAME)-spark-master -f $(DOCKER_FILE_DIR)/docker-spark-master/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-spark-master -f $(DOCKER_FILE_DIR)/docker-spark-master/Dockerfile .

build-spark-worker: ## build spark worker image
	@echo "docker build -t $(IMAGE_NAME)-spark-worker -f $(DOCKER_FILE_DIR)/docker-spark-worker/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-spark-worker -f $(DOCKER_FILE_DIR)/docker-spark-worker/Dockerfile .

build-airflow: ## build airflow image
	@echo "docker build -t $(IMAGE_NAME)-airflow -f $(DOCKER_FILE_DIR)/docker-airflow/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-airflow -f $(DOCKER_FILE_DIR)/docker-airflow/Dockerfile .

build-notebook: ## build notebook image
	@echo "docker build -t $(IMAGE_NAME)-notebook -f $(DOCKER_FILE_DIR)/docker-notebook/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-notebook -f $(DOCKER_FILE_DIR)/docker-notebook/Dockerfile .

build-postgres: ## build postgres image
	@echo "docker build -t $(IMAGE_NAME)-postgres -f $(DOCKER_FILE_DIR)/docker-postgres/Dockerfile ."
	@docker build -t $(IMAGE_NAME)-postgres -f $(DOCKER_FILE_DIR)/docker-postgres/Dockerfile .

.PHONY: help
##@ Help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help
