#!/usr/bin/env bash
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-CouLiBaLy-B/pos-test}"
BRANCH="${GITHUB_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"
API_URL="https://api.github.com/repos/${REPO}/branches/${BRANCH}/protection"

if [[ -z "$TOKEN" ]]; then
  echo "GITHUB_TOKEN est requis" >&2
  exit 1
fi

payload=$(cat <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "validate"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
JSON
)

curl -fsS -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "$API_URL" \
  -d "$payload" >/dev/null

echo "Branch protection appliquée sur ${REPO}:${BRANCH}"
