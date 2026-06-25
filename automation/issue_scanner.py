#!/usr/bin/env python3
"""Issue scanner — finds bugs/issues in the codebase and files Jira triage tickets.

Hybrid detection:
  1. Deterministic pass: `npm run build` + `npx tsc --noEmit` (high confidence).
  2. Agent review pass: cursor-agent reviews src/ read-only for logic bugs.

Discovered issues are deduped (fingerprint store + open-Jira check) and filed under a
triage label, kept separate from the fixer's `support-agent` label. A human promotes a
triage ticket (adds the support-agent label) before the autonomous fixer in
agent_watcher.py picks it up.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_watcher import (
    Config,
    ConfigError,
    jira_request,
    jira_search,
    load_config,
    load_json,
    log,
    run_cursor_agent,
    save_json,
)

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

FINDINGS_START = "<FINDINGS>"
FINDINGS_END = "</FINDINGS>"
FP_MARKER = "scanner-fp"
FILED_BY = "issue-scanner"

SRC_PATH_RE = re.compile(r"\b(src/[\w./-]+\.(?:ts|html|scss|css))\b")
TSC_ERROR_RE = re.compile(r"^(.+?\.ts)\((\d+),(\d+)\): error (TS\d+): (.+)$")


@dataclass
class ScannerConfig:
    base: Config
    scan_interval_seconds: int
    triage_label: str
    scanner_state_file: Path
    scan_paths: list[str]
    min_severity: str
    max_tickets_per_scan: int


@dataclass
class Finding:
    title: str
    severity: str
    files: list[str]
    symptom: str
    source: str  # "build" | "tsc" | "agent"
    suggested_labels: list[str] = field(default_factory=list)
    evidence: str = ""

    def fingerprint(self) -> str:
        primary_file = self.files[0] if self.files else ""
        norm = f"{self.source}|{primary_file}|{self.title.strip().lower()}"
        return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def load_scanner_config(path: Path) -> ScannerConfig:
    base = load_config(path)
    raw = load_json(path)
    state_file = Path(raw.get("scanner_state_file", "scanner_state.json")).expanduser()
    if not state_file.is_absolute():
        state_file = base.workspace / state_file
    min_severity = str(raw.get("min_severity", "medium")).lower()
    if min_severity not in SEVERITY_ORDER:
        min_severity = "medium"
    return ScannerConfig(
        base=base,
        scan_interval_seconds=max(60, int(raw.get("scan_interval_seconds", 3600))),
        triage_label=raw.get("triage_label", "support-agent-triage"),
        scanner_state_file=state_file,
        scan_paths=list(raw.get("scan_paths", ["src"])),
        min_severity=min_severity,
        max_tickets_per_scan=max(1, int(raw.get("max_tickets_per_scan", 5))),
    )


def extract_src_files(text: str) -> list[str]:
    seen: list[str] = []
    for match in SRC_PATH_RE.findall(text):
        if match not in seen:
            seen.append(match)
    return seen


# ---------------------------------------------------------------------------
# Deterministic pass
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_build_check(cfg: ScannerConfig) -> list[Finding]:
    log("Deterministic: npm run build")
    try:
        result = _run(["npm", "run", "build"], cfg.base.workspace, timeout=900)
    except (subprocess.TimeoutExpired, OSError) as exc:
        log(f"build check skipped: {exc}")
        return []
    if result.returncode == 0:
        return []
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    files = extract_src_files(output)
    return [
        Finding(
            title="Build fails: npm run build returns errors",
            severity="high",
            files=files,
            symptom="The app does not build; users cannot get a working release.",
            source="build",
            suggested_labels=["build"],
            evidence=output[-1800:].strip(),
        )
    ]


def run_tsc_check(cfg: ScannerConfig) -> list[Finding]:
    log("Deterministic: npx tsc --noEmit")
    try:
        result = _run(["npx", "tsc", "--noEmit"], cfg.base.workspace, timeout=600)
    except (subprocess.TimeoutExpired, OSError) as exc:
        log(f"tsc check skipped: {exc}")
        return []
    if result.returncode == 0:
        return []
    output = (result.stdout or "") + "\n" + (result.stderr or "")
    findings: list[Finding] = []
    for line in output.splitlines():
        m = TSC_ERROR_RE.match(line.strip())
        if not m:
            continue
        file_path, _line, _col, code, message = m.groups()
        findings.append(
            Finding(
                title=f"Type error {code}: {message[:80]}",
                severity="high",
                files=[file_path],
                symptom=f"TypeScript reports {code} in {file_path}: {message}",
                source="tsc",
                suggested_labels=["typescript"],
                evidence=line.strip(),
            )
        )
    if not findings:
        findings.append(
            Finding(
                title="Type check fails: npx tsc --noEmit returns errors",
                severity="high",
                files=extract_src_files(output),
                symptom="TypeScript type checking fails.",
                source="tsc",
                suggested_labels=["typescript"],
                evidence=output[-1800:].strip(),
            )
        )
    return findings


# ---------------------------------------------------------------------------
# Agent review pass
# ---------------------------------------------------------------------------

def build_review_prompt(cfg: ScannerConfig) -> str:
    paths = ", ".join(cfg.scan_paths)
    return f"""You are a READ-ONLY code reviewer for this Angular repository.

STRICT RULES:
- Do NOT edit, create, or delete any files.
- Do NOT run git, do NOT commit, do NOT open pull requests.
- Only read and analyze code.

TASK:
Review the code under: {paths}
Find genuine BUGS, logic errors, or clear defects that affect users (e.g. a feature
that silently does nothing, an off-by-one, incorrect state handling). Ignore style
preferences, formatting, and minor nits.

OUTPUT:
Return ONLY a JSON array of findings between the markers {FINDINGS_START} and {FINDINGS_END}.
Each finding is an object:
{{"title": "short imperative title",
  "severity": "low|medium|high|critical",
  "files": ["src/..."],
  "symptom": "the user-visible problem in plain language (no file paths or root cause)",
  "suggested_labels": ["one-or-two", "kebab-case-labels"]}}

If you find nothing, return an empty array.
Example:
{FINDINGS_START}
[{{"title": "Clear completed does nothing", "severity": "high", "files": ["src/app/services/task.service.ts"], "symptom": "Clicking Clear completed leaves finished tasks in the list.", "suggested_labels": ["clear-completed"]}}]
{FINDINGS_END}
"""


def parse_findings(output: str) -> list[Finding]:
    start = output.find(FINDINGS_START)
    end = output.find(FINDINGS_END, start + 1)
    if start == -1 or end == -1:
        # Fallback: try to find a bare JSON array.
        bracket = output.find("[")
        if bracket == -1:
            return []
        raw = output[bracket:]
    else:
        raw = output[start + len(FINDINGS_START):end]
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Best effort: trim to last closing bracket.
        last = raw.rfind("]")
        if last == -1:
            return []
        try:
            data = json.loads(raw[: last + 1])
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    findings: list[Finding] = []
    for item in data:
        if not isinstance(item, dict) or not item.get("title"):
            continue
        severity = str(item.get("severity", "medium")).lower()
        if severity not in SEVERITY_ORDER:
            severity = "medium"
        files = [str(f) for f in item.get("files", []) if isinstance(f, str)]
        labels = [str(l) for l in item.get("suggested_labels", []) if isinstance(l, str)]
        findings.append(
            Finding(
                title=str(item["title"]).strip(),
                severity=severity,
                files=files,
                symptom=str(item.get("symptom", "")).strip(),
                source="agent",
                suggested_labels=labels,
                evidence="Flagged by agent code review.",
            )
        )
    return findings


def run_agent_review(cfg: ScannerConfig) -> list[Finding]:
    log("Agent review pass over: " + ", ".join(cfg.scan_paths))
    prompt = build_review_prompt(cfg)
    output = run_cursor_agent(cfg.base, prompt)
    findings = parse_findings(output)
    log(f"Agent review returned {len(findings)} finding(s)")
    return findings


# ---------------------------------------------------------------------------
# Dedup + ticket creation
# ---------------------------------------------------------------------------

def jira_has_fingerprint(cfg: ScannerConfig, fingerprint: str) -> bool:
    jql = (
        f'project = {cfg.base.jira_project} AND labels = "{cfg.triage_label}" '
        f'AND description ~ "{FP_MARKER}:{fingerprint}"'
    )
    try:
        issues = jira_search(cfg.base, jql, limit=1)
    except RuntimeError as exc:
        log(f"Jira dedup search failed (continuing on state only): {exc}")
        return False
    return bool(issues)


def build_ticket_description(finding: Finding, fingerprint: str) -> str:
    files = "\n".join(f"- {f}" for f in finding.files) or "- (not localized)"
    evidence = finding.evidence.strip() or "(none)"
    return (
        f"## What's happening\n\n{finding.symptom or finding.title}\n\n"
        f"## Where (suspected)\n\n{files}\n\n"
        f"## Evidence ({finding.source})\n\n"
        f"```\n{evidence[:1500]}\n```\n\n"
        f"---\n"
        f"_Filed automatically by the issue scanner. Promote to the fixer by adding "
        f"the `support-agent` label once triaged._\n\n"
        f"[{FP_MARKER}:{fingerprint}] [filed-by:{FILED_BY}]"
    )


def create_triage_ticket(cfg: ScannerConfig, finding: Finding, fingerprint: str) -> str:
    # Keep the fixer's base label out so triage tickets are not auto-processed.
    labels = [cfg.triage_label]
    for label in finding.suggested_labels:
        if label and label != cfg.base.jira_label and label not in labels:
            labels.append(label)

    body = {
        "fields": {
            "project": {"key": cfg.base.jira_project},
            "summary": f"[Scanner] {finding.title}"[:240],
            "description": build_ticket_description(finding, fingerprint),
            "issuetype": {"name": "Bug"},
            "labels": labels,
        }
    }
    result = jira_request(cfg.base, "POST", "/rest/api/2/issue", body)
    return result.get("key", "(unknown)")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def collect_findings(cfg: ScannerConfig) -> list[Finding]:
    findings: list[Finding] = []
    findings += run_build_check(cfg)
    findings += run_tsc_check(cfg)
    findings += run_agent_review(cfg)
    return findings


def passes_threshold(cfg: ScannerConfig, finding: Finding) -> bool:
    # Deterministic findings are always filed; agent findings must meet min_severity.
    if finding.source in ("build", "tsc"):
        return True
    return SEVERITY_ORDER.get(finding.severity, 1) >= SEVERITY_ORDER[cfg.min_severity]


def scan_once(cfg: ScannerConfig) -> int:
    state = load_json(cfg.scanner_state_file) if cfg.scanner_state_file.exists() else {"issues": {}}
    issues_state = state.setdefault("issues", {})

    findings = [f for f in collect_findings(cfg) if passes_threshold(cfg, f)]
    log(f"{len(findings)} finding(s) over threshold (min_severity={cfg.min_severity})")

    created = 0
    skipped_dupe = 0
    for finding in findings:
        if created >= cfg.max_tickets_per_scan:
            log(f"Reached max_tickets_per_scan ({cfg.max_tickets_per_scan}); stopping.")
            break

        fingerprint = finding.fingerprint()
        if fingerprint in issues_state:
            skipped_dupe += 1
            continue
        if jira_has_fingerprint(cfg, fingerprint):
            issues_state[fingerprint] = {
                "key": "(existing)",
                "title": finding.title,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            save_json(cfg.scanner_state_file, state)
            skipped_dupe += 1
            continue

        try:
            key = create_triage_ticket(cfg, finding, fingerprint)
        except RuntimeError as exc:
            log(f"Ticket creation failed for '{finding.title}': {exc}")
            continue

        issues_state[fingerprint] = {
            "key": key,
            "title": finding.title,
            "severity": finding.severity,
            "source": finding.source,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        save_json(cfg.scanner_state_file, state)
        created += 1
        log(f"Filed triage ticket {key}: {finding.title}")

    log(f"Scan complete. Filed {created}, skipped {skipped_dupe} duplicate(s).")
    return 0


def scan_forever(cfg: ScannerConfig) -> int:
    while True:
        try:
            scan_once(cfg)
        except KeyboardInterrupt:
            log("Stopped by user")
            return 130
        except Exception as exc:  # noqa: BLE001 - keep the loop alive
            log(f"Scan error: {exc}")
        log(f"Sleeping {cfg.scan_interval_seconds}s")
        time.sleep(cfg.scan_interval_seconds)


USAGE = "Usage: python3 issue_scanner.py <config.json> [--once]"


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(USAGE, file=sys.stderr)
        return 2

    config_path = Path(argv[1]).expanduser()
    flags = argv[2:]
    unknown = [a for a in flags if a != "--once"]
    if unknown:
        print(f"Unknown argument(s): {' '.join(unknown)}\n{USAGE}", file=sys.stderr)
        return 2
    once = "--once" in flags

    try:
        cfg = load_scanner_config(config_path)
    except (OSError, json.JSONDecodeError, ConfigError) as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    if once:
        return scan_once(cfg)
    return scan_forever(cfg)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
