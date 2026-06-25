#!/usr/bin/env python3
"""Reset support-agent demo Jira tickets to Backlog for another run."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_JIRA_URL = "https://iolap-inc.atlassian.net"
DEFAULT_USERNAME = "filip.maric@elixirr.com"

# User-voice ticket text (no file paths, root cause, or runbook spoilers).
DEMO_TICKET_FIELDS: dict[str, dict[str, str]] = {
    "TEST-1": {
        "summary": "[Support Agent PoC] Clear completed button doesn't remove finished tasks",
        "description": (
            "## What I'm seeing\n\n"
            "I complete tasks and click **Clear completed**, but nothing happens — "
            "completed tasks stay in the list and the count doesn't go down.\n\n"
            "## What I expected\n\n"
            "Completed tasks should be removed when I click **Clear completed**.\n\n"
            "## Notes\n\n"
            "- Reproduces every time\n"
            "- Active tasks and the completion toggle still work fine"
        ),
    },
    "TEST-2": {
        "summary": "[Support Agent PoC] Add priority levels to tasks",
        "description": (
            "## What I want\n\n"
            "I want to mark tasks as High, Medium, or Low priority so I can focus on what's important.\n\n"
            "## What I'd expect\n\n"
            "- New tasks start at Medium unless I change them\n"
            "- I can tell priority at a glance (e.g. a colored indicator near the title)\n"
            "- I can change priority easily\n"
            "- Option to sort the list so high-priority items show first\n"
            "- Priority should still be there after I refresh the page\n\n"
            "## Notes\n\n"
            "Existing tasks without a stored priority should behave like Medium."
        ),
    },
    "TEST-3": {
        "summary": '[Support Agent PoC] Task "Added" date shows wrong month',
        "description": (
            "## What I'm seeing\n\n"
            "The **Added** date on tasks shows the wrong month. For example, a task I create "
            "today in June displays as `5/24/2026` instead of `6/24/2026`.\n\n"
            "## What I expected\n\n"
            "The month should match when I actually created the task.\n\n"
            "## Notes\n\n"
            "- Happens on every task\n"
            "- Title and done checkbox work normally"
        ),
    },
}


def jira_request(
    jira_url: str,
    auth_header: str,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> Any:
    url = f"{jira_url.rstrip('/')}{path}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def get_transitions(jira_url: str, auth_header: str, issue_key: str) -> list[dict[str, Any]]:
    payload = jira_request(jira_url, auth_header, "GET", f"/rest/api/2/issue/{issue_key}/transitions")
    return payload.get("transitions", [])


def transition_issue(
    jira_url: str,
    auth_header: str,
    issue_key: str,
    transition_name: str,
    comment: str,
) -> None:
    transitions = get_transitions(jira_url, auth_header, issue_key)
    match = next((t for t in transitions if t.get("name") == transition_name), None)
    if not match:
        available = [t.get("name") for t in transitions]
        raise RuntimeError(f"No transition '{transition_name}' for {issue_key}. Available: {available}")

    jira_request(
        jira_url,
        auth_header,
        "POST",
        f"/rest/api/2/issue/{issue_key}/transitions",
        {
            "transition": {"id": match["id"]},
            "update": {"comment": [{"add": {"body": comment}}]},
        },
    )


def add_comment(jira_url: str, auth_header: str, issue_key: str, body: str) -> None:
    jira_request(
        jira_url,
        auth_header,
        "POST",
        f"/rest/api/2/issue/{issue_key}/comment",
        {"body": body},
    )


def restore_ticket_fields(jira_url: str, auth_header: str, issue_key: str) -> None:
    fields = DEMO_TICKET_FIELDS.get(issue_key)
    if not fields:
        return
    jira_request(
        jira_url,
        auth_header,
        "PUT",
        f"/rest/api/2/issue/{issue_key}",
        {"fields": {"summary": fields["summary"], "description": fields["description"]}},
    )
    print(f"  {issue_key}: restored user-voice summary/description")


def reset_ticket(jira_url: str, auth_header: str, issue_key: str, backlog_status: str) -> None:
    restore_ticket_fields(jira_url, auth_header, issue_key)

    comment = (
        f"**Demo reset** — ticket reopened for another support-agent run.\n\n"
        f"Previous PR comments are **obsolete**. Process this ticket as new.\n"
        f"Only skip if there is an **open** PR for `{issue_key}` on task-app-angular."
    )

    try:
        transition_issue(jira_url, auth_header, issue_key, backlog_status, comment)
        print(f"  {issue_key}: transitioned to {backlog_status}")
    except RuntimeError as exc:
        if "No transition" in str(exc):
            add_comment(jira_url, auth_header, issue_key, comment)
            print(f"  {issue_key}: already in target state, comment added")
            return
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset demo Jira tickets to Backlog")
    parser.add_argument(
        "--tickets",
        default=os.environ.get("DEMO_TICKETS", "TEST-1,TEST-2,TEST-3"),
        help="Comma-separated ticket keys",
    )
    parser.add_argument(
        "--backlog-status",
        default=os.environ.get("DEMO_BACKLOG_STATUS", "Backlog"),
        help="Jira status name for reopened tickets",
    )
    args = parser.parse_args()

    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if not token:
        print("ERROR: JIRA_API_TOKEN is required", file=sys.stderr)
        return 1

    jira_url = os.environ.get("JIRA_URL", DEFAULT_JIRA_URL)
    username = os.environ.get("JIRA_USERNAME", DEFAULT_USERNAME)
    auth_header = "Basic " + base64.b64encode(f"{username}:{token}".encode()).decode()

    tickets = [key.strip() for key in args.tickets.split(",") if key.strip()]
    print(f"Resetting {len(tickets)} ticket(s) to {args.backlog_status}...")

    for issue_key in tickets:
        try:
            reset_ticket(jira_url, auth_header, issue_key, args.backlog_status)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            print(f"  {issue_key}: FAILED ({exc.code}) {body[:200]}", file=sys.stderr)
            return 1

    print("Jira reset complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
