# Demo Reset

Restore the repo and Jira tickets so you can re-run the support-agent demo from scratch.

**Presenter walkthrough:** [demo-script.md](./demo-script.md)

## What gets reset

| Item | After reset |
|------|-------------|
| **Git `main`** | `demo-baseline` tag (`91dfe4b`) — bugs unresolved |
| **Fix branches** | Deleted locally (and remotely with `--push`) |
| **Watcher state** | `automation/agent_watcher_state.json` cleared |
| **Jira TEST-1, TEST-2, TEST-3** | Backlog + user-voice summary/description restored + "demo reset" comment |

## Known bugs at baseline

- `clearCompleted()` is empty (`runbooks/clear-completed-noop.md`)
- No priority feature (`runbooks/task-priority-levels.md`)
- Date off-by-one (`runbooks/date-format-off-by-one.md`)

## Run

```bash
export JIRA_API_TOKEN="your-token"

# Local reset only (main reset locally, no remote changes)
./scripts/demo-reset.sh

# Full reset including GitHub (force-push main, delete fix branches)
./scripts/demo-reset.sh --push
```

Then start the demo:

```bash
npm start
python3 automation/agent_watcher.py automation/agent_watcher_config.json
```

## Options

| Env var | Default | Purpose |
|---------|---------|---------|
| `DEMO_BASELINE_COMMIT` | `demo-baseline` | Git ref to restore |
| `DEMO_TICKETS` | `TEST-1,TEST-2,TEST-3` | Comma-separated Jira keys |
| `DEMO_BACKLOG_STATUS` | `Backlog` | Target Jira status |

## Notes

- Merged PRs (#1, #2) stay in GitHub history — new runs open PR #3, #4, etc.
- `--push` rewrites remote `main`; coordinate if others use the repo.
- Old Jira PR comments remain but are marked obsolete by the reset comment.
- Jira descriptions are **user reports only** (symptoms, no file paths). Runbooks hold the fix procedure.
