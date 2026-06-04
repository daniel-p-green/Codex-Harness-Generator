#!/usr/bin/env python3
"""Prepare a Codex migration packet for a legacy Claude-style harness."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import migration_audit
import plan_project_adoption


DEFAULT_GENERATED_DATE = "2026-06-04"


def ensure_output_dir(path: Path, force: bool) -> None:
    if path.exists() and not path.is_dir():
        raise SystemExit(f"Output path exists and is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not force:
            raise SystemExit(f"Output directory is not empty. Re-run with --force to replace it: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_packet_readme(path: Path, payload: dict) -> Path:
    lines = [
        "# Codex Migration Packet",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Migration readiness: {payload['migration_readiness']}",
        f"Selected profile: `{payload['profile']}`",
        "",
        "This packet helps port a Claude-style harness or project into a Codex-native harness. It is intentionally non-destructive.",
        "",
        "## Packet Contents",
        "",
        f"- Migration audit: `{Path(payload['migration_report']).name}`",
        f"- Codex blueprint: `{Path(payload['blueprint']).name}/`",
        f"- Adoption plan: `{Path(payload['adoption_report']).name}`",
        f"- Add-only copy script: `{Path(payload['copy_script']).name}`",
        "",
        "## Recommended Flow",
        "",
        "1. Read the migration audit and adoption plan.",
        "2. Run the add-only copy script if the add rows look right.",
        "3. Merge conflict rows manually, preserving project-specific instructions.",
        "4. Run the post-adoption checks listed in the adoption plan.",
        "5. Archive legacy Claude files only after their useful content is translated.",
        "",
        "## Claim Boundary",
        "",
        "- Preparing this packet does not prove the harness is migrated.",
        "- The copy script refuses to overwrite existing files.",
        "- Legacy cleanup is a manual review step, not an automatic deletion.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_payload(args: argparse.Namespace) -> dict:
    source = Path(args.source)
    output = Path(args.output)
    if not source.exists():
        raise SystemExit(f"Source path does not exist: {source}")
    if not source.is_dir():
        raise SystemExit(f"Source path must be a directory: {source}")
    ensure_output_dir(output, args.force)

    migration_report = output / "CODEX_MIGRATION_PLAN.md"
    blueprint = output / "codex-blueprint"
    adoption_report = output / "HARNESS_ADOPTION_PLAN.md"
    copy_script = output / "copy-codex-harness-adds.sh"
    readme = output / "README.md"

    audit_payload = migration_audit.build_payload([source.as_posix()])
    migration_audit.write_report(migration_report, audit_payload)
    audit_result = audit_payload["results"][0]

    adoption_payload = plan_project_adoption.build_payload(
        project=source,
        profile=args.profile,
        project_name=args.project_name,
        harness=None,
        blueprint_out=blueprint,
        force_blueprint=True,
        max_files=args.max_files,
        limit=args.limit,
        generated_date=args.generated_date,
        source_label=args.source_label,
    )
    plan_project_adoption.write_report(adoption_report, adoption_payload)
    plan_project_adoption.write_copy_script(copy_script, adoption_payload, blueprint, source)

    payload = {
        "generated": args.generated,
        "status": "pass",
        "source_label": args.source_label or source.name,
        "output": output.as_posix(),
        "migration_readiness": audit_result["migration_plan"]["readiness"],
        "migration_status": audit_payload["status"],
        "migration_failures": audit_result["failure_count"],
        "migration_warnings": audit_result["warning_count"],
        "profile": adoption_payload["profile"],
        "adoption_summary": adoption_payload["summary"],
        "migration_report": migration_report.as_posix(),
        "blueprint": blueprint.as_posix(),
        "adoption_report": adoption_report.as_posix(),
        "copy_script": copy_script.as_posix(),
        "readme": readme.as_posix(),
        "claim_boundary": (
            "Preparing a migration packet is not proof of migration; apply the add-only script, merge conflicts "
            "manually, run post-adoption checks, and archive legacy files only after translation."
        ),
    }
    write_packet_readme(readme, payload)
    return payload


def print_text(payload: dict) -> None:
    print(f"Migration packet: {payload['status'].upper()}")
    print(f"- source label: {payload['source_label']}")
    print(f"- migration readiness: {payload['migration_readiness']}")
    print(f"- selected profile: {payload['profile']}")
    print(f"- add: {payload['adoption_summary'].get('add', 0)}")
    print(f"- conflicts: {payload['adoption_summary'].get('conflict', 0)}")
    print(f"- output: {payload['output']}")
    print(f"- migration audit: {payload['migration_report']}")
    print(f"- adoption plan: {payload['adoption_report']}")
    print(f"- copy script: {payload['copy_script']}")
    print(f"- boundary: {payload['claim_boundary']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Legacy Claude-style harness or project directory")
    parser.add_argument("output", help="Output directory for the migration packet")
    parser.add_argument("--profile", help="Starter profile override; defaults to inspection recommendation")
    parser.add_argument("--project-name", help="Project name for generated blueprint docs")
    parser.add_argument("--source-label", help="Public-safe label for the source project")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum source files to inspect")
    parser.add_argument("--limit", type=int, default=3, help="Number of inspection recommendations to consider")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for blueprint docs")
    parser.add_argument(
        "--generated",
        default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        help="UTC timestamp for packet metadata",
    )
    parser.add_argument("--force", action="store_true", help="Replace output directory contents")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args(argv)

    payload = build_payload(args)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
