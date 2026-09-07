# syntax=docker/dockerfile:1
# =============================================================================
# JupyterLab Image for Docker Data ETL Platform (Ultra-Fast Build)
# =============================================================================
# This Dockerfile creates a JupyterLab development environment:
# - JupyterLab 4.x (jupyter/base-notebook, no heavy scipy stack)
# - Python 3.12 + pandas/matplotlib for analysis notebooks
# - PySpark integration (Python kernel only)
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
FROM quay.io/jupyter/base-notebook:python-3.12 AS jupyter_builder

# Build arguments
ARG UV_VERSION=0.12.10

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
        # Analysis stack (base-notebook does not ship these)
        "pandas>=2.2.0,<3.0.0" \
        "matplotlib>=3.8.0" \
        # Database connectivity
        psycopg2-binary==2.9.10 \
        "sqlalchemy>=2.0.0" \
        # PySpark (match pyproject.toml/uv.lock and Airflow constraints)
        pyspark==3.5.3 \
        # Chinese text processing
        jieba==0.42.1 \
        # Web scraping
        "beautifulsoup4>=4.12.0" \
        "lxml>=5.0.0" \
        # JupyterLab extensions
        "jupyterlab-git>=0.50.0"

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final production image
# -----------------------------------------------------------------------------
FROM quay.io/jupyter/base-notebook:python-3.12

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
        tree \
        git && \
    # Point the arch-independent JAVA_HOME at the actual JDK dir (…-amd64 / …-arm64)
    ln -sfn "$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")" /usr/lib/jvm/java-17-openjdk

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk \
    PATH="${PATH}:/usr/lib/jvm/java-17-openjdk/bin"

# Copy additional packages from builder
COPY --from=jupyter_builder --chown=${NB_UID}:${NB_GID} \
    /opt/conda/lib/python3.12/site-packages /opt/conda/lib/python3.12/site-packages

# Copy Jupyter data dir (prebuilt lab extensions, e.g. jupyterlab-git) from builder
COPY --from=jupyter_builder --chown=${NB_UID}:${NB_GID} \
    /opt/conda/share/jupyter /opt/conda/share/jupyter

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

# Health check: inherit the base image's /etc/jupyter/docker_healthcheck.py
# (a Python check that handles the token and TLS). base-notebook has no curl,
# so do not override it with a curl-based HEALTHCHECK.

# Start JupyterLab
# Note: Official image already has proper entrypoint and secure defaults
# Token will be auto-generated on first start and shown in logs, or can be set via JUPYTER_TOKEN env var
CMD ["start-notebook.py"]
