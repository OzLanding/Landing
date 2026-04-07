#!/bin/sh

set -e

. /app/.venv/bin/activate

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
gunicorn Landing.asgi:application --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker
