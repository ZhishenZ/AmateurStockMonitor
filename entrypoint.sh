#!/bin/bash
set -e

# # Start PostgreSQL in the background
docker-entrypoint.sh postgres &

# Wait for PostgreSQL to start
until pg_isready -h "localhost"; do
    echo "PostgreSQL is starting..."
    sleep 1
done

echo "PostgreSQL is up and running."

FLASK_APP=app.py
exec python app.py
