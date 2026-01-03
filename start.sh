#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding database (using get_or_create, safe to run multiple times)..."
python manage.py seed_database seeds/seed_4-21_12-59.csv --verbosity 0

echo "Seeding dialogue..."
python manage.py seed_database seeds/dialogue-seed_2-7_1-19.csv --verbosity 0

echo "Starting gunicorn..."
exec gunicorn --bind :8000 --workers 2 mythsite.wsgi
