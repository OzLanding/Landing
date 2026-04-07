#!/bin/sh

set -e

echo "Applying database migrations..."
uv run python manage.py migrate

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
uv run gunicorn Landing.wsgi:application --bind 0.0.0.0:8000
