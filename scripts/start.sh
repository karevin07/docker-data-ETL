#!/bin/bash
# =============================================================================
# Docker Data ETL Platform - Complete Setup Script
# =============================================================================
# This script handles the complete startup and configuration:
# 1. Start all Docker services
# 2. Wait for services to be healthy
# 3. Configure Airflow connections automatically
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Docker Data ETL Platform Setup"
echo "=========================================="

# Step 1: Start Docker Compose services
echo ""
echo "Step 1: Starting Docker services..."
echo "=========================================="
cd "$PROJECT_DIR"
docker-compose up -d

# Step 2: Wait for services to be healthy
echo ""
echo "Step 2: Waiting for services to be ready..."
echo "=========================================="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until docker exec data-etl-postgres pg_isready -U airflow > /dev/null 2>&1; do
    echo "  PostgreSQL is starting up..."
    sleep 3
done
echo "✓ PostgreSQL is ready"

# Wait for Airflow webserver
echo "Waiting for Airflow webserver..."
until docker exec data-etl-airflow curl -f http://localhost:8080/health > /dev/null 2>&1; do
    echo "  Airflow webserver is starting up..."
    sleep 5
done
echo "✓ Airflow webserver is ready"

# Wait for Airflow scheduler
echo "Waiting for Airflow scheduler..."
sleep 10
echo "✓ Airflow scheduler is ready"

# Wait for Spark master
echo "Waiting for Spark master..."
until docker exec data-etl-spark-master curl -f http://localhost:8080 > /dev/null 2>&1; do
    echo "  Spark master is starting up..."
    sleep 3
done
echo "✓ Spark master is ready"

# Step 3: Configure Airflow connections
echo ""
echo "Step 3: Configuring Airflow connections..."
echo "=========================================="
bash "$SCRIPT_DIR/setup-airflow-connections.sh"

# Step 4: Show service URLs
echo ""
echo "=========================================="
echo "✓ All services are up and running!"
echo "=========================================="
echo ""
echo "Access your services at:"
echo "  Airflow UI:    http://localhost:8282"
echo "  Spark UI:      http://localhost:8080"
echo "  JupyterLab:    http://localhost:8888"
echo "  PostgreSQL:    localhost:5432"
echo ""
echo "Spark Workers:"
echo "  Worker 1:      http://localhost:8081"
echo "  Worker 2:      http://localhost:8082"
echo "  Worker 3:      http://localhost:8083"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f [service_name]"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
