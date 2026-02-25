#!/usr/bin/env sh
set -e

echo "Running migrations..."
alembic upgrade head || true

echo "Starting app..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
