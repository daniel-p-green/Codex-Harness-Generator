#!/usr/bin/env python3
"""Summarize prepared external pilots before they become usage proof."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD_DIR = REPO_ROOT / "Docs" / "Environment" / "pilot-records"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_BOARD.md"
ALLOWED_STATUSES = {"prepared", "invited", "completed", "converted", "dropped"}
INSTALLED_BRIEF_GENERATION_PATHS = {
    "installed-init-brief",
    "installed-quickstart",
}


def default_record_path(record_dir: Path, slug: str) -> Path:
    return record_dir / f"{slug}.json"


def build_record(payload: dict, status: str = "prepared", notes: str = "") -> dict:
    selected = payload["selected_pilot"]
    prepared = payload["prepared_pilot"]
    pilot_pack = prepared.get("pilot_pack") or {}
    return {
        "slug": selected["slug"],
        "title": selected["title"],
        "generated": payload["generated"],
        "status": status,
        "domain": selected["domain"],
        "profile": selected["profile"],
        "source_type": selected["source_type"],
        "generation_path": selected["generation_path"],
        "target": prepared["target"],
        "harness_label": pilot_pack.get("harness_label") or selected["project_name"],
        "pilot_pack": pilot_pack.get("pack", ""),
        "issue_draft": pilot_pack.get("issue_draft", ""),
        "selected_index": payload["selected_index"],
        "notes": notes,
        "usage_record": "",
        "claim_boundary": payload["claim_boundary"],
    }


def write_record(path: Path, record: dict, force: bool = False) -> dict:
    if path.exists() and not force:
        return {
            "status": "fail",
            "path": path.as_posix(),
            "error": "record already exists; pass --force to replace it",
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "pass", "path": path.as_posix()}


def validate_record(record: dict, path: Path) -> list[str]:
    errors = []
    required_fields = [
        "slug",
        "title",
        "generated",
        "status",
        "domain",
        "profile",
        "source_type",
        "generation_path",
        "target",
        "harness_label",
        "pilot_pack",
        "claim_boundary",
    ]
    for field in required_fields:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{path.name}: missing non-empty {field}")
    if record.get("status") not in ALLOWED_STATUSES:
        errors.append(f"{path.name}: unsupported status {record.get('status')!r}")
    if record.get("status") == "converted" and not record.get("usage_record"):
        errors.append(f"{path.name}: converted pilot must include usage_record")
    if "proof" not in str(record.get("claim_boundary", "")).casefold():
        errors.append(f"{path.name}: claim_boundary must say the pilot is not usage proof")
    return errors


def load_records(record_dir: Path) -> tuple[list[dict], list[str]]:
    records = []
    errors = []
    if not record_dir.exists():
        return records, errors
    for path in sorted(record_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON: {exc}")
            continue
        record["_path"] = path.as_posix()
        errors.extend(validate_record(record, path))
        records.append(record)
    return records, errors


def summarize(records: list[dict]) -> dict:
    status_counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for record in records:
        status = record.get("status")
        if status in status_counts:
            status_counts[status] += 1
    domains = sorted({record.get("domain", "").strip() for record in records if record.get("domain", "").strip()})
    return {
        "total": len(records),
        "statuses": status_counts,
        "pending": status_counts["prepared"] + status_counts["invited"],
        "completed_not_converted": status_counts["completed"],
        "external_or_multi_project": sum(
            1 for record in records if record.get("source_type") in {"external", "multi-project"}
        ),
        "installed_brief_generation": sum(
            1 for record in records if record.get("generation_path") in INSTALLED_BRIEF_GENERATION_PATHS
        ),
        "distinct_domains": len(domains),
        "domains": domains,
    }


def build_payload(record_dir: Path) -> dict:
    records, errors = load_records(record_dir)
    summary = summarize(records)
    status = "pass" if not errors else "fail"
    if summary["total"] == 0:
        readiness = "no-pilots-prepared"
    elif summary["completed_not_converted"]:
        readiness = "completed-pilots-need-usage-records"
    elif summary["pending"]:
        readiness = "pilot-funnel-active"
    else:
        readiness = "pilot-funnel-clear"
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "readiness": readiness,
        "record_dir": record_dir.as_posix(),
        "summary": summary,
        "records": records,
        "errors": errors,
        "claim_boundary": "Pilot-board records track outreach and completion state only; they are not usage proof until converted into validated usage records.",
    }


def write_report(path: Path, payload: dict) -> None:
    summary = payload["summary"]
    lines = [
        "# Pilot Board",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Total pilot records: {summary['total']}",
        f"- Pending outreach or reporter work: {summary['pending']}",
        f"- Completed but not converted: {summary['completed_not_converted']}",
        f"- External or multi-project pilots: {summary['external_or_multi_project']}",
        f"- Installed brief-based generation pilots: {summary['installed_brief_generation']}",
        f"- Distinct domains: {summary['distinct_domains']}",
        "",
        "## Status Counts",
        "",
    ]
    lines.extend(f"- {status}: {count}" for status, count in summary["statuses"].items())
    lines.extend(["", "## Pilot Records", ""])
    if payload["records"]:
        lines.extend(["| Pilot | Status | Domain | Source | Generation | Usage record |", "|---|---|---|---|---|---|"])
        for record in payload["records"]:
            usage_record = record.get("usage_record") or "not converted"
            lines.append(
                "| `{slug}` | {status} | {domain} | `{source_type}` | `{generation_path}` | {usage_record} |".format(
                    slug=record["slug"],
                    status=record["status"],
                    domain=record["domain"],
                    source_type=record["source_type"],
                    generation_path=record["generation_path"],
                    usage_record=usage_record,
                )
            )
    else:
        lines.append("- none")
    if payload["errors"]:
        lines.extend(["", "## Validation Errors", ""])
        lines.extend(f"- {error}" for error in payload["errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown board")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(Path(args.record_dir))
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot board: {payload['status'].upper()}")
        print(f"- readiness: {payload['readiness']}")
        print(f"- records: {payload['summary']['total']}")
        print(f"- pending: {payload['summary']['pending']}")
        print(f"- completed_not_converted: {payload['summary']['completed_not_converted']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
