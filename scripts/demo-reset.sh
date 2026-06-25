#!/usr/bin/env bash
# Reset repo + Jira + watcher state for another support-agent demo run.
#
# Usage:
#   export JIRA_API_TOKEN="..."
#   ./scripts/demo-reset.sh              # local reset only
#   ./scripts/demo-reset.sh --push       # also force-push main + delete remote fix branches
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE="${DEMO_BASELINE_COMMIT:-demo-baseline}"
TICKETS="${DEMO_TICKETS:-TEST-1,TEST-2,TEST-3}"
FIX_BRANCHES=(
  fix/test-1-clear-completed
  fix/test-2-task-priority-levels
)
PUSH=false

for arg in "$@"; do
  case "$arg" in
    --push) PUSH=true ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg (try --push)" >&2
      exit 1
      ;;
  esac
done

cd "$REPO_ROOT"

echo "==> Stopping agent watcher (if running)"
pkill -f "agent_watcher.py" 2>/dev/null || true

echo "==> Ensuring demo baseline tag exists"
if ! git rev-parse -q --verify "$BASELINE" >/dev/null 2>&1; then
  git tag -f demo-baseline 91dfe4b
  echo "    tagged demo-baseline -> 91dfe4b"
fi
BASELINE_SHA="$(git rev-parse "$BASELINE")"
echo "    baseline: $BASELINE ($BASELINE_SHA)"

echo "==> Resetting git to demo baseline"
git fetch origin
git checkout main
git reset --hard "$BASELINE_SHA"

echo "==> Removing local fix branches"
for branch in "${FIX_BRANCHES[@]}"; do
  git branch -D "$branch" 2>/dev/null && echo "    deleted local $branch" || true
done

if [[ "$PUSH" == "true" ]]; then
  echo "==> Force-pushing main to origin"
  git push --force origin main
  echo "==> Deleting remote fix branches"
  for branch in "${FIX_BRANCHES[@]}"; do
    git push origin --delete "$branch" 2>/dev/null && echo "    deleted remote $branch" || true
  done
else
  echo "    (skip remote update — pass --push to force-push main and delete remote branches)"
fi

echo "==> Clearing agent watcher state"
printf '%s\n' '{"tickets": {}}' > automation/agent_watcher_state.json

echo "==> Clearing issue scanner state"
printf '%s\n' '{"issues": {}}' > automation/scanner_state.json

echo "==> Resetting Jira tickets: $TICKETS"
if [[ -z "${JIRA_API_TOKEN:-}" ]]; then
  echo "ERROR: JIRA_API_TOKEN is required for Jira reset" >&2
  exit 1
fi
python3 scripts/demo-reset-jira.py --tickets "$TICKETS"

echo "==> Verifying build"
npm run build --silent

echo ""
echo "Demo reset complete."
echo "  Repo:  main @ $BASELINE_SHA (bugs unresolved)"
echo "  Jira:  $TICKETS -> Backlog"
echo "  State: automation/agent_watcher_state.json cleared"
echo ""
echo "Next:"
echo "  npm start"
echo "  python3 automation/agent_watcher.py automation/agent_watcher_config.json"
