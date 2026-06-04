#!/usr/bin/env python3
"""Summarize prepared external pilots before they become usage proof."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from validate_usage_records import DEFAULT_RECORD_DIR as DEFAULT_USAGE_RECORD_DIR
from validate_usage_records import validate_record_file


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD_DIR = REPO_ROOT / "Docs" / "Environment" / "pilot-records"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_BOARD.md"
ALLOWED_STATUSES = {"prepared", "invited", "completed", "converted", "dropped"}
CONVERTIBLE_STATUSES = {"prepared", "invited", "completed"}
INSTALLED_BRIEF_GENERATION_PATHS = {
    "installed-init-brief",
    "installed-quickstart",
}


def default_record_path(record_dir: Path, slug: str) -> Path:
    return record_dir / f"{slug}.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def unique_paths(paths: list[Path]) -> list[Path]:
    seen = set()
    unique = []
    for path in paths:
        key = path.as_posix()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def usage_record_candidates(usage_record_dir: Path, value: str) -> list[Path]:
    if not value.strip():
        return []
    raw = Path(value)
    if raw.is_absolute():
        return [raw]
    if raw.suffix == ".json" or len(raw.parts) > 1:
        return unique_paths([REPO_ROOT / raw, usage_record_dir / raw.name])
    return unique_paths([usage_record_dir / f"{value}.json", usage_record_dir / value])


def resolve_usage_record_path(usage_record_dir: Path, value: str) -> Path | None:
    for candidate in usage_record_candidates(usage_record_dir, value):
        if candidate.exists():
            return candidate
    return None


def validate_converted_usage_record(record: dict, path: Path, usage_record_dir: Path) -> tuple[list[str], str]:
    if record.get("status") != "converted":
        return [], ""
    usage_record = str(record.get("usage_record", "")).strip()
    resolved = resolve_usage_record_path(usage_record_dir, usage_record)
    if not resolved:
        return [f"{path.name}: converted usage_record not found: {usage_record}"], ""

    validation = validate_record_file(resolved)
    if validation["status"] != "pass":
        return [f"{path.name}: converted usage_record is invalid: {validation['error']}"], resolved.as_posix()

    payload = json.loads(resolved.read_text(encoding="utf-8"))
    errors = []
    for field in ("domain", "source_type", "generation_path"):
        pilot_value = str(record.get(field, "")).strip().casefold()
        usage_value = str(payload.get(field, "")).strip().casefold()
        if pilot_value != usage_value:
            errors.append(
                f"{path.name}: converted usage_record {field} mismatch: pilot={record.get(field)!r} usage={payload.get(field)!r}"
            )
    return errors, resolved.as_posix()


def validate_pre_conversion(
    record_dir: Path,
    slug: str,
    domain: str,
    source_type: str,
    generation_path: str,
) -> dict:
    path = default_record_path(record_dir, slug)
    record = read_record(path)
    errors = validate_record(record, path)
    if record.get("status") not in CONVERTIBLE_STATUSES:
        errors.append(f"{path.name}: pilot status must be prepared, invited, or completed before conversion")
    for field, usage_value in (
        ("domain", domain),
        ("source_type", source_type),
        ("generation_path", generation_path),
    ):
        pilot_value = str(record.get(field, "")).strip().casefold()
        if pilot_value != usage_value.strip().casefold():
            errors.append(
                f"{path.name}: pilot {field} mismatch before write: pilot={record.get(field)!r} usage={usage_value!r}"
            )
    if errors:
        raise SystemExit("Pilot conversion validation failed: " + "; ".join(errors))
    return record


def read_record(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Pilot record does not exist: {path.as_posix()}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Pilot record is invalid JSON: {path.as_posix()}: {exc}") from exc


def update_record(record: dict, status: str, notes: str = "", usage_record: str = "", updated: str | None = None) -> dict:
    if status not in ALLOWED_STATUSES:
        raise SystemExit(f"Unsupported pilot status: {status}")
    if status == "converted" and not usage_record and not record.get("usage_record"):
        raise SystemExit("Converted pilots must include --usage-record.")
    previous_status = record.get("status", "unknown")
    timestamp = updated or utc_now()
    history = record.get("status_history", [])
    if not isinstance(history, list):
        history = []
    history.append(
        {
            "at": timestamp,
            "from": previous_status,
            "to": status,
            "notes": notes,
            "usage_record": usage_record or record.get("usage_record", ""),
        }
    )
    record["status"] = status
    record["updated"] = timestamp
    if notes:
        record["notes"] = notes
    if usage_record:
        record["usage_record"] = usage_record
    record["status_history"] = history
    return record


def update_record_file(
    record_dir: Path,
    slug: str,
    status: str,
    notes: str = "",
    usage_record: str = "",
    updated: str | None = None,
    usage_record_dir: Path = DEFAULT_USAGE_RECORD_DIR,
) -> dict:
    path = default_record_path(record_dir, slug)
    record = update_record(read_record(path), status, notes=notes, usage_record=usage_record, updated=updated)
    errors = validate_record(record, path)
    conversion_errors, usage_record_path = validate_converted_usage_record(record, path, usage_record_dir)
    errors.extend(conversion_errors)
    if errors:
        raise SystemExit("Updated pilot record is invalid: " + "; ".join(errors))
    if usage_record_path:
        record["validated_usage_record"] = usage_record_path
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "pass", "path": path.as_posix(), "record": record}


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


def load_records(record_dir: Path, usage_record_dir: Path = DEFAULT_USAGE_RECORD_DIR) -> tuple[list[dict], list[str]]:
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
        conversion_errors, usage_record_path = validate_converted_usage_record(record, path, usage_record_dir)
        errors.extend(conversion_errors)
        if usage_record_path:
            record["_validated_usage_record"] = usage_record_path
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
        "converted_validated": sum(1 for record in records if record.get("status") == "converted" and record.get("_validated_usage_record")),
        "external_or_multi_project": sum(
            1 for record in records if record.get("source_type") in {"external", "multi-project"}
        ),
        "installed_brief_generation": sum(
            1 for record in records if record.get("generation_path") in INSTALLED_BRIEF_GENERATION_PATHS
        ),
        "distinct_domains": len(domains),
        "domains": domains,
    }


def build_payload(record_dir: Path, usage_record_dir: Path = DEFAULT_USAGE_RECORD_DIR) -> dict:
    records, errors = load_records(record_dir, usage_record_dir=usage_record_dir)
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
        "generated": utc_now(),
        "status": status,
        "readiness": readiness,
        "record_dir": record_dir.as_posix(),
        "usage_record_dir": usage_record_dir.as_posix(),
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
        f"- Converted with validated usage records: {summary['converted_validated']}",
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
    parser.add_argument("--usage-record-dir", default=DEFAULT_USAGE_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--update", help="Pilot slug to update before writing the board")
    parser.add_argument("--status", choices=sorted(ALLOWED_STATUSES), help="New status for --update")
    parser.add_argument("--notes", default="", help="Public-safe note for --update")
    parser.add_argument("--usage-record", default="", help="Usage record slug or path required when --status converted")
    parser.add_argument("--updated", help="UTC timestamp override for --update")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown board")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    update_payload = None
    record_dir = Path(args.record_dir)
    usage_record_dir = Path(args.usage_record_dir)
    if args.update:
        if not args.status:
            raise SystemExit("--status is required with --update.")
        update_payload = update_record_file(
            record_dir,
            args.update,
            args.status,
            notes=args.notes,
            usage_record=args.usage_record,
            updated=args.updated,
            usage_record_dir=usage_record_dir,
        )

    payload = build_payload(record_dir, usage_record_dir=usage_record_dir)
    if update_payload:
        payload["update"] = update_payload
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
        if update_payload:
            print(f"- updated: {update_payload['path']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
