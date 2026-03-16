#!/bin/bash

CONTAINER_NAME="flaresolverr-japscan"

# --- FONCTION DE NETTOYAGE ---
function cleanup {
    echo "Arrêt du Docker..."
    docker stop $CONTAINER_NAME > /dev/null 2>&1
    docker rm $CONTAINER_NAME > /dev/null 2>&1
    echo "Terminé."
}
trap cleanup EXIT


# --- 1. LANCEMENT DOCKER ---
echo "Lancement du Docker Flaresolverr..."
docker run -d --name $CONTAINER_NAME -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest
sleep 5


# --- 2. LANCEMENT DU SCRIPT PYTHON ---
# --- 2. LANCEMENT DU SCRIPT PYTHON ---
echo "Lancement du script Python..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

./venv/bin/python scan_checker.py