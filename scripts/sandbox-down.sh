#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose --profile sandbox stop assistant-sandbox >/dev/null 2>&1 || true
docker compose --profile sandbox rm -f assistant-sandbox >/dev/null 2>&1 || true

echo "Sandbox arrêtée."
