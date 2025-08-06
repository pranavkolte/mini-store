#!/bin/bash
set -e

echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Applying database migrations..."
python manage.py migrate

echo "🚀 Starting Gunicorn server..."
exec gunicorn config.wsgi:application -c /app/gunicorn.conf.py