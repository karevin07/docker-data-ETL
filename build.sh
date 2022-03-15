#!/bin/bash

NAME=$1
IMAGE_NAME="data-etl"
DOCKER_FILE_DIR="docker"
TAG=data-etl-${NAME}

echo ${TAG}

build() {
    docker build -t ${TAG} -f ${DOCKER_FILE_DIR}/docker-${NAME}/Dockerfile .
    echo "docker build -t ${TAG} -f ${DOCKER_FILE_DIR}/docker-${NAME}/Dockerfile ."
}

build ${NAME}