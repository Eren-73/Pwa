#!/usr/bin/env bash
# d:/Freelance/Python_Dev/Pwa/scripts/deploy_docker.sh
# Deploy ou met a jour l'application Docker (web, db, nginx).
# Automatise pull, build, restart et checks de sante essentiels.
# RELEVANT FILES:docker-compose.yml,.env.example,Devis/settings.py,nginx/default.conf

set -euo pipefail

PROJECT_ROOT="/var/www/devis/Pwa"

if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
  SUDO="sudo -n"
else
  SUDO=""
fi

run_docker_compose() {
  if [ -n "$SUDO" ]; then
    $SUDO docker compose "$@"
  else
    docker compose "$@"
  fi
}

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

run_docker_compose down
run_docker_compose up -d --build

run_docker_compose ps

# Basic runtime checks
run_docker_compose exec -T web python manage.py check
run_docker_compose exec -T web python manage.py showmigrations | tail -n 20

echo "Deploy complete. App should be available on http://<server-ip>/"
