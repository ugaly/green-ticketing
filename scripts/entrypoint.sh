#!/usr/bin/env sh
set -eu

cd /app

# Default safe-ish dev env in container
export DJANGO_DEBUG="${DJANGO_DEBUG:-true}"
export DJANGO_ALLOWED_HOSTS="${DJANGO_ALLOWED_HOSTS:-127.0.0.1,localhost}"

# Run migrations automatically (dev convenience)
python manage.py migrate --noinput

# Start dev server
exec python manage.py runserver 0.0.0.0:8000

