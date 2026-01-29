# syntax=docker/dockerfile:1
# =============================================================================
# Base Python Image for Docker Data ETL Platform (Fast Build Version)
# =============================================================================
# This multi-stage Dockerfile creates an optimized base image with:
# - Python 3.12.12 (official Docker image - MUCH FASTER!)
# - Scala 2.13.18 (latest 2.13.x compatible with Spark 4.x)
# - Poetry for dependency management
# - OpenJDK 17 (required for Spark 4.x)
# =============================================================================
# Build time: ~2-3 minutes (vs 15-20 minutes with source compilation)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.12.12-slim-bookworm AS builder

# Build arguments for version management
ARG SCALA_VERSION=2.13.18
ARG POETRY_VERSION=1.8.5

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies and Java
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Build tools
        build-essential \
        gcc \
        git \
        wget \
        curl \
        ca-certificates \
        # Java (Debian Bookworm has OpenJDK 17)
        openjdk-17-jdk-headless \
        # Locale support
        locales \
        # Snappy compression for Spark
        libsnappy-dev && \
    # Generate locale
    locale-gen en_US.UTF-8 && \
    # Cleanup in same layer
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Scala
WORKDIR /tmp
RUN wget -q "https://github.com/scala/scala/releases/download/v${SCALA_VERSION}/scala-${SCALA_VERSION}.tgz" && \
    tar -xzf "scala-${SCALA_VERSION}.tgz" && \
    mkdir -p /usr/local/scala && \
    mv "scala-${SCALA_VERSION}"/* /usr/local/scala/ && \
    rm -rf "scala-${SCALA_VERSION}" "scala-${SCALA_VERSION}.tgz"

# Upgrade pip and install Poetry
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Configure Poetry
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install Python dependencies from pyproject.toml
WORKDIR /app
COPY pyproject.toml ./
RUN poetry install --only main --no-root --no-cache && \
    rm -rf /tmp/poetry_cache

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.12.12-slim-bookworm

# Metadata labels following OCI standards
LABEL org.opencontainers.image.title="Data ETL Base Image" \
      org.opencontainers.image.description="Base Python image with Scala for ETL workflows" \
      org.opencontainers.image.version="2.0.0-fast" \
      org.opencontainers.image.authors="Kelvin Liao" \
      org.opencontainers.image.licenses="MIT" \
      maintainer="Kelvin Liao"

# Build arguments
ARG WORKSPACE=/home/workspace
ARG APP_USER=etluser
ARG APP_UID=1000
ARG APP_GID=1000

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SCALA_HOME=/usr/local/scala \
    PATH="/usr/local/scala/bin:${PATH}" \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java runtime (Debian Bookworm has OpenJDK 17)
        openjdk-17-jre-headless \
        # Utilities
        ca-certificates \
        curl \
        wget \
        git \
        supervisor \
        # Snappy for Spark
        libsnappy1v5 \
        # Locale
        locales && \
    locale-gen en_US.UTF-8 && \
    # Cleanup
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy Scala from builder
COPY --from=builder /usr/local/scala /usr/local/scala

# Copy virtual environment (Poetry not needed in runtime)
COPY --from=builder /app/.venv /app/.venv

# Create non-root user and group
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -m -s /bin/bash ${APP_USER} && \
    mkdir -p ${WORKSPACE} && \
    chown -R ${APP_USER}:${APP_USER} ${WORKSPACE} /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Set working directory
WORKDIR ${WORKSPACE}

# Switch to non-root user
USER ${APP_USER}

# Verify installations
RUN python --version && \
    pip --version && \
    scala -version

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["bash"]
