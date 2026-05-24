#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${GITHUB_REPOSITORY:-CouLiBaLy-B/pos-test}"
TOKEN="${GITHUB_TOKEN:-}"
LABELS_FILE="${ROOT_DIR}/.github/labels.json"

if [[ -z "$TOKEN" ]]; then
  echo "GITHUB_TOKEN est requis" >&2
  exit 1
fi

python3 - <<'PY' "$LABELS_FILE" | while IFS=$'\t' read -r name color description; do
import json, sys
from pathlib import Path
for label in json.loads(Path(sys.argv[1]).read_text()):
    print(label['name'], label['color'], label['description'], sep='\t')
PY
  payload=$(python3 - <<'PY' "$name" "$color" "$description"
import json, sys
print(json.dumps({"name": sys.argv[1], "color": sys.argv[2], "description": sys.argv[3]}))
PY
)
  encoded_name=$(python3 - <<'PY' "$name"
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=''))
PY
)

  status=$(curl -s -o /tmp/label-response.json -w '%{http_code}' \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${REPO}/labels/${encoded_name}")

  if [[ "$status" == "200" ]]; then
    curl -fsS -X PATCH \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com/repos/${REPO}/labels/${encoded_name}" \
      -d "$payload" >/dev/null
    echo "Label mis à jour: $name"
  else
    curl -fsS -X POST \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com/repos/${REPO}/labels" \
      -d "$payload" >/dev/null
    echo "Label créé: $name"
  fi
done
