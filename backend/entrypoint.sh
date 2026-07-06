#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

export PYTHONPATH=.

echo "=== Running database migrations ==="
alembic upgrade head

echo "=== Seeding database ==="
python -m app.scripts.seed

echo "=== Starting FastAPI application ==="
exec "$@"
