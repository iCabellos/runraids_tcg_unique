#!/bin/bash

# Build script for Vercel deployment
echo "Building RunRaids for Vercel..."

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --clear

# Run migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data

echo "Build completed successfully!"
