#!/usr/bin/env python3
"""Prepare a batch of suggested beta-exit pilots from current usage gaps."""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import pilot_board
import prepare_pilot
import usage_gaps
from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE


DEFAULT_TARGET_ROOT = "/tmp/codex-beta-exit-pilots"


def selected_pilots(gaps_payload: dict, max_pilots: int) -> list[dict]:
    pilots = gaps_payload.get("suggested_pilots", [])
    if max_pilots < 0:
        raise SystemExit("--max-pilots must be 0 or greater.")
    if max_pilots == 0:
        return pilots
    return pilots[:max_pilots]


def pilot_target(args: argparse.Namespace, pilot: dict) -> str:
    if args.use_suggested_targets:
        return pilot["target"]
    return (Path(args.target_root).expanduser() / pilot["slug"]).as_posix()


def pilot_output_path(args: argparse.Namespace, pilot: dict, suffix: str) -> str | None:
    if not args.out_dir:
        return None
    return (Path(args.out_dir).expanduser() / f"{pilot['slug']}-{suffix}").as_posix()


def build_prepare_args(args: argparse.Namespace, pilot: dict) -> Namespace:
    return Namespace(
        target=pilot_target(args, pilot),
        brief=pilot["brief"],
        project_name=pilot["project_name"],
        notes=args.notes,
        generated_date=args.generated_date,
        created=args.created,
        generated=args.generated,
        target_label=args.target_label,
        limit=args.limit,
        allow_low_confidence=args.allow_low_confidence,
        force=args.force,
        min_score=args.min_score,
        min_successes=args.min_successes,
        domain=pilot["domain"],
        slug=pilot["slug"],
        title=pilot["title"],
        source_type=pilot["source_type"],
        generation_path=pilot["generation_path"],
        harness_label=pilot["project_name"],
        out=pilot_output_path(args, pilot, "pilot-pack.md"),
        issue_out=pilot_output_path(args, pilot, "usage-issue.md"),
    )


def planned_entry(args: argparse.Namespace, index: int, pilot: dict) -> dict:
    return {
        "selected_index": index,
        "profile": pilot["profile"],
        "domain": pilot["domain"],
        "slug": pilot["slug"],
        "source_type": pilot["source_type"],
        "generation_path": pilot["generation_path"],
        "target": pilot_target(args, pilot),
        "pilot_pack": pilot_output_path(args, pilot, "pilot-pack.md"),
        "issue_draft": pilot_output_path(args, pilot, "usage-issue.md"),
    }


def write_pilot_record(args: argparse.Namespace, index: int, pilot: dict, prepared: dict) -> dict | None:
    if not args.pilot_record_dir:
        return None
    provisional_payload = {
        "generated": args.generated,
        "selected_index": index,
        "selected_pilot": pilot,
        "prepared_pilot": prepared,
        "claim_boundary": (
            "Preparing a pilot batch is not usage proof until reporters complete real task trials "
            "and evidence is converted into checked usage records."
        ),
    }
    record = pilot_board.build_record(provisional_payload, status=args.pilot_status, notes=args.pilot_notes)
    path = pilot_board.default_record_path(Path(args.pilot_record_dir), record["slug"])
    return pilot_board.write_record(path, record, force=args.force)


def build_payload(args: argparse.Namespace) -> dict:
    gaps_payload = usage_gaps.build_payload(
        Path(args.record_dir),
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    pilots = selected_pilots(gaps_payload, args.max_pilots)
    prepared = []
    pilot_records = []
    failures = []

    for index, pilot in enumerate(pilots, start=1):
        plan = planned_entry(args, index, pilot)
        if args.dry_run:
            prepared.append({"status": "planned", **plan})
            continue

        prepared_payload = prepare_pilot.build_payload(build_prepare_args(args, pilot))
        prepared.append({"selected_index": index, "selected_pilot": pilot, "prepared_pilot": prepared_payload})
        if prepared_payload["status"] != "pass":
            failures.append(f"{pilot['slug']}: prepare-pilot status {prepared_payload['status']}")
            continue
        record = write_pilot_record(args, index, pilot, prepared_payload)
        if record:
            pilot_records.append(record)
            if record["status"] != "pass":
                failures.append(f"{pilot['slug']}: pilot record {record.get('error', record['status'])}")

    status = "pass" if gaps_payload["status"] == "pass" and not failures else "fail"
    return {
        "generated": args.generated,
        "status": status,
        "mode": "dry-run" if args.dry_run else "prepare",
        "readiness": gaps_payload["readiness"],
        "target_root": args.target_root,
        "selected_count": len(pilots),
        "usage_gaps": {
            "status": gaps_payload["status"],
            "readiness": gaps_payload["readiness"],
            "gaps": gaps_payload["gaps"],
            "coverage_projection": gaps_payload["coverage_projection"],
        },
        "planned_pilots": [planned_entry(args, index, pilot) for index, pilot in enumerate(pilots, start=1)],
        "prepared": prepared,
        "pilot_records": pilot_records,
        "failures": failures,
        "claim_boundary": (
            "A prepared pilot batch is not usage proof; beta-exit evidence only exists after real task evidence "
            "is converted into valid usage records."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=usage_gaps.DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--target-root", default=DEFAULT_TARGET_ROOT, help="Directory where generated pilot harnesses are prepared")
    parser.add_argument("--use-suggested-targets", action="store_true", help="Use each suggested pilot's target path instead of --target-root")
    parser.add_argument("--out-dir", help="Optional directory for pilot packs and issue drafts")
    parser.add_argument("--max-pilots", type=int, default=0, help="Maximum suggested pilots to prepare; 0 means all")
    parser.add_argument("--notes", default="batch pilot selected from usage evidence gaps")
    parser.add_argument("--min-successes", type=int, default=1, help="Minimum passing success task trials expected for later pilots")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum generated harness validation score")
    parser.add_argument("--target-label", help="Override target label written inside generated creation contexts")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), help="UTC timestamp for batch metadata")
    parser.add_argument("--min-records", type=int, default=usage_gaps.DEFAULT_TARGETS["min_records"], help="Target valid usage records")
    parser.add_argument("--min-external-or-multi-project", type=int, default=usage_gaps.DEFAULT_TARGETS["min_external_or_multi_project"], help="Target external or multi-project records")
    parser.add_argument("--min-domains", type=int, default=usage_gaps.DEFAULT_TARGETS["min_domains"], help="Target distinct domains")
    parser.add_argument("--min-installed-init-brief", type=int, default=usage_gaps.DEFAULT_TARGETS["min_installed_init_brief"], help="Target records generated via installed brief-based generation")
    parser.add_argument("--pilot-record-dir", help="Optional directory where prepared-pilot tracking records are written")
    parser.add_argument("--pilot-status", choices=sorted(pilot_board.ALLOWED_STATUSES), default="prepared", help="Status for optional pilot-board records")
    parser.add_argument("--pilot-notes", default="", help="Optional public-safe note for pilot-board records")
    parser.add_argument("--dry-run", action="store_true", help="Only print the batch plan; do not generate harnesses or write pilot records")
    parser.add_argument("--force", action="store_true", help="Replace generated targets and pilot records when they already exist")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Prepare pilot batch: {payload['status'].upper()} ({payload['mode']})")
        print(f"- selected pilots: {payload['selected_count']}")
        for pilot in payload["planned_pilots"]:
            print(f"- {pilot['slug']}: {pilot['target']}")
        print(f"- boundary: {payload['claim_boundary']}")
        for failure in payload["failures"]:
            print(f"- failure: {failure}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
