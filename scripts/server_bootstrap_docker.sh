#!/usr/bin/env bash
# d:/Freelance/Python_Dev/Pwa/scripts/server_bootstrap_docker.sh
# Installe Docker sur Ubuntu serveur et prépare le dossier projet.
# Permet un setup initial reproductible avant le premier deploiement.
# RELEVANT FILES:scripts/deploy_docker.sh,docker-compose.yml,.env.example

set -euo pipefail

PROJECT_ROOT="/var/www/devis/Pwa"
REPO_URL="https://github.com/Eren-73/Pwa.git"

sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker

if [ ! -d "/var/www/devis" ]; then
  sudo mkdir -p /var/www/devis
fi
sudo chown -R "$USER":"$USER" /var/www/devis

if [ ! -d "$PROJECT_ROOT/.git" ]; then
  git clone "$REPO_URL" "$PROJECT_ROOT"
else
  echo "Repository already exists at $PROJECT_ROOT"
fi

echo "Bootstrap complete. Next: copy .env and run scripts/deploy_docker.sh"
