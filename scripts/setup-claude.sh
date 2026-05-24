#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_DIR="${HOME}/.claude"
SKILLS_DIR="${CLAUDE_DIR}/skills"

mkdir -p "$CLAUDE_DIR" "$SKILLS_DIR"

if [[ -f "${CLAUDE_DIR}/settings.json" ]]; then
  cp "${CLAUDE_DIR}/settings.json" "${CLAUDE_DIR}/settings.json.bak.$(date +%Y%m%d%H%M%S)"
fi

cp "${ROOT_DIR}/config/claude/settings.json" "${CLAUDE_DIR}/settings.json"

for skill in feature-dev write-tests debug-loop git-workflow sandbox-first; do
  mkdir -p "${SKILLS_DIR}/${skill}"
  cp "${ROOT_DIR}/skills/${skill}/SKILL.md" "${SKILLS_DIR}/${skill}/SKILL.md"
done

echo "Configuration Claude installée dans ${CLAUDE_DIR}"
echo "Skills installés dans ${SKILLS_DIR}"
