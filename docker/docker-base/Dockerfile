# syntax=docker/dockerfile:1
# =============================================================================
# Base Python Image for Docker Data ETL Platform (Ultra-Fast Build Version)
# =============================================================================
# This multi-stage Dockerfile creates an optimized base image with:
# - Python 3.12.12 (official Docker image)
# - uv for dependency management (10-100x faster than pip/poetry!)
# - OpenJDK 17 JRE (required for Spark 4.x)
# - BuildKit cache mounts for faster rebuilds
# =============================================================================
# Build time: ~1-2 minutes (first build), ~30 seconds (rebuilds with cache)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.12.12-slim-bookworm AS builder

# Build arguments for version management
ARG UV_VERSION=0.12.10

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies (for any sdist-only Python wheels)
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        # Build tools
        build-essential \
        gcc \
        git \
        wget \
        curl \
        ca-certificates \
        # Locale support
        locales \
        # Snappy compression for Spark
        libsnappy-dev && \
    # Generate locale
    locale-gen en_US.UTF-8

# Install uv - The fast Python package installer
# Using BuildKit cache mount to cache downloads
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --upgrade pip && \
    pip install "uv==${UV_VERSION}"

# Configure uv
ENV UV_CACHE_DIR=/tmp/uv_cache \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

# Install Python dependencies using uv sync (10-100x faster than pip/poetry!)
# uv.lock ensures reproducible builds across all environments
WORKDIR /app
COPY pyproject.toml uv.lock ./

# Sync dependencies from uv.lock with BuildKit cache
RUN --mount=type=cache,target=/tmp/uv_cache,sharing=locked \
    # Create virtual environment
    uv venv /app/.venv && \
    # Sync all dependencies from lock file (fastest and most reliable)
    # --no-install-project: only install dependencies, not the project itself
    uv sync --frozen --no-dev --no-install-project

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Minimal production image
# -----------------------------------------------------------------------------
FROM python:3.12.12-slim-bookworm

# Metadata labels following OCI standards
LABEL org.opencontainers.image.title="Data ETL Base Image" \
      org.opencontainers.image.description="Base Python image (with JRE) for ETL workflows" \
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
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Install runtime dependencies only
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java runtime (Debian Bookworm has OpenJDK 17)
        openjdk-17-jre-headless \
        # Utilities
        ca-certificates \
        curl \
        wget \
        git \
        # Snappy for Spark
        libsnappy1v5 \
        # Locale
        locales && \
    locale-gen en_US.UTF-8

# Copy virtual environment (uv not needed in runtime, only the venv)
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
    java -version

# No HEALTHCHECK: this is a base image, not a long-running service. The images
# that run as services (spark-master, spark-worker, ...) define their own.
CMD ["bash"]
