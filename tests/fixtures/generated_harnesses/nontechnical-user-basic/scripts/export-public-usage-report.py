#!/usr/bin/env python3
"""Export a public-safe usage report draft from a copied generated harness."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASK_TRIALS_PATH = ROOT / "Docs/Environment/TASK_TRIALS.md"
GENESIS_PATH = ROOT / "Docs/Environment/GENESIS.md"
REPORT_PATH = ROOT / "Docs/Environment/PUBLIC_USAGE_REPORT.md"
VALID_OUTCOMES = {"success", "partial", "failed", "inconclusive"}
SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(/Users/|/home/|C:\\\\Users\\\\)[^\s]+"),
]


def reject_sensitive(label: str, value: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            raise SystemExit(f"{label} appears to contain sensitive or machine-local data; summarize or redact it first.")


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("### "):
            if current is not None:
                entries.append(current)
            title = line.removeprefix("### ").strip()
            parts = title.split(" - ", 2)
            current = {"title": title}
            if len(parts) == 3:
                current.update({"date": parts[0], "outcome": parts[1].lower(), "task": parts[2]})
            continue
        if current is None or not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        current[key.strip().lower().replace(" ", "_").replace("-", "_")] = value.strip()
    if current is not None:
        entries.append(current)
    return entries


def complete_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    complete = []
    for entry in entries:
        if entry.get("outcome") not in VALID_OUTCOMES:
            continue
        if all(entry.get(field, "").strip() for field in ["task", "evidence", "verification", "privacy_review", "limitations"]):
            complete.append(entry)
    return complete


def latest_success(entries: list[dict[str, str]]) -> dict[str, str] | None:
    successes = [entry for entry in entries if entry.get("outcome") == "success"]
    return successes[-1] if successes else None


def genesis_field(label: str, fallback: str) -> str:
    if not GENESIS_PATH.is_file():
        return fallback
    prefix = f"{label}:"
    for line in GENESIS_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            value = stripped.split(":", 1)[1].strip().rstrip(".")
            return value or fallback
    return fallback


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "generated-codex-harness"


def run_eval(min_successes: int) -> dict:
    completed = subprocess.run(
        [sys.executable, "scripts/run-harness-evals.py", "--min-successes", str(min_successes), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {}
    payload["returncode"] = completed.returncode
    payload["stderr"] = completed.stderr.strip()
    return payload


def bullet_lines(value: str) -> list[str]:
    items = [line.strip(" -*") for line in value.splitlines() if line.strip()]
    if not items:
        items = [value.strip()]
    return [f"- {item}" for item in items if item]


def build_report(args: argparse.Namespace) -> tuple[str, dict]:
    if not TASK_TRIALS_PATH.is_file():
        raise SystemExit("No task trials file found. Record a trial with scripts/record-task-trial.py first.")
    eval_payload = run_eval(args.min_successes)
    if eval_payload.get("status") != "pass":
        issues = eval_payload.get("issues") or ["copied-harness eval did not pass"]
        raise SystemExit("Cannot export public usage report until local eval passes: " + "; ".join(issues))

    entries = complete_entries(parse_entries(TASK_TRIALS_PATH.read_text(encoding="utf-8")))
    entry = latest_success(entries)
    if entry is None:
        raise SystemExit("No complete success task trial found. Record a successful task trial before exporting a public usage report.")

    for field in ["task", "evidence", "verification", "privacy_review", "harness_helped", "limitations"]:
        reject_sensitive(field.replace("_", " "), entry.get(field, ""))

    domain = args.domain or genesis_field("Domain", "unspecified domain")
    harness_label = args.harness_label or genesis_field("Project", "generated Codex harness")
    slug = safe_slug(args.slug or harness_label)
    reject_sensitive("domain", domain)
    reject_sensitive("harness label", harness_label)
    reject_sensitive("slug", slug)

    evidence = bullet_lines(entry["evidence"])
    evidence.append(f"- Copied-harness eval report status: {eval_payload.get('status', 'unknown').upper()}.")
    verification = bullet_lines(entry["verification"])
    verification.append("- `python scripts/run-harness-evals.py --min-successes {}` passed before export.".format(args.min_successes))
    limitations = bullet_lines(entry["limitations"])
    limitations.append("- One copied-harness task trial; not longitudinal proof or broad adoption evidence.")

    lines = [
        "### Pilot or usage-record slug",
        "",
        slug,
        "",
        "### Domain or project type",
        "",
        domain,
        "",
        "### Generated harness profile or label",
        "",
        harness_label,
        "",
        "### Evidence type",
        "",
        "private-summary",
        "",
        "### Source type",
        "",
        args.source_type,
        "",
        "### Generation path",
        "",
        args.generation_path,
        "",
        "### Outcome",
        "",
        entry["outcome"],
        "",
        "### Public-safe task summary",
        "",
        entry["task"],
        "",
        "### Evidence",
        "",
        *evidence,
        "",
        "### Verification performed",
        "",
        *verification,
        "",
        "### Privacy review",
        "",
        entry["privacy_review"],
        "",
        "### Limitations",
        "",
        *limitations,
        "",
        "### Claim boundary",
        "",
        "This report describes one public-safe copied-harness task trial. It does not prove production readiness, compliance, broad adoption, or long-term reliability.",
    ]
    report = "\n".join(lines).rstrip() + "\n"
    reject_sensitive("report", report)
    return report, {
        "status": "pass",
        "task": entry["task"],
        "outcome": entry["outcome"],
        "slug": slug,
        "domain": domain,
        "harness_label": harness_label,
        "eval_status": eval_payload.get("status"),
    }


def output_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=REPORT_PATH.as_posix(), help="Markdown report path")
    parser.add_argument("--slug", help="Public-safe pilot or usage-record slug; defaults to the generated harness label")
    parser.add_argument("--domain", help="Public-safe domain override")
    parser.add_argument("--harness-label", help="Public-safe harness label override")
    parser.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], default="external")
    parser.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        default="installed-quickstart",
    )
    parser.add_argument("--min-successes", type=int, default=1, help="Minimum success task trials required by local eval")
    parser.add_argument("--no-write", action="store_true", help="Print/validate without writing the report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    report, payload = build_report(args)
    out = output_path(args.out)
    if not args.no_write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        payload["path"] = out.relative_to(ROOT).as_posix() if out.is_relative_to(ROOT) else out.as_posix()
    else:
        payload["path"] = None
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        if args.no_write:
            print(report)
        else:
            print(f"Exported public usage report draft to {payload['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
