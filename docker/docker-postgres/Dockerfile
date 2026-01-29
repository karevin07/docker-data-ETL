# syntax=docker/dockerfile:1
# =============================================================================
# PostgreSQL Database Image for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates a PostgreSQL database with:
# - PostgreSQL 16.6 (latest stable version 16.x)
# - Custom initialization scripts
# - Optimized configuration for ETL workloads
# =============================================================================
# IMPORTANT MIGRATION NOTE:
# This upgrades from PostgreSQL 9.6 to 16.6 (major version upgrade)
# You MUST perform a database dump/restore migration:
#   1. Export data: pg_dump -U airflow airflow > backup.sql
#   2. Update to new image
#   3. Restore data: psql -U airflow airflow < backup.sql
# =============================================================================

FROM postgres:16.6-alpine

# Metadata labels
LABEL org.opencontainers.image.title="Data ETL PostgreSQL" \
      org.opencontainers.image.description="PostgreSQL database for Airflow and ETL data storage" \
      org.opencontainers.image.version="16.6" \
      org.opencontainers.image.authors="Kelvin Liao" \
      maintainer="Kelvin Liao"

# Environment variables for PostgreSQL configuration
# These can be overridden in docker-compose.yml
ENV POSTGRES_USER=airflow \
    POSTGRES_PASSWORD=airflow \
    POSTGRES_DB=airflow \
    PGDATA=/var/lib/postgresql/data/pgdata

# Install additional extensions and utilities
RUN apk add --no-cache \
    # Utilities for troubleshooting
    bash \
    curl \
    # Additional PostgreSQL extensions
    postgresql-contrib && \
    # Create necessary directories
    mkdir -p /var/lib/postgresql/data && \
    chown -R postgres:postgres /var/lib/postgresql

# Copy initialization scripts
# These scripts will run automatically when the database is first created
COPY docker/docker-postgres/pg-init-scripts/*.sh /docker-entrypoint-initdb.d/

# Ensure scripts are executable
RUN chmod +x /docker-entrypoint-initdb.d/*.sh

# Copy custom PostgreSQL configuration (optional)
# COPY postgresql.conf /etc/postgresql/postgresql.conf

# Expose PostgreSQL default port
EXPOSE 5432

# Health check for PostgreSQL
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} || exit 1

# Use the default postgres entrypoint and command
# The official image already defines proper ENTRYPOINT and CMD
