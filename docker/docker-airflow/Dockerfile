# syntax=docker/dockerfile:1
# =============================================================================
# Apache Airflow Image for Docker Data ETL Platform (Ultra-Fast Build)
# =============================================================================
# This Dockerfile creates an Airflow image with:
# - Apache Airflow 2.10.4 (using official image)
# - Apache Spark 4.1.1 (copied from data-etl-spark-base, no re-download!)
# - PostgreSQL support
# - uv for package management (10-100x faster than pip!)
# - BuildKit cache mounts for faster rebuilds
# =============================================================================
# Build time:
#   First build: ~1-2 minutes (Spark copied from spark-base, no download!)
#   Rebuild: ~20-30 seconds (with cache) ⚡⚡⚡
# =============================================================================
# IMPORTANT: Requires data-etl-spark-base to be built first!
#   Run: make build-base && make build-spark-base
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install additional providers and dependencies
# -----------------------------------------------------------------------------
FROM apache/airflow:2.10.4-python3.12 AS airflow_builder

# Build arguments
ARG SPARK_VERSION=4.1.1
ARG AIRFLOW_VERSION=2.10.4
ARG PYSPARK_VERSION=3.5.3
ARG UV_VERSION=0.5.21

# Switch to root for installation
USER root

# Install additional system dependencies
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # For Spark
        openjdk-17-jre-headless \
        # Utilities
        rsync \
        netcat-openbsd

# Switch to airflow user for package installations
USER airflow

# Install uv - The fast Python package installer (10-100x faster than pip!)
RUN --mount=type=cache,target=/home/airflow/.cache/pip,sharing=locked,uid=50000,gid=0 \
    pip install "uv==${UV_VERSION}"

# Use official Airflow constraints for faster, conflict-free installation
ENV AIRFLOW_CONSTRAINTS_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"

# Install additional Airflow providers and dependencies using uv
# Note: Using PySpark 3.5.3 as required by Airflow 2.10.4 constraints
# Spark cluster runs 4.1.1 separately via SparkSubmitOperator
# Using BuildKit cache mount to cache uv packages (10-100x faster than pip!)
# Use --python to explicitly specify the Python interpreter
RUN --mount=type=cache,target=/home/airflow/.cache/uv,sharing=locked,uid=50000,gid=0 \
    uv pip install --python $(which python) --constraint "${AIRFLOW_CONSTRAINTS_URL}" \
        "apache-airflow-providers-apache-spark" \
        "pyspark==${PYSPARK_VERSION}" \
        redis \
        celery

# Copy and install DAG dependencies with uv
COPY docker/docker-airflow/requirements.txt /tmp/dag-requirements.txt
RUN --mount=type=cache,target=/home/airflow/.cache/uv,sharing=locked,uid=50000,gid=0 \
    uv pip install --python $(which python) -r /tmp/dag-requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final production image
# -----------------------------------------------------------------------------
FROM apache/airflow:2.10.4-python3.12

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL Airflow (Fast Build)" \
      org.opencontainers.image.description="Apache Airflow for ETL workflow orchestration" \
      org.opencontainers.image.version="2.10.4-fast" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Build arguments
ARG AIRFLOW_USER_HOME=/opt/airflow
ARG SPARK_VERSION=4.1.1
ARG HADOOP_VERSION=3

# Switch to root for setup
USER root

# Install runtime dependencies
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java runtime for Spark
        openjdk-17-jre-headless \
        # Utilities
        rsync \
        netcat-openbsd \
        vim \
        less

# Copy Spark from data-etl-spark-base (no re-download needed!)
# This avoids downloading Spark again (~400MB saved)
COPY --from=data-etl-spark-base:latest /usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /usr/local/spark

# Copy Python packages from builder
COPY --from=airflow_builder /home/airflow/.local /home/airflow/.local

# Environment variables
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME} \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__EXECUTOR=LocalExecutor \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
    SPARK_HOME=/usr/local/spark \
    PATH="/usr/local/spark/bin:${PATH}" \
    PYTHONPATH="${AIRFLOW_USER_HOME}/dags" \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    DEBIAN_FRONTEND=noninteractive \
    TERM=linux \
    LANGUAGE=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8

# Create Airflow directories (official image already has airflow user)
RUN mkdir -p \
        ${AIRFLOW_USER_HOME}/dags \
        ${AIRFLOW_USER_HOME}/logs \
        ${AIRFLOW_USER_HOME}/plugins && \
    chown -R airflow:root ${AIRFLOW_USER_HOME} /usr/local/spark && \
    chmod -R g+rw ${AIRFLOW_USER_HOME} /usr/local/spark

# Copy entrypoint script and configuration
COPY --chown=airflow:root docker/docker-airflow/scripts/entrypoint.sh /entrypoint.sh
COPY --chown=airflow:root docker/docker-airflow/config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

# Set permissions
RUN chmod +x /entrypoint.sh

# Switch to airflow user
USER airflow

WORKDIR ${AIRFLOW_USER_HOME}

# Expose Airflow webserver, flower, and worker ports
EXPOSE 8080 5555 8793

# Health check for Airflow webserver
# Note: 若容器執行 scheduler，請改用 airflow jobs check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl --fail http://localhost:8080/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]
