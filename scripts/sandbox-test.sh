#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/sandbox-up.sh >/dev/null

docker compose exec assistant-sandbox bash -lc "python3 -m pip install -r requirements-dev.txt >/dev/null && ./scripts/run-tests.sh"
