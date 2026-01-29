# syntax=docker/dockerfile:1
# =============================================================================
# Apache Airflow Image for Docker Data ETL Platform (Ultra-Fast Build)
# =============================================================================
# This Dockerfile creates an Airflow image with:
# - Apache Airflow 2.10.4 (using official image - MUCH FASTER!)
# - Apache Spark 4.1.1 integration
# - PostgreSQL support
# - Optimized for minimal build time
# =============================================================================
# Build time: ~1-2 minutes (vs 10-17 minutes with manual installation)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Spark Downloader - Cache Spark separately for reuse
# -----------------------------------------------------------------------------
FROM alpine:3.21 AS spark_downloader

ARG SPARK_VERSION=4.1.1
ARG HADOOP_VERSION=3

WORKDIR /tmp

# Download and extract Spark in a separate stage for better caching
RUN apk add --no-cache curl tar && \
    curl -fsSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -o spark.tgz && \
    tar -xzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /spark && \
    rm spark.tgz

# -----------------------------------------------------------------------------
# Stage 2: Builder - Install additional providers and dependencies
# -----------------------------------------------------------------------------
FROM apache/airflow:2.10.4-python3.12 AS airflow_builder

# Build arguments
ARG SPARK_VERSION=4.1.1
ARG AIRFLOW_VERSION=2.10.4
ARG PYSPARK_VERSION=3.5.3

# Switch to root for installation
USER root

# Install additional system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # For Spark
        openjdk-17-jre-headless \
        # Utilities
        rsync \
        netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch to airflow user for pip installations
USER airflow

# Use official Airflow constraints for faster, conflict-free installation
ENV AIRFLOW_CONSTRAINTS_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"

# Install additional Airflow providers and dependencies using constraints
# Note: Using PySpark 3.5.3 as required by Airflow 2.10.4 constraints
# Spark cluster runs 4.1.1 separately via SparkSubmitOperator
RUN pip install --no-cache-dir --constraint "${AIRFLOW_CONSTRAINTS_URL}" \
        "apache-airflow-providers-apache-spark" \
        "pyspark==${PYSPARK_VERSION}" \
        redis \
        celery

# Copy and install DAG dependencies
COPY docker/docker-airflow/requirements.txt /tmp/dag-requirements.txt
RUN pip install --no-cache-dir -r /tmp/dag-requirements.txt

# -----------------------------------------------------------------------------
# Stage 3: Runtime - Final production image
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
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java runtime for Spark
        openjdk-17-jre-headless \
        # Utilities
        rsync \
        netcat-openbsd \
        vim \
        less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Spark from downloader stage
COPY --from=spark_downloader /spark /usr/local/spark

# Copy Python packages from builder
COPY --from=airflow_builder /home/airflow/.local /home/airflow/.local

# Environment variables
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME} \
    AIRFLOW__CORE__LOAD_EXAMPLES=False \
    AIRFLOW__CORE__EXECUTOR=LocalExecutor \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow \
    SPARK_HOME=/usr/local/spark \
    PATH="/usr/local/spark/bin:${PATH}" \
    PYTHONPATH="${PYTHONPATH}:${AIRFLOW_USER_HOME}/dags" \
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
