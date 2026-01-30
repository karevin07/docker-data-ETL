# syntax=docker/dockerfile:1
# =============================================================================
# JupyterLab Image for Docker Data ETL Platform (Ultra-Fast Build)
# =============================================================================
# This Dockerfile creates a JupyterLab development environment:
# - JupyterLab 4.x (using official image)
# - Python 3.12 with data science libraries
# - Spark integration
# - Scala kernel (Almond)
# - uv for package management (10-100x faster than pip!)
# - BuildKit cache mounts for faster rebuilds
# =============================================================================
# Build time:
#   First build: ~1-2 minutes
#   Rebuild: ~30 seconds (with cache) ⚡⚡⚡
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install additional packages
# -----------------------------------------------------------------------------
FROM quay.io/jupyter/scipy-notebook:python-3.12 AS jupyter_builder

# Build arguments
ARG UV_VERSION=0.5.21

# Switch to root for installation
USER root

# Install system dependencies
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java for Spark
        openjdk-17-jre-headless \
        # Utilities
        vim \
        less \
        tree \
        git

# Switch back to jovyan user for package installations
USER ${NB_UID}

# Install uv - The fast Python package installer (10-100x faster than pip!)
RUN --mount=type=cache,target=/home/jovyan/.cache/pip,sharing=locked,uid=1000,gid=100 \
    pip install "uv==${UV_VERSION}"

# Install additional Python packages with uv
# Using BuildKit cache mount to cache uv packages (HUGE speedup!)
# Jupyter uses conda environment, so we specify --python explicitly
RUN --mount=type=cache,target=/home/jovyan/.cache/uv,sharing=locked,uid=1000,gid=100 \
    uv pip install --python $(which python) \
        # Database connectivity
        psycopg2-binary==2.9.10 \
        "sqlalchemy>=2.0.0" \
        # PySpark (use 3.5.4 to match requirements.txt)
        pyspark==3.5.4 \
        # Chinese text processing
        jieba==0.42.1 \
        # Web scraping
        "beautifulsoup4>=4.12.0" \
        "lxml>=5.0.0" \
        # JupyterLab extensions
        "jupyterlab-git>=0.50.0"

# Install Scala kernel (Almond) for Scala 2.13 with Coursier
# Using specific version for reproducibility and security
ARG COURSIER_VERSION=v2.1.20
# SHA256 checksum for Coursier v2.1.20 (x86_64-pc-linux.gz)
# Verified: 2026-01-30
ARG COURSIER_SHA256="327d6d1a3c94c7a51d8bfe92036bd7361672a7c1e791aa591844d9f3220183ea"

# Download and install Coursier with BuildKit cache mount
# Add uid/gid for jovyan user (1000:100) to cache mount for write permissions
RUN --mount=type=cache,target=/tmp/coursier_cache,sharing=locked,uid=1000,gid=100 \
    # Download Coursier only if not in cache
    if [ ! -f "/tmp/coursier_cache/cs-${COURSIER_VERSION}.gz" ]; then \
        curl -fsSL "https://github.com/coursier/coursier/releases/download/${COURSIER_VERSION}/cs-x86_64-pc-linux.gz" \
        -o "/tmp/coursier_cache/cs-${COURSIER_VERSION}.gz"; \
    fi && \
    # Copy from cache to working directory
    cp "/tmp/coursier_cache/cs-${COURSIER_VERSION}.gz" coursier.gz && \
    # Verify SHA256 checksum for security
    echo "${COURSIER_SHA256}  coursier.gz" | sha256sum -c - && \
    # Extract and install Scala kernel
    gzip -d coursier.gz && \
    chmod +x coursier && \
    ./coursier launch --fork almond:0.14.1 --scala 2.13 -- \
        --install \
        --id scala \
        --display-name "Scala 2.13" && \
    rm -f coursier

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final production image
# -----------------------------------------------------------------------------
FROM quay.io/jupyter/scipy-notebook:python-3.12

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL JupyterLab (Fast)" \
      org.opencontainers.image.description="JupyterLab development environment for data ETL" \
      org.opencontainers.image.version="4.3.5-fast" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Build arguments
ARG WORKSPACE=/home/jovyan/work

# Switch to root for setup
USER root

# Install runtime dependencies and Java
# Using BuildKit cache mount to speed up repeated builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        vim \
        less \
        tree \
        git

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PATH="${PATH}:/usr/lib/jvm/java-17-openjdk-amd64/bin"

# Copy additional packages from builder
COPY --from=jupyter_builder --chown=${NB_UID}:${NB_GID} \
    /opt/conda/lib/python3.12/site-packages /opt/conda/lib/python3.12/site-packages

# Copy Scala kernel (Almond) from builder
COPY --from=jupyter_builder --chown=${NB_UID}:${NB_GID} \
    /home/jovyan/.local/share/jupyter /home/jovyan/.local/share/jupyter

# Create workspace directories
RUN mkdir -p \
        ${WORKSPACE}/notebooks \
        ${WORKSPACE}/data \
        ${WORKSPACE}/dags \
        ${WORKSPACE}/spark && \
    chown -R ${NB_UID}:${NB_GID} ${WORKSPACE}

# Switch to notebook user
USER ${NB_UID}

WORKDIR ${WORKSPACE}

# Expose JupyterLab and Spark UI ports
EXPOSE 8888 4040

# Health check for JupyterLab
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8888/lab || exit 1

# Start JupyterLab
# Note: Official image already has proper entrypoint and secure defaults
# Token will be auto-generated on first start and shown in logs, or can be set via JUPYTER_TOKEN env var
CMD ["start-notebook.py"]
