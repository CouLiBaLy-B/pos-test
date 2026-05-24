#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pytest -q

for script in scripts/*.sh; do
  bash -n "$script"
done

if command -v docker >/dev/null 2>&1; then
  TEMP_ENV=0
  if [[ ! -f .env ]]; then
    cp .env.example .env
    TEMP_ENV=1
  fi

  docker compose config >/dev/null

  if [[ "$TEMP_ENV" -eq 1 ]]; then
    rm -f .env
  fi
fi

echo "Tests et validations terminés avec succès."
