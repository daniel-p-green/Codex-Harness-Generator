#!/usr/bin/env python3
"""Prepare a generated harness plus external pilot evidence kit in one command."""

from __future__ import annotations

import argparse
import json
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

import export_pilot_pack
import run_quickstart
from record_usage_case import ALLOWED_GENERATION_PATHS
from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE


DEFAULT_BRIEF = "LLM-powered app, RAG, agent, prompt, and eval workflow development with one privacy-safe task, local eval, and public-safe usage evidence"
DEFAULT_TARGET = "/tmp/codex-external-pilot"


def default_issue_path(target: Path) -> Path:
    return target / "Docs" / "Environment" / export_pilot_pack.DEFAULT_ISSUE_NAME


def build_quickstart_args(args: argparse.Namespace, target: Path) -> Namespace:
    return Namespace(
        target=target.as_posix(),
        brief=args.brief,
        project_name=args.project_name,
        notes=args.notes,
        generated_date=args.generated_date,
        created=args.created,
        target_label=args.target_label,
        limit=args.limit,
        allow_low_confidence=args.allow_low_confidence,
        force=args.force,
        min_score=args.min_score,
        min_successes=0,
        no_write=False,
    )


def build_pilot_pack_args(args: argparse.Namespace, target: Path) -> Namespace:
    return Namespace(
        harness=target.as_posix(),
        out=args.out,
        issue_out=args.issue_out or default_issue_path(target).as_posix(),
        harness_label=args.harness_label or args.project_name,
        domain=args.domain,
        slug=args.slug,
        title=args.title,
        source_type=args.source_type,
        generation_path=args.generation_path,
        min_successes=args.min_successes,
        prefill_from_trials=False,
        generated=args.generated,
    )


def build_payload(args: argparse.Namespace) -> dict:
    if args.generation_path not in ALLOWED_GENERATION_PATHS:
        raise SystemExit(f"Unsupported generation path: {args.generation_path}")

    target = Path(args.target).expanduser().resolve()
    quickstart = run_quickstart.build_payload(build_quickstart_args(args, target))
    pilot_pack = None
    if quickstart["status"] == "pass":
        pack_args = build_pilot_pack_args(args, target)
        pack_payload = export_pilot_pack.build_payload(pack_args)
        pilot_pack = export_pilot_pack.write_outputs(pack_args, pack_payload)

    status = "pass" if quickstart["status"] == "pass" and pilot_pack and pilot_pack["status"] == "pass" else "fail"
    return {
        "generated": args.generated,
        "status": status,
        "target": target.as_posix(),
        "brief": args.brief,
        "profile": quickstart.get("profile"),
        "domain": args.domain,
        "source_type": args.source_type,
        "generation_path": args.generation_path,
        "quickstart": quickstart,
        "pilot_pack": pilot_pack,
        "next_steps": [
            f"Open the generated harness at {target.as_posix()}.",
            "Ask the reporter to complete one small real Codex task using Docs/GETTING_STARTED.md.",
            "Record the result with scripts/record-task-trial.py, including evidence, verification, privacy review, and limitations.",
            "Run scripts/run-harness-evals.py from the generated harness.",
            "Convert public-safe evidence with codex-harness usage-from-harness or codex-harness usage-from-issue.",
        ],
        "claim_boundary": "Prepared pilot materials are not usage proof until a real task trial is recorded and converted into a checked usage record.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default=DEFAULT_TARGET, help="Generated pilot harness target directory")
    parser.add_argument("--brief", default=DEFAULT_BRIEF, help="Short pilot project brief")
    parser.add_argument("--project-name", default="External Pilot Harness", help="Human-readable project name")
    parser.add_argument("--notes", default="external pilot preparation", help="Notes for creation context")
    parser.add_argument("--domain", required=True, help="Public-safe usage domain")
    parser.add_argument("--slug", required=True, help="Suggested usage-record slug")
    parser.add_argument("--title", required=True, help="Suggested usage-record title")
    parser.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], default="external")
    parser.add_argument("--generation-path", choices=sorted(ALLOWED_GENERATION_PATHS), default="installed-quickstart")
    parser.add_argument("--harness-label", help="Public-safe harness label; defaults to --project-name")
    parser.add_argument("--out", help="Pilot pack path; defaults inside the generated harness")
    parser.add_argument("--issue-out", help="Issue-body draft path; defaults inside the generated harness")
    parser.add_argument("--min-successes", type=int, default=1, help="Minimum passing success task trials expected for the later pilot")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum generated harness validation score")
    parser.add_argument("--target-label", help="Override target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), help="UTC timestamp for pilot pack metadata")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Prepare pilot: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- selected profile: {payload['profile']}")
        if payload["pilot_pack"]:
            print(f"- pilot pack: {payload['pilot_pack']['pack']}")
            if "issue_draft" in payload["pilot_pack"]:
                print(f"- issue draft: {payload['pilot_pack']['issue_draft']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
