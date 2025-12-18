#!/bin/sh
set -e

# Run database migrations (idempotent)
python manage.py migrate --noinput

# Collect static files (do not fail the container if this errors)
python manage.py collectstatic --noinput || true

# Start gunicorn
exec gunicorn pgadmin_config.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --threads 1 \
  --worker-class sync \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --keep-alive 5