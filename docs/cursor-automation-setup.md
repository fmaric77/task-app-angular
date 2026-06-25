# Cursor Cloud Automation Setup

Replace the local `automation/agent_watcher.py` with two Cursor Automations running on Cursor's cloud VMs.

## Prerequisites

1. **Paid Cursor plan** (Cloud Agents require Teams or paid plan)
2. **GitHub connected** in [Cloud Agents dashboard](https://cursor.com/agents)
3. **Repo connected:** `fmaric77/task-app-angular`

## Step 1: Cloud secrets

Go to [cursor.com → Settings → Cloud Agents → Secrets](https://cursor.com/settings) and add:

| Secret | Value |
|--------|-------|
| `JIRA_URL` | `https://iolap-inc.atlassian.net` |
| `JIRA_USERNAME` | `filip.maric@elixirr.com` |
| `JIRA_API_TOKEN` | Your Atlassian API token |

## Step 2: Jira MCP in cloud (dashboard — required)

**API inline `mcpServers` does not attach on this account.** Add Jira in the dashboard:

1. Go to [cursor.com/agents](https://cursor.com/agents) → **MCP** (or your Automation → Tools → MCP server)
2. Paste this **single flat object** (no `mcpServers` wrapper, no `jira` key):

```json
{
  "command": "uvx",
  "args": ["mcp-atlassian"],
  "env": {
    "JIRA_URL": "https://iolap-inc.atlassian.net",
    "JIRA_USERNAME": "filip.maric@elixirr.com",
    "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
  }
}
```

3. Ensure Cloud secrets (Step 1) include `JIRA_API_TOKEN` — the `${JIRA_API_TOKEN}` reference resolves from secrets.

**Alternative (OAuth, no API token):**
```json
{
  "url": "https://mcp.atlassian.com/v1/mcp"
}
```

**Do NOT paste:**
- `{ "mcpServers": { ... } }` — causes "must have command or url"
- `{ "jira": { ... } }` — causes "only one server"

Re-run the agent/automation after MCP shows as connected.

## Step 3: Automation 1 — New Jira tickets

Create at [cursor.com/automations](https://cursor.com/automations):

| Setting | Value |
|---------|-------|
| **Name** | Support Agent — New Tickets |
| **Trigger** | Scheduled — every 15 minutes |
| **Repository** | `fmaric77/task-app-angular` / `main` |
| **Tools** | MCP server (Jira), Pull request creation |
| **Prompt** | Copy from `.cursor/automation-prompts/new-ticket.md` |

### Optional: Real-time Jira webhook (instead of schedule)

1. Save the automation first → copy **Webhook URL** and **Auth header** (`Bearer crsr_...`)
2. In Jira: **Project settings → Automation → Create rule**
3. Trigger: **Issue labeled** → `support-agent`
4. Action: **Send web request**
   - URL: Cursor webhook URL
   - Method: POST
   - Headers: `Authorization: Bearer crsr_<your-token>`, `Content-Type: application/json`
   - Body:
   ```json
   {
     "event": "jira.issue_labeled",
     "issueKey": "{{issue.key}}",
     "summary": "{{issue.summary}}"
   }
   ```

Test webhook:
```bash
./scripts/test-cursor-webhook.sh <webhook-url> <crsr-token>
```

## Step 4: Automation 2 — PR review feedback

Create second automation:

| Setting | Value |
|---------|-------|
| **Name** | Support Agent — PR Feedback |
| **Trigger** | GitHub → Pull request commented |
| **Repository** | `fmaric77/task-app-angular` |
| **Tools** | MCP server (Jira), Comment on pull request |
| **Prompt** | Copy from `.cursor/automation-prompts/pr-feedback.md` |

This handles human review comments on agent PRs and updates Jira.

## Step 5: Stop local watcher

```bash
pkill -f "automation/agent_watcher.py"
```

The cloud automations replace the local poller.

## Step 6: Test

1. Reset a known bug on `main` (see runbooks) or create new ticket
2. Create Jira ticket in TEST with label `support-agent`, status Backlog
3. Wait for scheduled run (or fire webhook)
4. Verify: PR opened, Jira commented, ticket → In Progress
5. Leave a PR review comment → Automation 2 should address it

## Architecture

```
Jira (label=support-agent)
  → [schedule or webhook] → Cursor Cloud Agent
  → reads runbook → fixes src/ → opens PR → updates Jira

GitHub (PR comment)
  → Cursor Cloud Agent
  → applies feedback → pushes → comments Jira + PR
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Webhook 401 | Regenerate auth header in Automations dashboard; Jira must send `Authorization: Bearer crsr_...` |
| MCP not available in cloud | Add MCP in cursor.com/agents; use HTTP MCP if stdio fails |
| Agent can't push | Ensure GitHub integration connected; private automations push as your account |
| No tickets found | Check JQL status is `Backlog` (TEST project uses Backlog, not To Do) |
