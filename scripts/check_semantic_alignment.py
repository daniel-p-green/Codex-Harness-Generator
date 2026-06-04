#!/usr/bin/env python3
"""Check key local Codex guidance against official OpenAI docs.

This is a live maintainer drift check, not an offline CI gate. It verifies that
official docs still contain the core concepts this repo depends on and that the
repo's public guidance still mentions those concepts in the expected artifacts.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from check_source_freshness import assert_official_url


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = REPO_ROOT / "Docs" / "Environment" / "SEMANTIC_ALIGNMENT.json"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "SEMANTIC_ALIGNMENT.md"


@dataclass(frozen=True)
class ConceptCheck:
    name: str
    url: str
    official_terms: tuple[str, ...]
    local_terms: tuple[str, ...]
    local_paths: tuple[str, ...]


@dataclass(frozen=True)
class FetchedDoc:
    url: str
    status: str
    text: str
    http_status: int | None
    error: str | None = None


CONCEPT_CHECKS = [
    ConceptCheck(
        name="AGENTS.md instruction loading",
        url="https://developers.openai.com/codex/guides/agents-md",
        official_terms=("AGENTS.md", "AGENTS.override.md", "project_doc_max_bytes", "project_doc_fallback_filenames", "32 KiB"),
        local_terms=("AGENTS.md", "AGENTS.override.md", "project_doc_max_bytes", "project_doc_fallback_filenames", "32 KiB"),
        local_paths=("Docs/AgentGuidelines/Topics/01-rules.md", "Docs/Templates/Core/agents-md.md", "README.md"),
    ),
    ConceptCheck(
        name="Config permission schema",
        url="https://developers.openai.com/codex/permissions",
        official_terms=("default_permissions", "permissions.<name>.extends", ":workspace_roots", "glob_scan_max_depth", "read", "write", "deny"),
        local_terms=("default_permissions", "extends", ":workspace_roots", "glob_scan_max_depth", "read", "write", "deny"),
        local_paths=("Docs/AgentGuidelines/Topics/11-permissions.md", "Docs/Templates/Core/codex-config-toml.md", "scripts/eval_generated_harness.py"),
    ),
    ConceptCheck(
        name="Subagent schema",
        url="https://developers.openai.com/codex/subagents",
        official_terms=("name", "description", "developer_instructions", "model_reasoning_effort", "sandbox_mode", "skills.config"),
        local_terms=("name", "description", "developer_instructions", "model_reasoning_effort", "sandbox_mode", "skills.config"),
        local_paths=("Docs/AgentGuidelines/Topics/02-agents.md", "Docs/Templates/Agents/reviewer.md", "scripts/eval_generated_harness.py"),
    ),
    ConceptCheck(
        name="Skill schema",
        url="https://developers.openai.com/codex/skills",
        official_terms=("SKILL.md", "description", "skills.config", "enabled"),
        local_terms=("SKILL.md", "description", "Use when", "skills.config", "enabled"),
        local_paths=("Docs/AgentGuidelines/Topics/03-skills.md", "Docs/Templates/Skills/health-check.md", "scripts/eval_generated_harness.py"),
    ),
    ConceptCheck(
        name="Config model controls",
        url="https://developers.openai.com/codex/config-reference",
        official_terms=("model_reasoning_effort", "model_verbosity", "approval_policy", "default_permissions"),
        local_terms=("model_reasoning_effort", "model_verbosity", "approval_policy", "default_permissions"),
        local_paths=("Docs/AgentGuidelines/Topics/13-gpt-5-5-specifics.md", "Docs/Templates/Core/codex-config-toml.md", "scripts/generate_minimal_harness.py"),
    ),
]


def normalize_text(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text)


def fetch_doc(url: str, timeout: int) -> FetchedDoc:
    assert_official_url(url)
    request = urllib.request.Request(url, headers={"User-Agent": "Codex-Harness-Generator-semantic-check/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return FetchedDoc(url=url, status="pass", text=normalize_text(raw), http_status=response.getcode())
    except urllib.error.HTTPError as exc:
        return FetchedDoc(url=url, status="fail", text="", http_status=exc.code, error=str(exc))
    except Exception as exc:
        return FetchedDoc(url=url, status="fail", text="", http_status=None, error=str(exc))


def contains_term(text: str, term: str) -> bool:
    return term.casefold() in text.casefold()


def read_local_text(paths: tuple[str, ...], root: Path = REPO_ROOT) -> tuple[str, list[str]]:
    chunks = []
    missing = []
    for raw_path in paths:
        path = root / raw_path
        if not path.is_file():
            missing.append(raw_path)
            continue
        chunks.append(path.read_text(encoding="utf-8"))
    return "\n".join(chunks), missing


def evaluate_checks(
    checks: list[ConceptCheck],
    timeout: int,
    fetcher=fetch_doc,
    root: Path = REPO_ROOT,
) -> dict:
    results = []
    for check in checks:
        fetched = fetcher(check.url, timeout)
        official_missing = []
        if fetched.status == "pass":
            official_missing = [
                term for term in check.official_terms if not contains_term(fetched.text, term)
            ]

        local_text, local_missing_paths = read_local_text(check.local_paths, root=root)
        local_missing_terms = [
            term for term in check.local_terms if not contains_term(local_text, term)
        ]
        status = "pass"
        if fetched.status != "pass" or official_missing or local_missing_paths or local_missing_terms:
            status = "fail"
        results.append(
            {
                "name": check.name,
                "status": status,
                "url": check.url,
                "http_status": fetched.http_status,
                "error": fetched.error,
                "official_missing_terms": official_missing,
                "local_missing_paths": local_missing_paths,
                "local_missing_terms": local_missing_terms,
                "local_paths": list(check.local_paths),
            }
        )
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "checks": results,
    }


def write_report(report_path: Path, payload: dict) -> None:
    lines = [
        "# Semantic Alignment",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        "",
        "This live maintainer check compares core Codex concepts in local guidance",
        "against the official OpenAI documentation pages this generator relies on.",
        "It is a drift signal, not a substitute for human source review.",
        "",
        "| Concept | Status | Source | Missing official terms | Missing local terms |",
        "|---|---|---|---|---|",
    ]
    for check in payload["checks"]:
        lines.append(
            "| {name} | {status} | {url} | {official} | {local} |".format(
                name=check["name"],
                status=check["status"].upper(),
                url=check["url"],
                official=", ".join(check["official_missing_terms"]) or "",
                local=", ".join(check["local_missing_terms"]) or "",
            )
        )
    failures = [check for check in payload["checks"] if check["status"] != "pass"]
    if failures:
        lines.extend(["", "## Review Needed", ""])
        for check in failures:
            lines.append(f"- {check['name']}: {check['error'] or 'semantic mismatch'}")
            if check["local_missing_paths"]:
                lines.append(f"  - Missing local paths: {', '.join(check['local_missing_paths'])}")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- Checks only official `developers.openai.com` pages.",
            "- Checks a small set of concepts the generator depends on: AGENTS.md,",
            "  config permissions, subagents, skills, and model/control settings.",
            "- A pass means the named concepts still appear in both official docs and",
            "  local guidance; it does not prove exact semantic equivalence.",
        ]
    )
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=15, help="Timeout per official doc in seconds")
    parser.add_argument("--json-output", default=DEFAULT_JSON.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write JSON/report files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = evaluate_checks(CONCEPT_CHECKS, timeout=args.timeout)
    if not args.no_write:
        json_path = Path(args.json_output)
        report_path = Path(args.report)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        write_report(report_path, payload)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Semantic alignment: {payload['status'].upper()}")
        for check in payload["checks"]:
            print(f"- {check['name']}: {check['status'].upper()}")
            if check["official_missing_terms"]:
                print(f"  missing official terms: {', '.join(check['official_missing_terms'])}")
            if check["local_missing_terms"]:
                print(f"  missing local terms: {', '.join(check['local_missing_terms'])}")
            if check["local_missing_paths"]:
                print(f"  missing local paths: {', '.join(check['local_missing_paths'])}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
