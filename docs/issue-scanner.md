# Issue Scanner

Flips the support-agent pipeline's entry point. Instead of waiting for Jira tickets, the
scanner finds issues in the codebase and files tickets. A human triages them before the
autonomous fixer ([automation/agent_watcher.py](../automation/agent_watcher.py)) runs.

## How it works

```
issue_scanner.py
  ├── deterministic pass: npm run build, npx tsc --noEmit
  ├── agent review pass: cursor-agent reviews src/ (read-only)
  ├── dedup: scanner_state.json fingerprints + open-Jira check
  └── create Jira ticket  →  label "support-agent-triage"  (NOT "support-agent")
                                      │
                          human adds "support-agent" label
                                      │
                          existing fixer picks it up → fix + PR
```

The triage label keeps scanner tickets invisible to the fixer, whose query requires
`labels = "support-agent" AND status = "Backlog"`. Nothing in the fixer changes.

## Detection

| Pass | Tool | Confidence | Filed when |
|------|------|------------|------------|
| Deterministic | `npm run build` | High | Always (if it fails) |
| Deterministic | `npx tsc --noEmit` | High | Always (if it fails) |
| Agent review | `cursor-agent` over `src/` | Medium | Severity >= `min_severity` |

Note: the demo baseline compiles cleanly, so the demo's logic bugs (empty
`clearCompleted()`, date off-by-one) are found by the **agent review pass**, not the
deterministic one.

## Run

```bash
export JIRA_API_TOKEN="your-token"

# Single scan
python3 automation/issue_scanner.py automation/agent_watcher_config.json --once

# Continuous (every scan_interval_seconds)
python3 automation/issue_scanner.py automation/agent_watcher_config.json
```

## Triage → fix (the human gate)

1. Review the `support-agent-triage` ticket the scanner filed.
2. If it is a real, in-scope issue, add the `support-agent` label (keep or add the
   triage label as you like) and ensure it is in **Backlog**.
3. The running fixer picks it up on its next poll and proceeds exactly as in the demo
   (semantic runbook search → fix → PR; novel issues also get a new runbook).
4. To reject, close the ticket or leave it in triage. No PR is ever opened from triage.

## Config

Keys in [automation/agent_watcher_config.json](../automation/agent_watcher_config.json):

| Key | Default | Purpose |
|-----|---------|---------|
| `scan_interval_seconds` | `3600` | Delay between scans in loop mode (min 60) |
| `triage_label` | `support-agent-triage` | Label for scanner-filed tickets |
| `scanner_state_file` | `scanner_state.json` | Fingerprint dedup store |
| `scan_paths` | `["src"]` | Directories the agent review covers |
| `min_severity` | `medium` | Minimum severity for agent findings (`low`/`medium`/`high`/`critical`) |
| `max_tickets_per_scan` | `5` | Cap on new tickets per scan (anti-spam) |

## Dedup

Each finding gets a fingerprint (`source + primary file + title`). Before filing, the
scanner skips it if the fingerprint is already in `scanner_state.json` **or** an open
triage ticket already carries that fingerprint marker (`[scanner-fp:<hash>]` in its
description). This stops the same issue being re-filed every scan.

## Safety

- Triage gate: a false positive becomes a triage ticket, never an unreviewed PR.
- Agent review runs read-only; it must not edit files, run git, or open PRs.
- Per-scan cap and severity threshold limit noise.

## Demo reset

`./scripts/demo-reset.sh` clears `scanner_state.json`. It does **not** delete
scanner-filed Jira tickets (they live outside the fixed TEST-1/2/3 demo set); close or
delete those manually if a scan created stray triage tickets.
