#!/usr/bin/env python3
"""Attach Jira MCP to a Cursor cloud agent via API."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
import base64
from pathlib import Path


def load_env() -> dict[str, str]:
    env_file = Path(__file__).resolve().parents[1] / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    mcp = json.loads(Path.home().joinpath(".cursor/mcp.json").read_text())
    jira = mcp["mcpServers"]["jira"]["env"]
    return {
        "CURSOR_API_KEY": os.environ["CURSOR_API_KEY"],
        "JIRA_URL": jira["JIRA_URL"],
        "JIRA_USERNAME": jira["JIRA_USERNAME"],
        "JIRA_API_TOKEN": jira["JIRA_API_TOKEN"],
    }


def api_request(method: str, url: str, api_key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    cred = base64.b64encode(f"{api_key}:".encode()).decode()
    req.add_header("Authorization", f"Basic {cred}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def jira_mcp_config(env: dict[str, str]) -> list[dict]:
    return [
        {
            "name": "jira",
            "type": "stdio",
            "command": "uvx",
            "args": ["mcp-atlassian"],
            "env": {
                "JIRA_URL": env["JIRA_URL"],
                "JIRA_USERNAME": env["JIRA_USERNAME"],
                "JIRA_API_TOKEN": env["JIRA_API_TOKEN"],
            },
        }
    ]


def create_jira_agent(env: dict[str, str], prompt: str) -> dict:
    return api_request(
        "POST",
        "https://api.cursor.com/v1/agents",
        env["CURSOR_API_KEY"],
        {
            "name": "Support Agent — Jira",
            "prompt": {"text": prompt},
            "repos": [{"url": "https://github.com/fmaric77/task-app-angular", "startingRef": "main"}],
            "mcpServers": jira_mcp_config(env),
            "autoCreatePR": False,
        },
    )


def attach_to_agent(env: dict[str, str], agent_id: str, prompt: str) -> dict:
    return api_request(
        "POST",
        f"https://api.cursor.com/v1/agents/{agent_id}/runs",
        env["CURSOR_API_KEY"],
        {
            "prompt": {"text": prompt},
            "mcpServers": jira_mcp_config(env),
        },
    )


def main() -> int:
    env = load_env()
    agent_id = sys.argv[1] if len(sys.argv) > 1 else None
    prompt = (
        "Test Jira MCP: run jira_search for "
        '`project = TEST AND labels = "support-agent"` then jira_get_issue on the newest ticket. '
        "Summarize key, status, summary. No code changes."
    )
    if agent_id:
        result = attach_to_agent(env, agent_id, prompt)
        print(json.dumps({"action": "follow_up", "run": result.get("run", result)}, indent=2))
    else:
        result = create_jira_agent(env, prompt)
        print(
            json.dumps(
                {
                    "action": "create",
                    "agent_id": result["agent"]["id"],
                    "agent_url": result["agent"]["url"],
                    "run_id": result["run"]["id"],
                    "run_status": result["run"]["status"],
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
