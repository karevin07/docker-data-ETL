# syntax=docker/dockerfile:1
# =============================================================================
# JupyterLab Image for Docker Data ETL Platform (Ultra-Fast Build)
# =============================================================================
# This Dockerfile creates a JupyterLab development environment:
# - JupyterLab 4.x (using official image - MUCH FASTER!)
# - Python 3.12 with data science libraries
# - Spark integration
# - Optional Scala kernel
# =============================================================================
# Build time: ~1-2 minutes (vs 8-12 minutes with manual installation)
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install additional packages
# -----------------------------------------------------------------------------
FROM quay.io/jupyter/scipy-notebook:python-3.12 AS jupyter_builder

# Switch to root for installation
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        # Java for Spark
        openjdk-17-jre-headless \
        # Utilities
        vim \
        less \
        tree \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to jovyan user for pip installations
USER ${NB_UID}

# Install additional Python packages
RUN pip install --no-cache-dir \
        # Database connectivity
        psycopg2-binary==2.9.10 \
        sqlalchemy>=2.0.0 \
        # PySpark (use 3.5.3 for compatibility)
        pyspark==3.5.3 \
        # Chinese text processing
        jieba==0.42.1 \
        # Web scraping
        beautifulsoup4>=4.12.0 \
        lxml>=5.0.0 \
        # JupyterLab extensions
        jupyterlab-git>=0.50.0

# Install Scala kernel (Almond) for Scala 2.13
# Use Almond 0.14.1 which automatically uses compatible Scala 2.13 version
RUN curl -fsSLo coursier.gz https://github.com/coursier/coursier/releases/latest/download/cs-x86_64-pc-linux.gz && \
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
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        vim \
        less \
        tree \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    PATH="${PATH}:/usr/lib/jvm/java-17-openjdk-amd64/bin"

# Copy additional packages from builder
COPY --from=jupyter_builder --chown=${NB_UID}:${NB_GID} \
    /opt/conda/lib/python3.12/site-packages /opt/conda/lib/python3.12/site-packages

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
# Note: Official image already has proper entrypoint
CMD ["start-notebook.py", \
     "--ServerApp.token=", \
     "--ServerApp.password=", \
     "--ServerApp.allow_origin='*'"]
