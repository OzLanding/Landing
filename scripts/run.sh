#!/bin/sh

set -e

. /opt/venv/bin/activate

echo "Applying database migrations..."
python manage.py migrate

echo "Starting Gunicorn server..."
gunicorn Landing.wsgi:application --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker
