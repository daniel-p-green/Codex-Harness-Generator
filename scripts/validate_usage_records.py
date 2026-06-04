#!/usr/bin/env python3
"""Validate checked-in usage-record evidence without modifying files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from record_usage_case import (
    DEFAULT_RECORD_DIR,
    EXTERNAL_OR_MULTI_PROJECT_SOURCE_TYPES,
    NON_SYNTHETIC_EVIDENCE_TYPES,
    UsageRecord,
    safe_slug,
    summarize_records,
    validate_record,
)


REQUIRED_FIELDS = {
    "slug",
    "title",
    "generated",
    "domain",
    "harness_path",
    "task_summary",
    "outcome",
    "evidence_type",
    "source_type",
    "generation_path",
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
        source_type=payload["source_type"],
        generation_path=payload["generation_path"],
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


def validate_record_dir(
    record_dir: Path,
    min_records: int = 0,
    require_non_synthetic: bool = False,
    require_success: bool = False,
    min_external_or_multi_project: int = 0,
    min_domains: int = 0,
    min_installed_init_brief: int = 0,
) -> dict:
    paths = sorted(record_dir.glob("*.json")) if record_dir.exists() else []
    results = [validate_record_file(path) for path in paths]
    valid_records = []
    for path, result in zip(paths, results):
        if result["status"] == "pass":
            valid_records.append(json.loads(path.read_text(encoding="utf-8")))
    summary = summarize_records(valid_records)
    requirement_errors = []
    if summary["total"] < min_records:
        requirement_errors.append(f"requires at least {min_records} usage record(s); found {summary['total']}")
    if require_non_synthetic and summary["non_synthetic"] == 0:
        allowed = ", ".join(sorted(NON_SYNTHETIC_EVIDENCE_TYPES))
        requirement_errors.append(f"requires at least one non-synthetic usage record ({allowed})")
    if require_success and summary["success"] == 0:
        requirement_errors.append("requires at least one successful usage record")
    if summary["external_or_multi_project"] < min_external_or_multi_project:
        allowed = ", ".join(sorted(EXTERNAL_OR_MULTI_PROJECT_SOURCE_TYPES))
        requirement_errors.append(
            "requires at least {required} external or multi-project usage record(s) ({allowed}); found {found}".format(
                required=min_external_or_multi_project,
                allowed=allowed,
                found=summary["external_or_multi_project"],
            )
        )
    if summary["distinct_domains"] < min_domains:
        requirement_errors.append(
            f"requires at least {min_domains} distinct usage domain(s); found {summary['distinct_domains']}"
        )
    if summary["installed_brief_generation"] < min_installed_init_brief:
        requirement_errors.append(
            "requires at least {required} installed brief-based generation usage record(s); found {found}".format(
                required=min_installed_init_brief,
                found=summary["installed_brief_generation"],
            )
        )
    status = "pass" if all(result["status"] == "pass" for result in results) and not requirement_errors else "fail"
    return {
        "status": status,
        "record_dir": record_dir.as_posix(),
        "record_count": len(results),
        "summary": summary,
        "requirement_errors": requirement_errors,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--min-records", type=int, default=0, help="Fail unless at least this many valid records exist")
    parser.add_argument("--require-non-synthetic", action="store_true", help="Fail unless sanitized or private-summary evidence exists")
    parser.add_argument("--require-success", action="store_true", help="Fail unless at least one successful usage record exists")
    parser.add_argument("--min-external-or-multi-project", type=int, default=0, help="Minimum external or multi-project usage records")
    parser.add_argument("--min-domains", type=int, default=0, help="Minimum distinct usage domains")
    parser.add_argument("--min-installed-init-brief", type=int, default=0, help="Minimum usage records generated via installed init --brief or quickstart")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = validate_record_dir(
        Path(args.record_dir),
        min_records=args.min_records,
        require_non_synthetic=args.require_non_synthetic,
        require_success=args.require_success,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Usage records validation: {payload['status'].upper()}")
        print(f"- record_dir: {payload['record_dir']}")
        print(f"- records: {payload['record_count']}")
        summary = payload["summary"]
        print(
            "- summary: total={total} synthetic={synthetic} sanitized={sanitized} private-summary={private_summary} non-synthetic={non_synthetic} success={success} external-or-multi-project={external_or_multi_project} domains={distinct_domains} installed-brief-generation={installed_brief_generation}".format(
                **summary
            )
        )
        for error in payload["requirement_errors"]:
            print(f"- requirement: FAIL - {error}")
        for result in payload["results"]:
            print(f"- {result['path']}: {result['status'].upper()}")
            if result["error"]:
                print(f"  {result['error']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
