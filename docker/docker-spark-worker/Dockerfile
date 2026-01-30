# syntax=docker/dockerfile:1
# =============================================================================
# Spark Worker Node for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates Spark worker nodes for distributed processing
# =============================================================================

FROM data-etl-spark-base:latest

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL Spark Worker" \
      org.opencontainers.image.description="Apache Spark worker node for distributed processing" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Switch to root for configuration
USER root

# Spark Worker specific environment variables
# Note: SPARK_HOME is inherited from base image
ENV SPARK_MODE=worker \
    SPARK_WORKER_WEBUI_PORT=8081 \
    SPARK_WORKER_LOG=${SPARK_HOME}/logs \
    SPARK_WORKER_MEMORY=1G \
    SPARK_WORKER_CORES=1

# Create log directory and set permissions
RUN mkdir -p ${SPARK_WORKER_LOG} && \
    chown -R etluser:etluser ${SPARK_WORKER_LOG}

# Switch back to non-root user for security
USER etluser

# Expose Spark Worker Web UI
EXPOSE 8081

# Health check for Spark Worker
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8081/ || exit 1

# Start Spark Worker
# The master URL is provided via environment variable SPARK_MASTER_URL
CMD ["sh", "-c", "bin/spark-class org.apache.spark.deploy.worker.Worker ${SPARK_MASTER_URL}"]
