---
name: support-workflow
description: Autonomous support agent workflow for Jira tickets. Use when processing a support ticket — read runbook, fix bug, push PR, update Jira, handle review feedback.
---

# Support Workflow

## When triggered

A Jira ticket with label `support-agent` needs resolution.

## Steps

### 1. Understand the ticket

- Fetch ticket via Jira MCP (`jira_get_issue`)
- Read summary, description, labels — **user report only** (symptoms, expected behavior)
- Do **not** use the ticket description for file paths, root cause, or fix steps

### 2. Find the runbook (semantic search)

- **Semantically search** `runbooks/` for a playbook matching the symptoms (by meaning, not just filename)
- If one matches: follow its diagnosis and fix steps exactly
- If **none** matches: this is a **novel issue** — diagnose from `src/` yourself
- Never modify an **existing** runbook

### 3. Apply the fix

- Edit files under `src/`
- If a runbook matched, follow its fix section
- If novel: after fixing, **create** a new `runbooks/<slug>.md` documenting the issue (Symptoms, Root cause, Diagnosis, Fix, Verification) and flag the PR as an unguided fix
- Keep changes minimal and focused

### 4. Verify locally

```bash
npm install
npm run build
```

Follow any manual verification steps in the runbook.

### 5. Create branch, commit, push

```bash
git checkout -b fix/<TICKET-KEY>-<short-slug>
git add src/ runbooks/   # include the new runbook if this was a novel issue
git commit -m "fix(<TICKET-KEY>): <summary>"
git push -u origin fix/<TICKET-KEY>-<short-slug>
```

### 6. Open PR

```bash
gh pr create \
  --repo fmaric77/task-app-angular \
  --title "[<TICKET-KEY>] <summary>" \
  --body "Fixes <TICKET-KEY>\n\n## Changes\n- <description>\n\n## Runbook\n- runbooks/<name>.md"
```

### 7. Update Jira

- `jira_add_comment`: post PR URL and summary of fix
- `jira_transition_issue`: move to "In Review" or equivalent

### 8. Handle PR review feedback

When review comments arrive:

1. Read the feedback
2. Apply requested changes on the same branch
3. Push updates
4. `jira_add_comment`: note that review feedback was addressed

## Runbook mapping

| Symptom / Label | Runbook |
|-----------------|---------|
| Clear completed does nothing | `runbooks/clear-completed-noop.md` |
| `clear-completed`, `filter` | `runbooks/clear-completed-noop.md` |
| Wrong month on task date | `runbooks/date-format-off-by-one.md` |
| `date`, `display` | `runbooks/date-format-off-by-one.md` |
| Add task priority levels | `runbooks/task-priority-levels.md` |
| `priority`, `feature` | `runbooks/task-priority-levels.md` |
