#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo ".env créé automatiquement"
fi

docker compose up -d

echo "Stack démarrée. Utilisez './scripts/healthcheck.sh' pour vérifier l'état."
