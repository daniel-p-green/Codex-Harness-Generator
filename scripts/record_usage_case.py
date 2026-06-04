#!/usr/bin/env python3
"""Record sanitized real-world generated-harness usage evidence."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD_DIR = REPO_ROOT / "Docs" / "Environment" / "usage-records"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_RECORDS.md"
ALLOWED_EVIDENCE_TYPES = {"synthetic", "sanitized", "private-summary"}
NON_SYNTHETIC_EVIDENCE_TYPES = {"sanitized", "private-summary"}
ALLOWED_OUTCOMES = {"success", "partial", "failed", "inconclusive"}
GENERATED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

SENSITIVE_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_-]{12,}"), "possible OpenAI API key"),
    (re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}"), "possible credential"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key material"),
    (re.compile(r"/Users/[^/\s]+/"), "local macOS user path"),
    (re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"), "email address"),
]


@dataclass(frozen=True)
class UsageRecord:
    slug: str
    title: str
    generated: str
    domain: str
    harness_path: str
    task_summary: str
    outcome: str
    evidence_type: str
    evidence: tuple[str, ...]
    verification: tuple[str, ...]
    privacy_review: str
    limitations: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "generated": self.generated,
            "domain": self.domain,
            "harness_path": self.harness_path,
            "task_summary": self.task_summary,
            "outcome": self.outcome,
            "evidence_type": self.evidence_type,
            "evidence": list(self.evidence),
            "verification": list(self.verification),
            "privacy_review": self.privacy_review,
            "limitations": list(self.limitations),
        }


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "-", value.lower()).strip("-")
    if not slug:
        raise SystemExit("Slug must contain at least one alphanumeric character.")
    return slug


def find_sensitive_text(text: str) -> list[str]:
    findings = []
    for pattern, label in SENSITIVE_PATTERNS:
        if pattern.search(text):
            findings.append(label)
    return sorted(set(findings))


def validate_record(record: UsageRecord) -> None:
    required_text = {
        "title": record.title,
        "generated": record.generated,
        "domain": record.domain,
        "harness_path": record.harness_path,
        "task_summary": record.task_summary,
        "privacy_review": record.privacy_review,
    }
    empty = [key for key, value in required_text.items() if not value.strip()]
    if empty:
        raise SystemExit("Required field(s) must not be empty: " + ", ".join(sorted(empty)))
    if not GENERATED_RE.match(record.generated):
        raise SystemExit("generated must use UTC timestamp format YYYY-MM-DDTHH:MM:SSZ.")
    if record.evidence_type not in ALLOWED_EVIDENCE_TYPES:
        raise SystemExit(f"Unsupported evidence_type: {record.evidence_type}")
    if record.outcome not in ALLOWED_OUTCOMES:
        raise SystemExit(f"Unsupported outcome: {record.outcome}")
    if not record.evidence or any(not item.strip() for item in record.evidence):
        raise SystemExit("At least one evidence item is required.")
    if not record.verification or any(not item.strip() for item in record.verification):
        raise SystemExit("At least one verification item is required.")
    if any(not item.strip() for item in record.limitations):
        raise SystemExit("Limitations must not include empty items.")
    if record.evidence_type in NON_SYNTHETIC_EVIDENCE_TYPES:
        if len(record.evidence) < 2:
            raise SystemExit("Non-synthetic usage records require at least two evidence items.")
        if len(record.verification) < 2:
            raise SystemExit("Non-synthetic usage records require at least two verification items.")
        if not record.limitations:
            raise SystemExit("Non-synthetic usage records require at least one limitation.")
    scan_text = json.dumps(record.to_dict(), sort_keys=True)
    findings = find_sensitive_text(scan_text)
    if findings:
        raise SystemExit("Refusing to write usage record with sensitive text: " + ", ".join(findings))


def record_from_args(args: argparse.Namespace) -> UsageRecord:
    return UsageRecord(
        slug=safe_slug(args.slug),
        title=args.title,
        generated=args.generated,
        domain=args.domain,
        harness_path=args.harness_path,
        task_summary=args.task_summary,
        outcome=args.outcome,
        evidence_type=args.evidence_type,
        evidence=tuple(args.evidence),
        verification=tuple(args.verification),
        privacy_review=args.privacy_review,
        limitations=tuple(args.limitation),
    )


def record_path(record_dir: Path, slug: str) -> Path:
    return record_dir / f"{slug}.json"


def write_record(record_dir: Path, record: UsageRecord, force: bool = False) -> Path:
    validate_record(record)
    record_dir.mkdir(parents=True, exist_ok=True)
    path = record_path(record_dir, record.slug)
    if path.exists() and not force:
        raise SystemExit(f"Usage record already exists. Re-run with --force to replace it: {path}")
    path.write_text(json.dumps(record.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def load_records(record_dir: Path) -> list[dict]:
    if not record_dir.exists():
        return []
    records = []
    for path in sorted(record_dir.glob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def summarize_records(records: list[dict]) -> dict:
    by_type = {evidence_type: 0 for evidence_type in sorted(ALLOWED_EVIDENCE_TYPES)}
    by_outcome = {outcome: 0 for outcome in sorted(ALLOWED_OUTCOMES)}
    for record in records:
        by_type[record["evidence_type"]] = by_type.get(record["evidence_type"], 0) + 1
        by_outcome[record["outcome"]] = by_outcome.get(record["outcome"], 0) + 1
    non_synthetic = sum(by_type.get(evidence_type, 0) for evidence_type in NON_SYNTHETIC_EVIDENCE_TYPES)
    return {
        "total": len(records),
        "synthetic": by_type.get("synthetic", 0),
        "sanitized": by_type.get("sanitized", 0),
        "private_summary": by_type.get("private-summary", 0),
        "non_synthetic": non_synthetic,
        "success": by_outcome.get("success", 0),
        "partial": by_outcome.get("partial", 0),
        "failed": by_outcome.get("failed", 0),
        "inconclusive": by_outcome.get("inconclusive", 0),
    }


def write_report(report_path: Path, records: list[dict]) -> None:
    summary = summarize_records(records)
    lines = [
        "# Usage Records",
        "",
        "This report indexes sanitized generated-harness usage evidence recorded by",
        "`python scripts/record_usage_case.py`. It is intentionally conservative:",
        "records may summarize private work, but public artifacts must not include",
        "secrets, personal data, proprietary source, or local machine paths.",
        "",
        "## Summary",
        "",
        "| Total | Synthetic | Sanitized | Private Summary | Non-Synthetic | Success | Partial | Failed | Inconclusive |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        "| {total} | {synthetic} | {sanitized} | {private_summary} | {non_synthetic} | {success} | {partial} | {failed} | {inconclusive} |".format(
            **summary
        ),
        "",
        "Product-proof status: {status}".format(
            status=(
                "non-synthetic usage evidence present"
                if summary["non_synthetic"]
                else "no non-synthetic usage records yet"
            )
        ),
        "",
        "## Records",
        "",
        "| Generated | Slug | Domain | Outcome | Evidence Type | Verification Count |",
        "|---|---|---|---|---|---:|",
    ]
    for record in sorted(records, key=lambda item: item["generated"], reverse=True):
        lines.append(
            "| {generated} | `{slug}` | {domain} | {outcome} | {evidence_type} | {verification_count} |".format(
                generated=record["generated"],
                slug=record["slug"],
                domain=record["domain"],
                outcome=record["outcome"],
                evidence_type=record["evidence_type"],
                verification_count=len(record.get("verification", [])),
            )
        )
    if not records:
        lines.append("|  |  |  |  |  | 0 |")
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- `synthetic`: public-safe generated or fake inputs.",
            "- `sanitized`: real workflow evidence stripped of secrets, personal data,",
            "  proprietary source, and local machine paths.",
            "- `private-summary`: public-safe summary of private work where raw evidence",
            "  cannot be published.",
            "- A record is evidence of one harness use, not proof that every generated",
            "  harness will perform well.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="Stable record slug")
    parser.add_argument("--title", required=True, help="Short record title")
    parser.add_argument("--domain", required=True, help="Usage domain")
    parser.add_argument("--harness-path", required=True, help="Generated harness path or public label")
    parser.add_argument("--task-summary", required=True, help="Public-safe task summary")
    parser.add_argument("--outcome", choices=sorted(ALLOWED_OUTCOMES), required=True)
    parser.add_argument("--evidence-type", choices=sorted(ALLOWED_EVIDENCE_TYPES), required=True)
    parser.add_argument("--evidence", action="append", required=True, help="Public-safe evidence item; repeatable")
    parser.add_argument("--verification", action="append", required=True, help="Verification item; repeatable")
    parser.add_argument("--privacy-review", required=True, help="Public-safe privacy review note")
    parser.add_argument("--limitation", action="append", default=[], help="Known limitation; repeatable")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    parser.add_argument("--json", action="store_true", help="Emit the record JSON")
    args = parser.parse_args()

    record = record_from_args(args)
    path = write_record(Path(args.record_dir), record, force=args.force)
    records = load_records(Path(args.record_dir))
    write_report(Path(args.report), records)

    if args.json:
        print(json.dumps({**record.to_dict(), "path": path.as_posix(), "report": args.report}, indent=2))
    else:
        print(f"Usage record: {record.outcome.upper()}")
        print(f"- record: {path}")
        print(f"- report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
