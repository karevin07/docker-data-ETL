# syntax=docker/dockerfile:1
# =============================================================================
# Spark Master Node for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates the Spark master node for cluster coordination
# =============================================================================

FROM data-etl-spark-base:latest

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL Spark Master" \
      org.opencontainers.image.description="Apache Spark master node for cluster coordination" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Switch to root for configuration
USER root

# Spark Master specific environment variables
# Note: SPARK_HOME is inherited from base image
ENV SPARK_MODE=master \
    SPARK_MASTER_WEBUI_PORT=8080 \
    SPARK_MASTER_PORT=7077 \
    SPARK_MASTER_LOG=${SPARK_HOME}/logs

# Create log directory and set permissions
RUN mkdir -p ${SPARK_MASTER_LOG} && \
    chown -R etluser:etluser ${SPARK_MASTER_LOG}

# Switch back to non-root user for security
USER etluser

# Expose Spark Master Web UI and master port
EXPOSE 8080 7077 6066

# Health check for Spark Master
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Start Spark Master
CMD ["bin/spark-class", "org.apache.spark.deploy.master.Master"]
