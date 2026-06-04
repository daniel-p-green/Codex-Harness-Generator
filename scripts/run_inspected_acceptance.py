#!/usr/bin/env python3
"""Generate a harness from local project inspection metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval_generated_harness import evaluate
from inspect_project import build_payload as build_inspection_payload
from run_brief_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE, append_manifest_entry, write_profile_selection
from run_create_acceptance import run_acceptance


PROJECT_INSPECTION_PATH = Path("Docs") / "Environment" / "PROJECT_INSPECTION.md"


def write_project_inspection(target: Path, inspection: dict, source_label: str) -> Path:
    lines = [
        "# Project Inspection",
        "",
        "Flow: metadata-based project inspection before deterministic harness generation.",
        f"Source label: {source_label}",
        f"Files scanned: {inspection['files_scanned']}{' (truncated)' if inspection['truncated'] else ''}",
        f"Inferred brief: {inspection['inferred_brief']}",
        "",
        "## Signals",
        "",
        f"- Config files: {', '.join(inspection['signals']['config_files']) if inspection['signals']['config_files'] else 'none detected'}",
        f"- Directories: {', '.join(inspection['signals']['directories']) if inspection['signals']['directories'] else 'none detected'}",
        "- Extensions: "
        + (
            ", ".join(f"{key}={value}" for key, value in inspection["signals"]["extensions"].items())
            if inspection["signals"]["extensions"]
            else "none detected"
        ),
        "",
        "## Recommendations",
        "",
    ]
    for index, item in enumerate(inspection["recommendations"]["recommendations"], 1):
        matched = ", ".join(item["matched_terms"]) if item["matched_terms"] else "none"
        lines.append(
            f"{index}. `{item['slug']}`: score={item['score']}; inspection_score={item['inspection_score']}; confidence={item['confidence']}; matched={matched}"
        )
    lines.extend(
        [
            "",
            "## Privacy Boundary",
            "",
            "- Inspection uses project metadata: filenames, top-level directories, extensions, and counts.",
            "- It does not copy source contents into this report.",
            "- Verify the generated harness against the real project before relying on it.",
        ]
    )
    path = target / PROJECT_INSPECTION_PATH
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    append_manifest_entry(target, PROJECT_INSPECTION_PATH)
    return path


def run_inspected_acceptance(
    target: Path,
    source: Path,
    project_name: str | None,
    notes: str,
    force: bool,
    generated_date: str,
    created: str,
    limit: int,
    max_files: int,
    allow_low_confidence: bool,
    target_label: str | None = None,
    source_label: str | None = None,
) -> dict:
    inspection = build_inspection_payload(source, max_files=max_files, limit=limit)
    selected = inspection["recommendations"]["recommendations"][0]
    if selected["confidence"] == "none" and not allow_low_confidence:
        raise SystemExit(
            "No confident metadata-based profile match. Use --allow-low-confidence, pass --brief, "
            "or run the full `/create` custom intake."
        )

    resolved_project_name = project_name or inspection["project"]
    resolved_source_label = source_label or inspection["project"]
    payload = run_acceptance(
        target=target,
        profile=selected["slug"],
        project_name=resolved_project_name,
        project_type=selected["domain"],
        notes=f"{notes}; inspected source: {resolved_source_label}" if notes else f"inspected source: {resolved_source_label}",
        force=force,
        generated_date=generated_date,
        created=created,
        target_label=target_label,
    )
    target_path = Path(payload["target"])
    selection_path = write_profile_selection(
        target_path,
        inspection["inferred_brief"],
        inspection["recommendations"],
        flow="metadata-inspected deterministic acceptance",
    )
    inspection_path = write_project_inspection(target_path, inspection, resolved_source_label)
    final_eval = evaluate(target_path)
    status = "pass" if final_eval["status"] == "pass" and payload["smoke"]["status"] == "pass" else "fail"
    payload.update(
        {
            "status": status,
            "brief": inspection["inferred_brief"],
            "recommendations": inspection["recommendations"],
            "profile": selected["slug"],
            "profile_selection": selection_path.as_posix(),
            "eval": final_eval,
            "inspection": inspection,
            "inspection_report": inspection_path.as_posix(),
            "source_label": resolved_source_label,
            "project_name": resolved_project_name,
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target project directory for generated harness")
    parser.add_argument("--from-project", required=True, help="Existing project directory to inspect")
    parser.add_argument("--project-name", help="Human-readable project name; defaults to inspected directory name")
    parser.add_argument("--notes", default="metadata-inspected deterministic acceptance", help="Notes for creation context")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--source-label", help="Public-safe label for the inspected project")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum source files to inspect before truncating")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = run_inspected_acceptance(
        target=Path(args.target),
        source=Path(args.from_project),
        project_name=args.project_name,
        notes=args.notes,
        force=args.force,
        generated_date=args.generated_date,
        created=args.created,
        limit=args.limit,
        max_files=args.max_files,
        allow_low_confidence=args.allow_low_confidence,
        target_label=args.target_label,
        source_label=args.source_label,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Inspected acceptance: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- inspected project: {payload['source_label']}")
        print(f"- selected profile: {payload['profile']}")
        print(f"- eval: {payload['eval']['status'].upper()} score={payload['eval']['score']}")
        print(f"- smoke: {payload['smoke']['status'].upper()}")
        print(f"- inspection report: {payload['inspection_report']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
