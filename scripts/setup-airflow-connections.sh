#!/bin/bash
# =============================================================================
# Airflow Connections Setup Script
# =============================================================================
# This script automatically configures Spark and PostgreSQL connections in Airflow
# Run this after starting all Docker containers
# =============================================================================

set -e

echo "=========================================="
echo "Setting up Airflow Connections"
echo "=========================================="

# Wait for Airflow webserver to be ready
echo ""
echo "Waiting for Airflow to be ready..."
until docker exec data-etl-airflow airflow db check > /dev/null 2>&1; do
    echo "Airflow is not ready yet. Waiting..."
    sleep 5
done
echo "✓ Airflow is ready"

# Setup Spark Connection
echo ""
echo "Setting up Spark connection..."
docker exec data-etl-airflow airflow connections delete 'spark_default' 2>/dev/null || true
docker exec data-etl-airflow airflow connections add 'spark_default' \
    --conn-type 'spark' \
    --conn-host 'spark://spark-master' \
    --conn-port '7077' \
    --conn-extra '{"queue": "root.default", "deploy-mode": "client"}'

echo "✓ Spark connection created"

# Setup PostgreSQL Connection
echo ""
echo "Setting up PostgreSQL connection..."
docker exec data-etl-airflow airflow connections delete 'postgres_default' 2>/dev/null || true
docker exec data-etl-airflow airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 'airflow' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-port '5432'

echo "✓ PostgreSQL connection created"

# Verify connections
echo ""
echo "=========================================="
echo "Verifying connections..."
echo "=========================================="
docker exec data-etl-airflow airflow connections list | grep -E "spark_default|postgres_default"

echo ""
echo "=========================================="
echo "✓ All connections configured successfully!"
echo "=========================================="
echo ""
echo "You can verify in Airflow UI:"
echo "  http://localhost:8282"
echo "  Admin -> Connections"
echo ""
