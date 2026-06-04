#!/usr/bin/env python3
"""Prepare the next external pilot from current usage-evidence gaps."""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import prepare_pilot
import pilot_board
import usage_gaps
from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE


def select_pilot(gaps_payload: dict, index: int) -> dict:
    pilots = gaps_payload.get("suggested_pilots", [])
    if not pilots:
        raise SystemExit("No suggested pilot targets remain; beta-exit usage gaps are already satisfied.")
    if index < 1 or index > len(pilots):
        raise SystemExit(f"--index must be between 1 and {len(pilots)}.")
    return pilots[index - 1]


def build_prepare_args(args: argparse.Namespace, pilot: dict) -> Namespace:
    target = args.target or pilot["target"]
    return Namespace(
        target=target,
        brief=args.brief or pilot["brief"],
        project_name=args.project_name or pilot["project_name"],
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
        domain=args.domain or pilot["domain"],
        slug=args.slug or pilot["slug"],
        title=args.title or pilot["title"],
        source_type=args.source_type or pilot["source_type"],
        generation_path=args.generation_path or pilot["generation_path"],
        harness_label=args.harness_label or pilot["project_name"],
        out=args.out,
        issue_out=args.issue_out,
    )


def build_payload(args: argparse.Namespace) -> dict:
    gaps_payload = usage_gaps.build_payload(
        Path(args.record_dir),
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    pilot = select_pilot(gaps_payload, args.index)
    prepare_args = build_prepare_args(args, pilot)
    prepared = prepare_pilot.build_payload(prepare_args)
    pilot_record = None
    if prepared["status"] == "pass" and (args.pilot_record_out or args.pilot_record_dir):
        provisional_payload = {
            "generated": args.generated,
            "selected_index": args.index,
            "selected_pilot": pilot,
            "prepared_pilot": prepared,
            "claim_boundary": "Preparing the next pilot is not usage proof until the reporter completes a real task trial and the evidence is converted into a checked usage record.",
        }
        record = pilot_board.build_record(
            provisional_payload,
            status=args.pilot_status,
            notes=args.pilot_notes,
        )
        record_path = (
            Path(args.pilot_record_out)
            if args.pilot_record_out
            else pilot_board.default_record_path(Path(args.pilot_record_dir), record["slug"])
        )
        pilot_record = pilot_board.write_record(record_path, record, force=args.force)

    status = "pass" if gaps_payload["status"] == "pass" and prepared["status"] == "pass" else "fail"
    if pilot_record and pilot_record["status"] != "pass":
        status = "fail"
    return {
        "generated": args.generated,
        "status": status,
        "selected_index": args.index,
        "selected_pilot": pilot,
        "usage_gaps": {
            "status": gaps_payload["status"],
            "readiness": gaps_payload["readiness"],
            "gaps": gaps_payload["gaps"],
            "summary": gaps_payload["summary"],
        },
        "prepared_pilot": prepared,
        "pilot_record": pilot_record,
        "claim_boundary": "Preparing the next pilot is not usage proof until the reporter completes a real task trial and the evidence is converted into a checked usage record.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="Override generated pilot harness target directory")
    parser.add_argument("--record-dir", default=usage_gaps.DEFAULT_RECORD_DIR.as_posix(), help="Directory where usage record JSON files are read")
    parser.add_argument("--index", type=int, default=1, help="1-based suggested pilot index from usage-gaps")
    parser.add_argument("--brief", help="Override selected pilot brief")
    parser.add_argument("--project-name", help="Override selected pilot project name")
    parser.add_argument("--notes", default="next pilot selected from usage evidence gaps", help="Notes for creation context")
    parser.add_argument("--domain", help="Override selected pilot domain")
    parser.add_argument("--slug", help="Override selected pilot usage-record slug")
    parser.add_argument("--title", help="Override selected pilot usage-record title")
    parser.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Override selected pilot source type")
    parser.add_argument("--generation-path", choices=sorted(prepare_pilot.ALLOWED_GENERATION_PATHS), help="Override selected pilot generation path")
    parser.add_argument("--harness-label", help="Public-safe harness label")
    parser.add_argument("--out", help="Pilot pack path")
    parser.add_argument("--issue-out", help="Issue-body draft path")
    parser.add_argument("--min-successes", type=int, default=1, help="Minimum passing success task trials expected for the later pilot")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum generated harness validation score")
    parser.add_argument("--target-label", help="Override target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), help="UTC timestamp for pilot metadata")
    parser.add_argument("--min-records", type=int, default=usage_gaps.DEFAULT_TARGETS["min_records"], help="Target valid usage records")
    parser.add_argument("--min-external-or-multi-project", type=int, default=usage_gaps.DEFAULT_TARGETS["min_external_or_multi_project"], help="Target external or multi-project records")
    parser.add_argument("--min-domains", type=int, default=usage_gaps.DEFAULT_TARGETS["min_domains"], help="Target distinct domains")
    parser.add_argument("--min-installed-init-brief", type=int, default=usage_gaps.DEFAULT_TARGETS["min_installed_init_brief"], help="Target records generated via installed brief-based generation")
    parser.add_argument("--pilot-record-dir", help="Optional directory where a prepared-pilot tracking record is written")
    parser.add_argument("--pilot-record-out", help="Optional explicit prepared-pilot tracking record path")
    parser.add_argument("--pilot-status", choices=sorted(pilot_board.ALLOWED_STATUSES), default="prepared", help="Status for optional pilot-board record")
    parser.add_argument("--pilot-notes", default="", help="Optional public-safe note for the pilot-board record")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        selected = payload["selected_pilot"]
        prepared = payload["prepared_pilot"]
        print(f"Prepare next pilot: {payload['status'].upper()}")
        print(f"- selected: {selected['domain']} ({selected['profile']})")
        print(f"- target: {prepared['target']}")
        print(f"- pilot pack: {prepared.get('pilot_pack', {}).get('pack')}")
        if payload["pilot_record"]:
            print(f"- pilot record: {payload['pilot_record'].get('path')}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
