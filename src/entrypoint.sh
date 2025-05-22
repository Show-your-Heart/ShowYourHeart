#!/bin/bash
set -e

# Function to start Gunicorn with dynamic reload-extra-file options
start_gunicorn() {
    # Generate the reload-extra-file options dynamically
    extra_files=$(find /srv/templates -name "*.html" -printf "--reload-extra-file %p ")

    # Start Gunicorn
    echo "Starting Gunicorn..."
    python manage.py migrate
    echo yes | python manage.py collectstatic
    gunicorn --bind 0.0.0.0:8000 --reload --reload-engine=poll $extra_files project.wsgi:application --threads=10

}

# Start Gunicorn
start_gunicorn