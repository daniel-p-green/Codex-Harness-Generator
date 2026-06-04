#!/usr/bin/env python3
"""Format usage-evidence lint JSON as a marker-managed GitHub comment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


MARKER = "<!-- codex-harness-usage-lint -->"

FIELD_LABELS = {
    "outcome": "Outcome",
    "task_summary": "Public-safe task summary",
    "evidence": "Evidence",
    "verification": "Verification performed",
    "privacy_review": "Privacy review",
    "limitations": "Limitations",
}

FIELD_GUIDANCE = {
    "outcome": "Use `success`, `partial`, `failed`, or `inconclusive`.",
    "task_summary": "Summarize one real task without private repo names, secrets, personal data, raw logs, or proprietary source.",
    "evidence": "Add at least two public-safe bullets about what the generated harness helped you do or verify.",
    "verification": "Add at least two bullets naming the checks you actually ran or reviews you performed.",
    "privacy_review": "State that the report excludes secrets, personal data, private paths, proprietary source, raw logs, and raw private transcripts.",
    "limitations": "Add at least one bullet describing the scope limit, such as one task, one repo, one reporter, or incomplete coverage.",
}


def load_payload(path: str) -> dict:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Usage lint payload is not valid JSON: {exc}") from exc


def bullet_lines(values: list[str]) -> list[str]:
    return [f"- {value}" for value in values] if values else ["- none"]


def github_issue_line(payload: dict) -> str:
    issue = payload.get("github_issue") or {}
    number = issue.get("number")
    url = issue.get("url") or ""
    if number and url:
        return f"Issue: #{number} ({url})"
    if number:
        return f"Issue: #{number}"
    return "Issue: unavailable"


def conversion_command_lines(payload: dict) -> list[str]:
    issue = payload.get("github_issue") or {}
    selector = issue.get("url") or issue.get("number") or "<issue-number-or-url>"
    base = (
        "codex-harness usage-from-github-issue "
        f"{selector} "
        "--include-comments "
        "--record-dir Docs/Environment/usage-records "
        "--report Docs/Environment/USAGE_RECORDS.md "
        "--pilot-record-dir Docs/Environment/pilot-records "
        "--pilot-board-report Docs/Environment/PILOT_BOARD.md"
    )
    return [
        "### Maintainer preview command",
        "",
        "Run this before writing a usage record:",
        "",
        "```bash",
        f"{base} --no-write --json",
        "```",
        "",
        "### Maintainer conversion command",
        "",
        "Run this only after previewing the public-safe record:",
        "",
        "```bash",
        f"{base} --json",
        "```",
        "",
    ]


def reply_template_lines(missing_fields: list[str]) -> list[str]:
    if not missing_fields:
        return []
    lines = [
        "### Reporter reply template",
        "",
        "Copy this into a new issue comment and replace each guidance line with your public-safe result:",
        "",
    ]
    for field in missing_fields:
        label = FIELD_LABELS.get(field, field.replace("_", " ").title())
        guidance = FIELD_GUIDANCE.get(field, "Add a public-safe value for this field.")
        lines.extend(
            [
                f"### {label}",
                "",
                guidance,
                "",
            ]
        )
    return lines


def format_comment(payload: dict) -> str:
    status = payload.get("status", "fail")
    readiness = payload.get("readiness", "needs-input")
    errors = list(payload.get("errors") or [])
    warnings = list(payload.get("warnings") or [])
    missing_fields = list(payload.get("missing_fields") or [])
    counts = payload.get("counts") or {}
    github_issue = payload.get("github_issue") or {}

    lines = [
        MARKER,
        "",
        "## Codex Harness usage-evidence lint",
        "",
        github_issue_line(payload),
        f"Status: `{status}`",
        f"Readiness: `{readiness}`",
        f"Comments included: `{str(github_issue.get('comments_included', False)).lower()}`",
        f"Fetched GitHub comment count: `{github_issue.get('total_comment_count', 0)}`",
        f"Reporter comment count: `{github_issue.get('reporter_comment_count', github_issue.get('comment_count', 0))}`",
        "",
        "This automated check only lints public-safe usage evidence. It does not write usage records, convert pilots, or count as adoption proof.",
        "",
    ]
    if readiness == "conversion-ready" and status == "pass":
        lines.extend(
            [
                "Result: ready for maintainer preview.",
                "",
                *conversion_command_lines(payload),
            ]
        )
    else:
        lines.extend(
            [
                "Result: more reporter input is needed before this can be previewed as usage evidence.",
                "",
                "### Missing fields",
                "",
                *bullet_lines(missing_fields),
                "",
                *reply_template_lines(missing_fields),
                "### Errors",
                "",
                *bullet_lines(errors),
                "",
            ]
        )

    lines.extend(
        [
            "### Warnings",
            "",
            *bullet_lines(warnings),
            "",
            "### Evidence counts",
            "",
            f"- Evidence bullets: `{counts.get('evidence', 0)}`",
            f"- Verification bullets: `{counts.get('verification', 0)}`",
            f"- Limitation bullets: `{counts.get('limitations', 0)}`",
            "",
            "### Privacy boundary",
            "",
            "Do not include secrets, personal data, private repository names, local machine paths, proprietary source, raw logs, or raw private transcripts.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="usage-from-github-issue --lint-only JSON file, or '-' for stdin")
    parser.add_argument("--out", help="Optional Markdown output path")
    args = parser.parse_args()

    comment = format_comment(load_payload(args.payload))
    if args.out:
        Path(args.out).write_text(comment, encoding="utf-8")
    else:
        print(comment, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
