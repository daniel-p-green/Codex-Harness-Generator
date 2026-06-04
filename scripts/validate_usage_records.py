#!/usr/bin/env python3
"""Validate checked-in usage-record evidence without modifying files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from record_usage_case import DEFAULT_RECORD_DIR, UsageRecord, safe_slug, validate_record


REQUIRED_FIELDS = {
    "slug",
    "title",
    "generated",
    "domain",
    "harness_path",
    "task_summary",
    "outcome",
    "evidence_type",
    "evidence",
    "verification",
    "privacy_review",
    "limitations",
}


def coerce_record(payload: dict, path: Path) -> UsageRecord:
    missing = sorted(REQUIRED_FIELDS - set(payload))
    if missing:
        raise ValueError(f"{path}: missing required field(s): {', '.join(missing)}")
    unexpected = sorted(set(payload) - REQUIRED_FIELDS)
    if unexpected:
        raise ValueError(f"{path}: unexpected field(s): {', '.join(unexpected)}")
    if not isinstance(payload["evidence"], list) or not all(isinstance(item, str) for item in payload["evidence"]):
        raise ValueError(f"{path}: evidence must be a list of strings")
    if not isinstance(payload["verification"], list) or not all(isinstance(item, str) for item in payload["verification"]):
        raise ValueError(f"{path}: verification must be a list of strings")
    if not isinstance(payload["limitations"], list) or not all(isinstance(item, str) for item in payload["limitations"]):
        raise ValueError(f"{path}: limitations must be a list of strings")
    for key in REQUIRED_FIELDS - {"evidence", "verification", "limitations"}:
        if not isinstance(payload[key], str):
            raise ValueError(f"{path}: {key} must be a string")
    slug = safe_slug(payload["slug"])
    if slug != payload["slug"]:
        raise ValueError(f"{path}: slug must already be normalized as {slug!r}")
    if path.stem != slug:
        raise ValueError(f"{path}: filename stem must match slug {slug!r}")
    return UsageRecord(
        slug=payload["slug"],
        title=payload["title"],
        generated=payload["generated"],
        domain=payload["domain"],
        harness_path=payload["harness_path"],
        task_summary=payload["task_summary"],
        outcome=payload["outcome"],
        evidence_type=payload["evidence_type"],
        evidence=tuple(payload["evidence"]),
        verification=tuple(payload["verification"]),
        privacy_review=payload["privacy_review"],
        limitations=tuple(payload["limitations"]),
    )


def validate_record_file(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: record JSON must be an object")
        record = coerce_record(payload, path)
        validate_record(record)
    except SystemExit as exc:
        return {"path": path.as_posix(), "status": "fail", "error": str(exc)}
    except Exception as exc:
        return {"path": path.as_posix(), "status": "fail", "error": str(exc)}
    return {"path": path.as_posix(), "status": "pass", "error": None}


def validate_record_dir(record_dir: Path) -> dict:
    paths = sorted(record_dir.glob("*.json")) if record_dir.exists() else []
    results = [validate_record_file(path) for path in paths]
    status = "pass" if all(result["status"] == "pass" for result in results) else "fail"
    return {
        "status": status,
        "record_dir": record_dir.as_posix(),
        "record_count": len(results),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = validate_record_dir(Path(args.record_dir))
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Usage records validation: {payload['status'].upper()}")
        print(f"- record_dir: {payload['record_dir']}")
        print(f"- records: {payload['record_count']}")
        for result in payload["results"]:
            print(f"- {result['path']}: {result['status'].upper()}")
            if result["error"]:
                print(f"  {result['error']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
