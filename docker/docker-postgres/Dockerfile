# syntax=docker/dockerfile:1
# =============================================================================
# PostgreSQL Database Image for Docker Data ETL Platform
# =============================================================================
# This Dockerfile creates a PostgreSQL database with:
# - PostgreSQL 16.6 (latest stable version 16.x)
# - Custom initialization scripts
# - Optimized configuration for ETL workloads
# =============================================================================
# ⚠️  CRITICAL MIGRATION WARNING (READ BEFORE UPGRADING) ⚠️
# =============================================================================
# This image represents a MAJOR VERSION UPGRADE from PostgreSQL 9.6 to 16.6.
# PostgreSQL does NOT support in-place upgrades across these versions.
#
# ❌ DANGER: If you have an existing Docker volume (e.g., "postgres_data") with
#    PostgreSQL 9.6 data, you MUST NOT reuse that volume directly with this
#    image. Doing so will cause PostgreSQL to FAIL TO START or result in
#    DATA LOSS/CORRUPTION.
#
# ✅ SAFE MIGRATION PROCEDURE:
#
# Step 1: Start your OLD PostgreSQL 9.6 container with existing volume
#         docker-compose up postgres
#
# Step 2: Export data from the old instance
#         docker exec data-etl-postgres pg_dump -U airflow airflow > backup.sql
#         # Or with custom format for better performance:
#         docker exec data-etl-postgres pg_dump -U airflow -Fc airflow > backup.dump
#
# Step 3: Stop and remove the old container (keep backup safe!)
#         docker-compose down
#         # OPTIONAL: Backup the old volume before deletion
#         docker run --rm -v postgres_data:/data -v $(pwd):/backup \
#           busybox tar czf /backup/postgres_9.6_backup.tar.gz /data
#
# Step 4: Remove old volume (or rename it for safety)
#         docker volume rm data-etl-postgres-data
#         # OR: docker volume rename data-etl-postgres-data postgres-data-old
#
# Step 5: Start NEW container with this 16.6 image (creates fresh volume)
#         docker-compose up -d postgres
#
# Step 6: Restore data into the new instance
#         # Wait for PostgreSQL to be ready
#         docker exec data-etl-postgres pg_isready -U airflow
#         # Restore from backup
#         docker exec -i data-etl-postgres psql -U airflow airflow < backup.sql
#         # Or with custom format:
#         docker exec -i data-etl-postgres pg_restore -U airflow -d airflow < backup.dump
#
# Step 7: Verify data integrity and test your ETL workflows
#
# For more information, see: docs/POSTGRESQL_MIGRATION.md
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
