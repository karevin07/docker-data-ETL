# syntax=docker/dockerfile:1
# =============================================================================
# Spark Base Image for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates a Spark base image built on the data-etl-base image
# - Apache Spark 4.1.1 (latest stable with Hadoop 3)
# - Compatible with Python 3.12 and Scala 2.13
# - Optimized for distributed data processing
# =============================================================================

FROM data-etl-base:latest

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL Spark Base Image" \
      org.opencontainers.image.description="Apache Spark base image for distributed data processing" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Build arguments
ARG SPARK_VERSION=4.1.1
ARG HADOOP_VERSION=3
ARG WORKSPACE=/home/workspace
# SHA512 checksum for Spark 4.1.1 with Hadoop 3
# Verify at: https://archive.apache.org/dist/spark/spark-4.1.1/spark-4.1.1-bin-hadoop3.tgz.sha512
ARG SPARK_SHA512="8dd8d1fdc26c8c9cddf58de62e939e3a33c3c2cc3e5464ae4e3c71eda99db4ac2e04b11a5e1c0e3f1cf51c31a3bbe74e6f2866d58f1c8e48e2c0a2f38e6f1a5f"

# Switch to root for installation
USER root

# Environment variables for Spark
ENV SPARK_HOME=/usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} \
    SPARK_MASTER_HOST=spark \
    SPARK_MASTER_PORT=7077 \
    PYSPARK_PYTHON=python3.12 \
    PYSPARK_DRIVER_PYTHON=python3.12 \
    PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

WORKDIR /tmp

# Download and install Apache Spark with checksum verification
# Using --no-cache-dir and cleaning up in same layer to minimize image size
RUN curl -fsSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -o spark.tgz && \
    # Verify SHA512 checksum for security (protects against supply chain attacks)
    echo "${SPARK_SHA512}  spark.tgz" | sha512sum -c - && \
    # Extract Spark
    tar -xzf spark.tgz && \
    # Move to final location
    mv "spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /usr/bin/ && \
    # Create log directory
    mkdir -p "${SPARK_HOME}/logs" && \
    # Create aliases for convenience
    echo "alias pyspark='${SPARK_HOME}/bin/pyspark'" >> /etc/bash.bashrc && \
    echo "alias spark-shell='${SPARK_HOME}/bin/spark-shell'" >> /etc/bash.bashrc && \
    echo "alias spark-submit='${SPARK_HOME}/bin/spark-submit'" >> /etc/bash.bashrc && \
    # Set proper permissions
    chown -R etluser:etluser "${SPARK_HOME}" && \
    # Cleanup in same layer
    rm -rf /tmp/spark.tgz /tmp/*

# Copy Spark configuration template (if exists)
# COPY spark-defaults.conf ${SPARK_HOME}/conf/spark-defaults.conf

# Create necessary directories with proper permissions
RUN mkdir -p "${SPARK_HOME}/work" "${SPARK_HOME}/logs" "${WORKSPACE}" && \
    chown -R etluser:etluser "${SPARK_HOME}/work" "${SPARK_HOME}/logs" "${WORKSPACE}" && \
    # Fix python3 symlink to point to python3.12 (force overwrite)
    ln -sf /app/.venv/bin/python3.12 /bin/python3 && \
    ln -sf /app/.venv/bin/python3.12 /usr/bin/python3

WORKDIR ${SPARK_HOME}

# Switch back to non-root user
USER etluser

# Verify Spark installation
RUN spark-submit --version

# Health check for Spark installation
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD spark-submit --version > /dev/null 2>&1 || exit 1

CMD ["bash"]
