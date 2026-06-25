#!/usr/bin/env bash
# Test a Cursor Automation webhook trigger.
# Usage: ./scripts/test-cursor-webhook.sh <webhook-url> <crsr-token>
set -euo pipefail

WEBHOOK_URL="${1:?Usage: $0 <webhook-url> <crsr-token>}"
TOKEN="${2:?Usage: $0 <webhook-url> <crsr-token>}"

curl -s -w "\nHTTP %{http_code}\n" -X POST "$WEBHOOK_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "jira.issue_labeled",
    "issueKey": "TEST-1",
    "summary": "[Support Agent PoC] Clear completed button does nothing — test scenario 1"
  }'
