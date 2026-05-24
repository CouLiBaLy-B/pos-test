#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

command -v docker >/dev/null || { echo "docker manquant"; exit 1; }
command -v curl >/dev/null || { echo "curl manquant"; exit 1; }
command -v jq >/dev/null || { echo "jq manquant"; exit 1; }

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo ".env créé depuis .env.example"
else
  echo ".env existe déjà"
fi

echo "Bootstrap terminé. Prochaine étape : make up"
