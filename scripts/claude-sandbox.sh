#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/sandbox-up.sh >/dev/null

cat <<'MSG'
Claude Code est lancé en mode sandbox-first :
- les commandes de développement doivent passer par ./scripts/sandbox-run.sh ou ./scripts/sandbox-test.sh
- la config ~/.claude/settings.json du projet doit autoriser seulement ces wrappers côté Bash
MSG

exec claude "$@"
