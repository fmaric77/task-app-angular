#!/usr/bin/env bash
# Publish this repo to responsum-team via PAT2 (same pattern as cursorskills).
#
# Requires in .env:
#   PAT2        GitHub PAT with repo scope for the responsum-team org
#   PAT2_USER   GitHub username that owns the PAT
#   PAT2_ORG    Target org (default: responsum-team)
#
# Usage:
#   ./scripts/publish_to_responsum.sh              # push HEAD -> main
#   ./scripts/publish_to_responsum.sh <branch>     # push HEAD -> named branch

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  set -o allexport
  # shellcheck disable=SC1091
  source <(grep -E '^[A-Z_][A-Z0-9_]*=' .env)
  set +o allexport
fi

: "${PAT2:?Set PAT2 in .env}"
: "${PAT2_USER:?Set PAT2_USER in .env}"

REPO_NAME="support-agent-poc"
ORG="${PAT2_ORG:-responsum-team}"
TARGET="${ORG}/${REPO_NAME}"
TARGET_BRANCH="${1:-main}"
AUTHED_URL="https://${PAT2_USER}:${PAT2}@github.com/${TARGET}.git"
DESC="Support agent PoC: Jira tickets, runbooks, autonomous fixes via Cursor Agent"

echo "==> Ensuring github.com/${TARGET} exists"
http_code=$(curl -sS -o /tmp/create-repo.json -w '%{http_code}' \
  -X POST \
  -H "Authorization: Bearer ${PAT2}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/orgs/${ORG}/repos" \
  -d "$(printf '{"name":"%s","private":true,"description":"%s","auto_init":false}' "$REPO_NAME" "$DESC")")

case "$http_code" in
  201) echo "    created ${TARGET}" ;;
  422)
    probe=$(curl -sS -o /dev/null -w '%{http_code}' \
      -H "Authorization: Bearer ${PAT2}" \
      "https://api.github.com/repos/${TARGET}")
    if [[ "$probe" == "200" ]]; then
      echo "    exists  ${TARGET}"
    else
      echo "    FAILED create ${TARGET} (422, probe ${probe})" >&2
      cat /tmp/create-repo.json >&2
      exit 1
    fi
    ;;
  *)
    echo "    FAILED create ${TARGET} (HTTP ${http_code})" >&2
    cat /tmp/create-repo.json >&2
    exit 1
    ;;
esac

echo "==> Pushing to ${TARGET} (${TARGET_BRANCH})"
if git remote get-url responsum >/dev/null 2>&1; then
  git remote set-url responsum "$AUTHED_URL"
else
  git remote add responsum "$AUTHED_URL"
fi

git push -u responsum HEAD:"${TARGET_BRANCH}"

echo "Done: https://github.com/${TARGET}"
