# syntax=docker/dockerfile:1
# =============================================================================
# Spark Base Image for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates a Spark base image built on the data-etl-base image
# - Apache Spark 4.1.3 (latest stable with Hadoop 3)
# - Compatible with Python 3.12 (Spark bundles its own Scala 2.13 runtime)
# - Optimized for distributed data processing
# =============================================================================

# "data-etl-base" resolves to the local data-etl-base:latest image, or to the
# "base" bake target when built via docker-bake.hcl (named build context).
FROM data-etl-base

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL Spark Base Image" \
      org.opencontainers.image.description="Apache Spark base image for distributed data processing" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Build arguments
ARG SPARK_VERSION=4.1.3
ARG HADOOP_VERSION=3
ARG WORKSPACE=/home/workspace
# SHA512 checksum for Spark 4.1.3 with Hadoop 3
# Verify at: https://archive.apache.org/dist/spark/spark-4.1.3/spark-4.1.3-bin-hadoop3.tgz.sha512
ARG SPARK_SHA512="391d04f40da0f6e961513d1ad72a6e3d51aef99f751c835e058a329b01369d83d17c2a9c68fad6be9496eea6687107d0d3d6893f7a53f53ddbfe669022220523"

# Switch to root for installation
USER root

# Environment variables for Spark
# Define SPARK_HOME first, then PATH can reference it in a separate ENV
ENV SPARK_HOME=/usr/bin/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} \
    SPARK_MASTER_HOST=spark \
    SPARK_MASTER_PORT=7077 \
    PYSPARK_PYTHON=python3.12 \
    PYSPARK_DRIVER_PYTHON=python3.12

ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

WORKDIR /tmp

# Spark download mirror. downloads.apache.org (CDN, currently-supported releases)
# is fast; archive.apache.org keeps every release but heavily rate-limits and
# Apache asks that it not be used for automated builds - so it is only the
# fallback. Override with --build-arg / bake for an internal mirror.
ARG SPARK_MIRRORS="https://downloads.apache.org/spark https://archive.apache.org/dist/spark"

# Download and install Apache Spark with checksum verification.
# The tarball is cached across builds via the cache mount; the cached copy is
# re-validated against SPARK_SHA512 every build, so a truncated/stale download
# is re-fetched (and a fresh download lands atomically via a .part rename).
RUN --mount=type=cache,target=/tmp/downloads,sharing=locked \
    SPARK_TGZ="spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" && \
    CACHED="/tmp/downloads/${SPARK_TGZ}" && \
    if ! echo "${SPARK_SHA512}  ${CACHED}" | sha512sum -c - >/dev/null 2>&1; then \
        rm -f "${CACHED}" && \
        for base in ${SPARK_MIRRORS}; do \
            echo "Fetching ${base}/spark-${SPARK_VERSION}/${SPARK_TGZ}" && \
            curl -fSL --retry 3 --retry-delay 2 \
                "${base}/spark-${SPARK_VERSION}/${SPARK_TGZ}" -o "${CACHED}.part" && \
            mv "${CACHED}.part" "${CACHED}" && break; \
        done; \
    fi && \
    # Verify SHA512 checksum for security (protects against supply chain attacks)
    echo "${SPARK_SHA512}  ${CACHED}" | sha512sum -c - && \
    # Extract to the final location
    tar -xzf "${CACHED}" -C /tmp && \
    mv "/tmp/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}" /usr/bin/ && \
    mkdir -p "${SPARK_HOME}/logs" && \
    # Convenience aliases for interactive shells
    printf "%s\n" \
        "alias pyspark='${SPARK_HOME}/bin/pyspark'" \
        "alias spark-shell='${SPARK_HOME}/bin/spark-shell'" \
        "alias spark-submit='${SPARK_HOME}/bin/spark-submit'" >> /etc/bash.bashrc && \
    chown -R etluser:etluser "${SPARK_HOME}"

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

# No HEALTHCHECK: intermediate image. spark-master / spark-worker define their own.
CMD ["bash"]
