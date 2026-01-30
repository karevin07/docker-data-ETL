#!/usr/bin/env bash
# =============================================================================
# PostgreSQL Migration Helper Script
# =============================================================================
# This script helps migrate data from PostgreSQL 9.6 to 16.6
#
# Usage:
#   bash scripts/migrate-postgres.sh [backup|restore]
#
# Commands:
#   backup  - Create a backup of the current PostgreSQL 9.6 database
#   restore - Restore the backup into PostgreSQL 16.6
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="${POSTGRES_CONTAINER:-data-etl-postgres}"
DB_USER="${POSTGRES_USER:-airflow}"
DB_NAME="${POSTGRES_DB:-airflow}"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.dump"
BACKUP_SQL="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if container is running
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_error "PostgreSQL container '${CONTAINER_NAME}' is not running!"
        print_info "Start it with: docker-compose up -d postgres"
        exit 1
    fi
}

# Function to create backup
backup_database() {
    print_info "Starting PostgreSQL backup..."

    # Create backup directory
    mkdir -p "${BACKUP_DIR}"

    # Check if container is running
    check_container

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    docker exec "${CONTAINER_NAME}" pg_isready -U "${DB_USER}" || {
        print_error "PostgreSQL is not ready!"
        exit 1
    }

    print_info "Creating custom format backup (recommended)..."
    docker exec "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" -Fc "${DB_NAME}" > "${BACKUP_FILE}"
    print_success "Custom format backup created: ${BACKUP_FILE}"

    print_info "Creating plain SQL backup (alternative)..."
    docker exec "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" "${DB_NAME}" > "${BACKUP_SQL}"
    print_success "SQL format backup created: ${BACKUP_SQL}"

    # Create backup info file
    cat > "${BACKUP_DIR}/backup_info_${TIMESTAMP}.txt" <<EOF
Backup Information
==================
Timestamp: ${TIMESTAMP}
Date: $(date)
Container: ${CONTAINER_NAME}
Database: ${DB_NAME}
User: ${DB_USER}
Custom Format: ${BACKUP_FILE}
SQL Format: ${BACKUP_SQL}

PostgreSQL Version:
EOF
    docker exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -c "SELECT version();" >> "${BACKUP_DIR}/backup_info_${TIMESTAMP}.txt"

    print_success "Backup completed successfully!"
    print_info "Backup location: ${BACKUP_DIR}"
    print_info ""
    print_info "Next steps:"
    print_info "1. Stop the containers: docker-compose down"
    print_info "2. Remove or rename the old volume: docker volume rm data-etl-postgres-data"
    print_info "3. Update docker-compose.yml to use PostgreSQL 16.6"
    print_info "4. Start the new container: docker-compose up -d postgres"
    print_info "5. Run this script again with 'restore': bash scripts/migrate-postgres.sh restore"
}

# Function to restore backup
restore_database() {
    print_info "Starting PostgreSQL restore..."

    # Check if container is running
    check_container

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec "${CONTAINER_NAME}" pg_isready -U "${DB_USER}" >/dev/null 2>&1; then
            break
        fi
        echo -n "."
        sleep 2
    done
    echo ""

    docker exec "${CONTAINER_NAME}" pg_isready -U "${DB_USER}" || {
        print_error "PostgreSQL is not ready after 60 seconds!"
        exit 1
    }

    # Find the most recent backup
    if [ ! -d "${BACKUP_DIR}" ]; then
        print_error "Backup directory '${BACKUP_DIR}' does not exist!"
        print_info "Please run backup first: bash scripts/migrate-postgres.sh backup"
        exit 1
    fi

    LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/*.dump 2>/dev/null | head -1)
    LATEST_SQL=$(ls -t "${BACKUP_DIR}"/*.sql 2>/dev/null | head -1)

    if [ -z "${LATEST_BACKUP}" ] && [ -z "${LATEST_SQL}" ]; then
        print_error "No backup files found in ${BACKUP_DIR}!"
        exit 1
    fi

    # Try custom format first (preferred)
    if [ -n "${LATEST_BACKUP}" ]; then
        print_info "Found custom format backup: ${LATEST_BACKUP}"
        print_info "Restoring database..."

        docker exec -i "${CONTAINER_NAME}" pg_restore -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists < "${LATEST_BACKUP}" || {
            print_warning "Custom format restore had warnings (this is normal)"
        }

        print_success "Database restored from custom format backup!"
    elif [ -n "${LATEST_SQL}" ]; then
        print_info "Found SQL format backup: ${LATEST_SQL}"
        print_info "Restoring database..."

        docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" "${DB_NAME}" < "${LATEST_SQL}" || {
            print_warning "SQL restore had warnings (this is normal)"
        }

        print_success "Database restored from SQL backup!"
    fi

    # Verify restore
    print_info "Verifying database..."
    TABLE_COUNT=$(docker exec "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    print_success "Database verification complete. Found ${TABLE_COUNT} tables."

    print_info ""
    print_success "Migration completed successfully!"
    print_info "Next steps:"
    print_info "1. Verify your data: docker exec -it ${CONTAINER_NAME} psql -U ${DB_USER} ${DB_NAME}"
    print_info "2. Start all services: docker-compose up -d"
    print_info "3. Test your ETL workflows"
}

# Function to show usage
show_usage() {
    cat <<EOF
${BLUE}PostgreSQL Migration Helper${NC}

This script helps migrate from PostgreSQL 9.6 to 16.6

${GREEN}Usage:${NC}
  bash scripts/migrate-postgres.sh [command]

${GREEN}Commands:${NC}
  backup   Create a backup of the current database
  restore  Restore a backup into the new database
  help     Show this help message

${GREEN}Environment Variables:${NC}
  POSTGRES_CONTAINER  Container name (default: data-etl-postgres)
  POSTGRES_USER       Database user (default: airflow)
  POSTGRES_DB         Database name (default: airflow)

${GREEN}Examples:${NC}
  # Create a backup
  bash scripts/migrate-postgres.sh backup

  # Restore the latest backup
  bash scripts/migrate-postgres.sh restore

${YELLOW}Migration Steps:${NC}
  1. Backup your PostgreSQL 9.6 database
     $ bash scripts/migrate-postgres.sh backup

  2. Stop all services
     $ docker-compose down

  3. Remove the old volume
     $ docker volume rm data-etl-postgres-data

  4. Start PostgreSQL 16.6 (creates fresh volume)
     $ docker-compose up -d postgres

  5. Restore your backup
     $ bash scripts/migrate-postgres.sh restore

  6. Verify and start all services
     $ docker-compose up -d

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        backup)
            backup_database
            ;;
        restore)
            restore_database
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
