#!/usr/bin/env bash
# d:/Freelance/Python_Dev/Pwa/scripts/deploy_docker.sh
# Deploy ou met a jour l'application Docker (web, db, nginx).
# Automatise pull, build, restart et checks de sante essentiels.
# RELEVANT FILES:docker-compose.yml,.env.example,Devis/settings.py,nginx/default.conf

set -euo pipefail

PROJECT_ROOT="/var/www/devis/Pwa"

cd "$PROJECT_ROOT"

if [ ! -f ".env" ]; then
  echo "Missing .env in $PROJECT_ROOT"
  echo "Copy .env.example to .env and set real values first."
  exit 1
fi

if [ -d ".git" ]; then
  git fetch origin
  git pull origin main
fi

sudo docker compose down
sudo docker compose up -d --build

sudo docker compose ps

# Basic runtime checks
sudo docker compose exec -T web python manage.py check
sudo docker compose exec -T web python manage.py showmigrations | tail -n 20

echo "Deploy complete. App should be available on http://<server-ip>/"
