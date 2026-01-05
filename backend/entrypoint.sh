#!/bin/bash
set -e

# Default to running Gunicorn if no argument is provided
cmd="$@"

# Function to verify database connection
wait_for_db() {
    echo "Waiting for database..."
    python manage.py shell -c "import time; from django.db import connections; from django.db.utils import OperationalError; conn = connections['default']; 
while True:
    try:
        conn.cursor()
        print('Database available!')
        break
    except OperationalError:
        print('Database down, waiting...')
        time.sleep(2)"
}

if [ "$1" = "web" ]; then
    wait_for_db
    echo "Applying migrations..."
    python manage.py migrate --noinput
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo "Starting Gunicorn..."
    exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
elif [ "$1" = "celery_worker" ]; then
    wait_for_db
    echo "Starting Celery Worker..."
    exec celery -A core worker -l info --concurrency=2
elif [ "$1" = "celery_beat" ]; then
    wait_for_db
    echo "Starting Celery Beat..."
    exec celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
    # If custom command
    exec $cmd
fi
