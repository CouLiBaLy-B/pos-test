#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

HOST_UID="${HOST_UID:-$(id -u)}"
HOST_GID="${HOST_GID:-$(id -g)}"

HOST_UID="$HOST_UID" HOST_GID="$HOST_GID" ./scripts/sandbox-up.sh >/dev/null
HOST_UID="$HOST_UID" HOST_GID="$HOST_GID" docker compose exec assistant-sandbox bash -lc "python3 -m pip install -r requirements-dev.txt >/dev/null && ./scripts/run-tests.sh"
