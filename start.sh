#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

# Only seed if database is empty (check if any Places exist)
if python manage.py shell -c "from mythgarden.models import Place; print(Place.objects.exists())" | grep -q "False"; then
    echo "Database is empty. Seeding database with initial data..."
    python manage.py seed_database seeds/seed_4-21_12-59.csv --verbosity 1

    echo "Seeding database with dialogue..."
    python manage.py seed_database seeds/dialogue-seed_2-7_1-19.csv --verbosity 1
else
    echo "Database already seeded, skipping seed operation..."
fi

echo "Starting gunicorn..."
exec gunicorn --bind :8000 --workers 2 mythsite.wsgi
