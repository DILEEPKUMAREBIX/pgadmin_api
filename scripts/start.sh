#!/bin/sh

# Retry migrations to avoid startup failures if DB isn’t ready yet
try_migrate() {
  echo "[startup] Running migrations..."
  python manage.py migrate --noinput && return 0
  return 1
}

retries=10
delay=5
count=1
while [ $count -le $retries ]; do
  if try_migrate; then
    echo "[startup] Migrations completed."
    break
  fi
  echo "[startup] Migrations failed (attempt $count/$retries). Retrying in ${delay}s..."
  sleep $delay
  count=$((count+1))
done

# Collect static files (non-fatal)
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