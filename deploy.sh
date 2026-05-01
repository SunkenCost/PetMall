#!/bin/bash

# --- PetMall Deployment Script ---
echo "Starting deployment process..."

# 1. Pull latest code
echo "Pulling code from GitHub..."
git fetch --all
git reset --hard origin/main

# 2. Rebuild and start containers
echo "Restarting container services..."
docker-compose up -d --build

# 3. Apply migrations
echo "Updating database schema..."
docker-compose exec -T backend python manage.py migrate

echo "Deployment completed"
