# syntax=docker/dockerfile:1
# =============================================================================
# Base Python Image for Docker Data ETL Platform (Ultra-Fast Build Version)
# =============================================================================
# This multi-stage Dockerfile creates an optimized base image with:
# - Python 3.12.12 (official Docker image)
# - Scala 2.13.18 (latest 2.13.x compatible with Spark 4.x)
# - uv for dependency management (10-100x faster than pip/poetry!)
# - OpenJDK 17 (required for Spark 4.x)
# - BuildKit cache mounts for faster rebuilds
# =============================================================================
# Build time: ~1-2 minutes (first build), ~30 seconds (rebuilds with cache)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.12.12-slim-bookworm AS builder

# Build arguments for version management
ARG SCALA_VERSION=2.13.18
ARG UV_VERSION=0.5.21
# SHA256 checksum for Scala 2.13.18
# Verify at: https://github.com/scala/scala/releases/download/v2.13.18/scala-2.13.18.tgz
ARG SCALA_SHA256="1834d09fd5c78ec77e9a933ab76c724280a8ec9595a332a6112823787a9ac3e6"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies and Java
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
        # Java (Debian Bookworm has OpenJDK 17)
        openjdk-17-jdk-headless \
        # Locale support
        locales \
        # Snappy compression for Spark
        libsnappy-dev && \
    # Generate locale
    locale-gen en_US.UTF-8

# Install Scala with checksum verification
# Using BuildKit cache mount to cache downloaded files across builds
WORKDIR /tmp
RUN --mount=type=cache,target=/tmp/downloads,sharing=locked \
    if [ ! -f "/tmp/downloads/scala-${SCALA_VERSION}.tgz" ]; then \
        wget -q "https://github.com/scala/scala/releases/download/v${SCALA_VERSION}/scala-${SCALA_VERSION}.tgz" \
        -O "/tmp/downloads/scala-${SCALA_VERSION}.tgz"; \
    fi && \
    # Copy from cache to working directory
    cp "/tmp/downloads/scala-${SCALA_VERSION}.tgz" . && \
    # Verify SHA256 checksum for security (protects against supply chain attacks)
    echo "${SCALA_SHA256}  scala-${SCALA_VERSION}.tgz" | sha256sum -c - && \
    tar -xzf "scala-${SCALA_VERSION}.tgz" && \
    mkdir -p /usr/local/scala && \
    mv "scala-${SCALA_VERSION}"/* /usr/local/scala/ && \
    rm -f "scala-${SCALA_VERSION}.tgz" && \
    rm -rf "scala-${SCALA_VERSION}"

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
        supervisor \
        # Snappy for Spark
        libsnappy1v5 \
        # Locale
        locales && \
    locale-gen en_US.UTF-8

# Copy Scala from builder
COPY --from=builder /usr/local/scala /usr/local/scala

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
    scala -version

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

CMD ["bash"]
