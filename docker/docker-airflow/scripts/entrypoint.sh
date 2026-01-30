#!/usr/bin/env bash
set -e

# Initialize Airflow database
if [ ! -f /opt/airflow/.db_initialized ]; then
    echo "Initializing Airflow database..."
    airflow db migrate
    touch /opt/airflow/.db_initialized
fi

# Create admin user if it doesn't exist
# Check for required environment variables
if [ -z "${AIRFLOW_ADMIN_USERNAME:-}" ] || [ -z "${AIRFLOW_ADMIN_PASSWORD:-}" ]; then
    echo "ERROR: AIRFLOW_ADMIN_USERNAME and AIRFLOW_ADMIN_PASSWORD must be set to create the initial admin user." >&2
    echo "Refusing to create an admin user with insecure default credentials." >&2
    exit 1
fi

AIRFLOW_ADMIN_EMAIL="${AIRFLOW_ADMIN_EMAIL:-admin@example.com}"
AIRFLOW_ADMIN_FIRSTNAME="${AIRFLOW_ADMIN_FIRSTNAME:-Admin}"
AIRFLOW_ADMIN_LASTNAME="${AIRFLOW_ADMIN_LASTNAME:-User}"

if ! airflow users list 2>/dev/null | grep -q "${AIRFLOW_ADMIN_USERNAME}"; then
    echo "Creating admin user '${AIRFLOW_ADMIN_USERNAME}'..."
    airflow users create \
        -r Admin \
        -u "${AIRFLOW_ADMIN_USERNAME}" \
        -e "${AIRFLOW_ADMIN_EMAIL}" \
        -f "${AIRFLOW_ADMIN_FIRSTNAME}" \
        -l "${AIRFLOW_ADMIN_LASTNAME}" \
        -p "${AIRFLOW_ADMIN_PASSWORD}"
fi

# Execute the command passed to the container
exec airflow "$@"