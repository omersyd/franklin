#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Create seed users for testing
echo "Creating seed users..."
python manage.py seed_users

# Load initial data if not already loaded
echo "Loading initial data..."
python manage.py load_initial_data

# Start server
exec "$@"