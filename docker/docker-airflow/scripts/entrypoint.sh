#!/usr/bin/env bash
set -e

# Initialize Airflow database
if [ ! -f /opt/airflow/.db_initialized ]; then
    echo "Initializing Airflow database..."
    airflow db migrate
    touch /opt/airflow/.db_initialized
fi

# Create admin user if it doesn't exist
if ! airflow users list 2>/dev/null | grep -q "admin"; then
    echo "Creating admin user..."
    airflow users create \
        -r Admin \
        -u admin \
        -e admin@example.com \
        -f admin \
        -l user \
        -p admin
fi

# Execute the command passed to the container
exec airflow "$@"