#!/usr/bin/env python3
"""Run deterministic /create acceptance from a short project brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval_generated_harness import evaluate
from profile_catalog import recommendation_payload
from run_create_acceptance import DEFAULT_CREATED, DEFAULT_GENERATED_DATE, append_manifest_entry, run_acceptance


PROFILE_SELECTION_PATH = Path("Docs") / "Environment" / "PROFILE_SELECTION.md"


def write_profile_selection(target: Path, brief: str, recommendations: dict) -> Path:
    selected = recommendations["recommendations"][0]
    lines = [
        "# Profile Selection",
        "",
        "Flow: deterministic brief-based acceptance.",
        f"Brief: {brief}",
        "",
        "## Selected Profile",
        "",
        f"- Profile: {selected['slug']}",
        f"- Score: {selected['score']}",
        f"- Confidence: {selected['confidence']}",
        f"- Domain: {selected['domain']}",
        f"- Target: {selected['target']}",
        f"- Matched terms: {', '.join(selected['matched_terms']) if selected['matched_terms'] else 'none'}",
        "",
        "## Alternatives",
        "",
    ]
    for item in recommendations["recommendations"][1:]:
        lines.append(
            f"- {item['slug']}: score={item['score']}; matched={', '.join(item['matched_terms']) if item['matched_terms'] else 'none'}"
        )
    if len(recommendations["recommendations"]) == 1:
        lines.append("- None with a positive deterministic match.")
    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- This is deterministic keyword selection, not model judgment.",
            "- If the selected profile does not fit the real project, use `/create` custom intake or pass an explicit profile.",
        ]
    )
    path = target / PROFILE_SELECTION_PATH
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    append_manifest_entry(target, PROFILE_SELECTION_PATH)
    return path


def run_brief_acceptance(
    target: Path,
    brief: str,
    project_name: str | None,
    notes: str,
    force: bool,
    generated_date: str,
    created: str,
    limit: int,
    allow_low_confidence: bool,
    target_label: str | None = None,
) -> dict:
    recommendations = recommendation_payload(brief, limit=limit)
    selected = recommendations["recommendations"][0]
    if selected["confidence"] == "none" and not allow_low_confidence:
        raise SystemExit(
            "No confident deterministic profile match. Use a clearer --brief, pass --allow-low-confidence, "
            "or run the full `/create` custom intake."
        )

    payload = run_acceptance(
        target=target,
        profile=selected["slug"],
        project_name=project_name,
        project_type=selected["domain"],
        notes=f"{notes}; brief: {brief}" if notes else f"brief: {brief}",
        force=force,
        generated_date=generated_date,
        created=created,
        target_label=target_label,
    )
    target_path = Path(payload["target"])
    selection_path = write_profile_selection(target_path, brief, recommendations)
    final_eval = evaluate(target_path)
    status = "pass" if final_eval["status"] == "pass" and payload["smoke"]["status"] == "pass" else "fail"
    payload.update(
        {
            "status": status,
            "brief": brief,
            "recommendations": recommendations,
            "profile": selected["slug"],
            "profile_selection": selection_path.as_posix(),
            "eval": final_eval,
        }
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="Target project directory for brief-based deterministic acceptance")
    parser.add_argument("--brief", required=True, help="Short project brief used to select a deterministic profile")
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--notes", default="brief-based deterministic acceptance", help="Notes for creation context")
    parser.add_argument("--generated-date", default=DEFAULT_GENERATED_DATE, help="Stable generated date for generated docs")
    parser.add_argument("--created", default=DEFAULT_CREATED, help="Stable created timestamp for CREATION_CONTEXT.md")
    parser.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    parser.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = run_brief_acceptance(
        target=Path(args.target),
        brief=args.brief,
        project_name=args.project_name,
        notes=args.notes,
        force=args.force,
        generated_date=args.generated_date,
        created=args.created,
        limit=args.limit,
        allow_low_confidence=args.allow_low_confidence,
        target_label=args.target_label,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Brief acceptance: {payload['status'].upper()}")
        print(f"- target: {payload['target']}")
        print(f"- selected profile: {payload['profile']}")
        print(f"- eval: {payload['eval']['status'].upper()} score={payload['eval']['score']}")
        print(f"- smoke: {payload['smoke']['status'].upper()}")
        print(f"- profile selection: {payload['profile_selection']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
