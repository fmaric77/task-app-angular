# Support Agent Initiative — Conversation Notes

**Date:** 2026-06-18  
**Topic:** Research prep for client support agents (app dev solutions)

Source: [support-agent-poc](https://github.com/fmaric77/support-agent-poc)

---

## Goal

Build support agents for app dev solutions using **Agentic Cursor** + **Jira MCP** + **Runbooks**.

Flow: agent reads ticket → finds solution in runbook → proposes or executes fix.

---

## Runbook strategy

| Approach | When to use |
|----------|-------------|
| PDF/markdown in context | Small runbooks (few pages) |
| Vectorization (RAG) | Many/large runbooks |
| Confluence via Atlassian MCP | Runbooks live in Confluence |
| **Markdown in repo** | **Current approach** — Cursor codebase index handles semantic search |

Start with markdown in `runbooks/`; add RAG only if precision drops as content grows.

---

## PoC test scenarios

1. Agent reads runbook from repo (no RAG) — does it answer correctly?
2. Jira MCP read-only — can it fetch a ticket?
3. End-to-end: ticket description → agent finds runbook → proposes fix

---

## This repo

Combines Angular TaskApp (Cursor enablement demo) with support agent PoC:

- `runbooks/` — markdown playbooks (read-only for agent)
- `src/` — Angular TaskApp (agent may edit)
- `.cursor/skills/support-workflow/` — autonomous ticket workflow
- `AGENTS.md` — cloud agent permissions and runbook mapping

See [cursor-automation-setup.md](./cursor-automation-setup.md) for cloud deployment.
