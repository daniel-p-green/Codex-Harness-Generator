#!/usr/bin/env python3
"""Audit a legacy Claude-style harness for Codex migration work."""

from __future__ import annotations

import argparse
import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path


LEGACY_PATHS = {
    "CLAUDE.md": "Move durable project instructions into AGENTS.md.",
    ".claude/settings.json": "Translate JSON settings into .codex/config.toml.",
    ".claude/agents": "Rewrite Markdown/frontmatter agents as .codex/agents/*.toml.",
    ".claude/commands": "Move slash-command behavior into AGENTS.md routing or .agents/skills.",
    ".claude/hooks": "Replace hooks with explicit validation commands or documented Codex workflows.",
    ".claude/skills": "Move reusable skills under .agents/skills/<name>/SKILL.md.",
    ".claudeignore": "Replace ignore-file assumptions with explicit permission and workflow guidance.",
}

CODEX_PATHS = {
    "AGENTS.md": "Project-level Codex instructions.",
    ".codex/config.toml": "Codex configuration, permissions, subagents, and skills.",
    ".codex/agents": "Codex subagent TOML definitions.",
    ".agents/skills": "Codex skill directories.",
}

LEGACY_TEXT_PATTERNS = (
    (re.compile(r"\bWebSearch\b"), "Replace legacy WebSearch wording with browser or web-search guidance that matches the active Codex environment."),
    (re.compile(r"\bWebFetch\b"), "Replace legacy WebFetch wording with source-fetch guidance that matches the active Codex environment."),
    (re.compile(r"\ballowed-tools\b"), "Translate legacy tool allow-list frontmatter into Codex permissions or prose workflow boundaries."),
    (re.compile(r"\bmaxTurns\b"), "Review legacy agent runtime budget fields; Codex subagents use TOML fields and model settings."),
    (re.compile(r"\bANTHROPIC_"), "Remove legacy provider environment variables from public harness guidance."),
)

TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "build", "dist", ".eggs"}


@dataclass(frozen=True)
class Finding:
    kind: str
    path: str
    status: str
    message: str
    recommendation: str

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "path": self.path,
            "status": self.status,
            "message": self.message,
            "recommendation": self.recommendation,
        }


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


def audit_path(root: Path) -> dict:
    root = root.resolve()
    findings: list[Finding] = []

    for path, recommendation in LEGACY_PATHS.items():
        target = root / path
        if target.exists():
            findings.append(
                Finding(
                    kind="legacy_path",
                    path=path,
                    status="fail",
                    message="Legacy harness artifact exists.",
                    recommendation=recommendation,
                )
            )

    for path, recommendation in CODEX_PATHS.items():
        target = root / path
        if not target.exists():
            findings.append(
                Finding(
                    kind="missing_codex_path",
                    path=path,
                    status="fail",
                    message="Expected Codex-native artifact is missing.",
                    recommendation=f"Create {path}: {recommendation}",
                )
            )

    for text_path in iter_text_files(root):
        try:
            text = text_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, recommendation in LEGACY_TEXT_PATTERNS:
            if pattern.search(text):
                findings.append(
                    Finding(
                        kind="legacy_text",
                        path=rel(text_path, root),
                        status="warn",
                        message=f"Legacy wording matched {pattern.pattern!r}.",
                        recommendation=recommendation,
                    )
                )

    fail_count = sum(1 for finding in findings if finding.status == "fail")
    warn_count = sum(1 for finding in findings if finding.status == "warn")
    status = "pass" if fail_count == 0 else "needs_migration"
    return {
        "path": root.as_posix(),
        "status": status,
        "failure_count": fail_count,
        "warning_count": warn_count,
        "findings": [finding.to_dict() for finding in findings],
        "next_steps": next_steps(findings),
        "migration_plan": migration_plan(root, findings),
    }


def next_steps(findings: list[Finding]) -> list[str]:
    if not findings:
        return [
            "Run codex-harness doctor.",
            "Run codex-harness validate <generated-harness-path> for generated outputs.",
        ]
    steps = []
    if any(finding.kind == "legacy_path" for finding in findings):
        steps.append("Map each legacy path to the Codex-native artifact listed in the recommendations.")
    if any(finding.kind == "missing_codex_path" for finding in findings):
        steps.append("Create the missing Codex-native files before relying on the harness.")
    if any(finding.kind == "legacy_text" for finding in findings):
        steps.append("Review legacy wording warnings and translate tool/model/config assumptions explicitly.")
    steps.append("After migration, run codex-harness validate <path> and codex-harness doctor.")
    return steps


def migration_plan(root: Path, findings: list[Finding]) -> dict:
    path = root.as_posix()
    quoted_path = shlex.quote(path)
    if not findings:
        return {
            "readiness": "codex-native",
            "commands": [
                f"codex-harness doctor",
                f"codex-harness validate {quoted_path}",
            ],
            "manual_steps": [
                "Review AGENTS.md and .codex/config.toml against the current project before publishing.",
            ],
        }

    legacy_paths = sorted({finding.path for finding in findings if finding.kind == "legacy_path"})
    missing_codex_paths = sorted({finding.path for finding in findings if finding.kind == "missing_codex_path"})
    legacy_text_paths = sorted({finding.path for finding in findings if finding.kind == "legacy_text"})
    blueprint = shlex.quote("/tmp/codex-migration-blueprint")
    report = shlex.quote("/tmp/HARNESS_ADOPTION_PLAN.md")
    copy_script = shlex.quote("/tmp/copy-codex-harness-adds.sh")
    return {
        "readiness": "needs-manual-migration",
        "commands": [
            f"codex-harness migration-audit {quoted_path} --report /tmp/CODEX_MIGRATION_PLAN.md",
            f"codex-harness init {blueprint} --from-project {quoted_path} --project-name 'Codex Migration Blueprint' --force --json",
            f"codex-harness adoption-plan {quoted_path} --blueprint-out {blueprint} --report {report} --copy-script {copy_script} --json",
            copy_script,
            f"codex-harness validate {quoted_path}",
            "codex-harness doctor",
        ],
        "manual_steps": [
            "Move durable project instructions from CLAUDE.md into AGENTS.md, preserving source-specific constraints.",
            "Translate .claude/settings.json into .codex/config.toml instead of copying provider-specific settings verbatim.",
            "Rewrite Claude agents, commands, hooks, and skills into Codex subagents, AGENTS.md routing, explicit validation commands, or .agents/skills.",
            "Review any add-only copy script output before merging conflicts; never overwrite existing project guidance blindly.",
            "Run validation after each manual merge phase and record remaining gaps in Docs/Environment/IMPROVEMENT_LOG.md.",
        ],
        "legacy_paths": legacy_paths,
        "missing_codex_paths": missing_codex_paths,
        "legacy_text_paths": legacy_text_paths,
    }


def build_payload(paths: list[str]) -> dict:
    results = [audit_path(Path(path)) for path in paths]
    return {
        "status": "pass" if all(result["status"] == "pass" for result in results) else "needs_migration",
        "results": results,
    }


def print_text(payload: dict) -> None:
    print(f"Migration audit: {payload['status'].upper()}")
    for result in payload["results"]:
        print(
            f"- {result['path']}: {result['status'].upper()} failures={result['failure_count']} warnings={result['warning_count']}"
        )
        for finding in result["findings"]:
            print(f"  - [{finding['status']}/{finding['kind']}] {finding['path']}: {finding['message']}")
            print(f"    {finding['recommendation']}")
        for step in result["next_steps"]:
            print(f"  next: {step}")
        for command in result["migration_plan"]["commands"]:
            print(f"  command: {command}")


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Codex Migration Plan",
        "",
        f"Status: {payload['status'].upper()}",
        "",
        "This report is an audit and migration plan. It does not rewrite files or prove the migrated harness is ready.",
        "",
    ]
    for result in payload["results"]:
        lines.extend(
            [
                f"## {result['path']}",
                "",
                f"- Status: {result['status'].upper()}",
                f"- Failures: {result['failure_count']}",
                f"- Warnings: {result['warning_count']}",
                f"- Migration readiness: {result['migration_plan']['readiness']}",
                "",
                "### Findings",
                "",
            ]
        )
        if result["findings"]:
            lines.extend(["| Status | Kind | Path | Recommendation |", "|---|---|---|---|"])
            for finding in result["findings"]:
                lines.append(
                    "| {status} | {kind} | `{path}` | {recommendation} |".format(
                        status=finding["status"],
                        kind=finding["kind"],
                        path=finding["path"],
                        recommendation=finding["recommendation"],
                    )
                )
        else:
            lines.append("- No migration findings.")
        lines.extend(["", "### Commands", ""])
        for command in result["migration_plan"]["commands"]:
            lines.append(f"- `{command}`")
        lines.extend(["", "### Manual Steps", ""])
        for step in result["migration_plan"]["manual_steps"]:
            lines.append(f"- {step}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Harness directories to audit for migration readiness")
    parser.add_argument("--report", help="Optional Markdown migration plan report path")
    parser.add_argument("--no-write", action="store_true", help="Do not write --report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args(argv)

    payload = build_payload(args.paths)
    if args.report and not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
