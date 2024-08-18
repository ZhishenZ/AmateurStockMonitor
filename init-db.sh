#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    until pg_isready -U "$POSTGRES_USER"; do
        sleep 1
    done
    echo "PostgreSQL is ready."
}

# Only execute if the database has not been initialized
if [ -z "$(ls -A /var/lib/postgresql/data)" ]; then
    echo "Initializing database..."

    # Start PostgreSQL service
    service postgresql start

    # Wait for PostgreSQL to be ready
    wait_for_postgres

    # Create database and user
    psql -U "$POSTGRES_USER" -c "CREATE DATABASE $POSTGRES_DB;"
    psql -U "$POSTGRES_USER" -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
    psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;"

    # Stop PostgreSQL service
    service postgresql stop
fi
