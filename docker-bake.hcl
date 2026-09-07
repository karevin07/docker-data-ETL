# =============================================================================
# docker-bake.hcl - build graph for the Data ETL image family
# =============================================================================
# The images form a chain (base -> spark-base -> spark-master/worker, and
# airflow copies the Spark distribution from spark-base). This file wires that
# graph with BuildKit named contexts ("target:...") instead of FROM <img>:latest,
# so the whole build is hermetic and BuildKit parallelises/prunes it for you.
#
# Usage:
#   docker buildx bake                    # build every image
#   docker buildx bake spark-worker       # build one image (+ its deps)
#   docker buildx bake spark              # build the "spark" group
#   docker buildx bake --print            # show the resolved plan, build nothing
#   docker buildx bake --set '*.no-cache=true'
#   TAG=v1 REGISTRY=ghcr.io/me/ docker buildx bake --push
#
# Version numbers live here so they are set in one place; the Dockerfiles keep
# matching ARG defaults for a plain `docker build`.
# NOTE: bumping SPARK_VERSION also needs SPARK_SHA512 updated in
#       docker/docker-spark-base/Dockerfile.
# =============================================================================

variable "REGISTRY" { default = "" }        # e.g. "ghcr.io/you/" (keep trailing slash)
variable "TAG" { default = "latest" }

variable "SPARK_VERSION" { default = "4.1.3" }
variable "HADOOP_VERSION" { default = "3" }
variable "PYSPARK_VERSION" { default = "3.5.3" }
variable "AIRFLOW_VERSION" { default = "2.10.4" }
variable "UV_VERSION" { default = "0.12.10" }

function "tags" {
  params = [name]
  result = TAG == "latest" ? ["${REGISTRY}data-etl-${name}:latest"] : ["${REGISTRY}data-etl-${name}:${TAG}", "${REGISTRY}data-etl-${name}:latest"]
}

group "default" {
  targets = ["base", "spark-base", "spark-master", "spark-worker", "airflow", "notebook", "postgres"]
}

group "spark" {
  targets = ["spark-master", "spark-worker"]
}

target "base" {
  context    = "."
  dockerfile = "docker/docker-base/Dockerfile"
  tags       = tags("base")
  args       = { UV_VERSION = UV_VERSION }
}

target "spark-base" {
  context    = "."
  dockerfile = "docker/docker-spark-base/Dockerfile"
  contexts   = { "data-etl-base" = "target:base" }
  tags       = tags("spark-base")
  args = {
    SPARK_VERSION  = SPARK_VERSION
    HADOOP_VERSION = HADOOP_VERSION
  }
}

target "spark-master" {
  context    = "."
  dockerfile = "docker/docker-spark-master/Dockerfile"
  contexts   = { "data-etl-spark-base" = "target:spark-base" }
  tags       = tags("spark-master")
}

target "spark-worker" {
  context    = "."
  dockerfile = "docker/docker-spark-worker/Dockerfile"
  contexts   = { "data-etl-spark-base" = "target:spark-base" }
  tags       = tags("spark-worker")
}

target "airflow" {
  context    = "."
  dockerfile = "docker/docker-airflow/Dockerfile"
  contexts   = { "data-etl-spark-base" = "target:spark-base" }
  tags       = tags("airflow")
  args = {
    SPARK_VERSION   = SPARK_VERSION
    HADOOP_VERSION  = HADOOP_VERSION
    PYSPARK_VERSION = PYSPARK_VERSION
    AIRFLOW_VERSION = AIRFLOW_VERSION
    UV_VERSION      = UV_VERSION
  }
}

target "notebook" {
  context    = "."
  dockerfile = "docker/docker-notebook/Dockerfile"
  tags       = tags("notebook")
  args       = { UV_VERSION = UV_VERSION }
}

target "postgres" {
  context    = "."
  dockerfile = "docker/docker-postgres/Dockerfile"
  tags       = tags("postgres")
}
