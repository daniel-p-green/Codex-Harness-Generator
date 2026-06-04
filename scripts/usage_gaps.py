#!/usr/bin/env python3
"""Report remaining usage-evidence gaps for beta exit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from profile_catalog import catalog_payload
from record_usage_case import DEFAULT_RECORD_DIR, load_records
from validate_usage_records import validate_record_dir


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "USAGE_GAPS.md"
DEFAULT_TARGETS = {
    "min_records": 5,
    "min_external_or_multi_project": 3,
    "min_domains": 4,
    "min_installed_init_brief": 2,
}
PILOT_PROFILE_PRIORITY = [
    "llm-app",
    "security-audit",
    "customer-support",
    "data-analysis",
    "legal-research",
    "financial-modeling",
    "hiring-pipeline",
    "software-development",
    "api-design",
    "product-management",
    "knowledge-work",
]


def record_domains(records: list[dict]) -> list[str]:
    return sorted({record.get("domain", "").strip() for record in records if record.get("domain", "").strip()})


def build_gaps(summary: dict, targets: dict) -> dict:
    return {
        "records": max(targets["min_records"] - summary["total"], 0),
        "external_or_multi_project": max(
            targets["min_external_or_multi_project"] - summary["external_or_multi_project"],
            0,
        ),
        "domains": max(targets["min_domains"] - summary["distinct_domains"], 0),
        "installed_init_brief": max(
            targets["min_installed_init_brief"] - summary["installed_brief_generation"],
            0,
        ),
    }


def build_recommendations(gaps: dict) -> list[str]:
    if not any(gaps.values()):
        return ["Beta-exit usage thresholds are satisfied; run proof-status with beta-exit thresholds before changing the README status."]
    recommendations = []
    if gaps["external_or_multi_project"]:
        recommendations.append(
            f"Collect {gaps['external_or_multi_project']} more external or multi-project usage record(s)."
        )
    if gaps["installed_init_brief"]:
        recommendations.append(
            f"Make at least {gaps['installed_init_brief']} of the next record(s) use installed brief-based generation (`codex-harness prepare-next-pilot`, `codex-harness prepare-pilot`, `codex-harness quickstart`, or `codex-harness init --brief`)."
        )
    if gaps["domains"]:
        recommendations.append(
            f"Cover {gaps['domains']} more distinct usage domain(s) instead of adding more same-domain proof."
        )
    if gaps["records"]:
        recommendations.append(f"Add {gaps['records']} more valid non-synthetic usage record(s).")
    recommendations.append(
        "For the next suggested pilot, run `codex-harness prepare-next-pilot <target>` or copy the `codex-harness prepare-pilot <target>` command, review the generated pack, then convert completed evidence with `usage-from-harness` or `usage-from-issue`."
    )
    return recommendations


def profile_candidates() -> list[dict]:
    profiles = {profile["slug"]: profile for profile in catalog_payload()["profiles"]}
    ordered = [profiles[slug] for slug in PILOT_PROFILE_PRIORITY if slug in profiles]
    ordered.extend(profile for slug, profile in sorted(profiles.items()) if slug not in PILOT_PROFILE_PRIORITY)
    return ordered


def build_suggested_pilots(domains: list[str], gaps: dict) -> list[dict]:
    target_count = max(gaps.values()) if gaps else 0
    if target_count == 0:
        return []

    represented = {domain.casefold() for domain in domains}
    candidates = [
        profile
        for profile in profile_candidates()
        if profile["domain"].casefold() not in represented
    ]
    if len(candidates) < target_count:
        candidates.extend(
            profile
            for profile in profile_candidates()
            if profile["domain"].casefold() in represented
        )

    pilots = []
    for index, profile in enumerate(candidates[:target_count]):
        source_type = "external" if index < gaps["external_or_multi_project"] else "multi-project"
        generation_path = "installed-quickstart"
        slug = f"{profile['slug']}-pilot"
        title = f"{profile['domain']} pilot"
        project_name = f"{profile['default_project_name']} Pilot"
        brief = f"{profile['target']} with one privacy-safe task, local eval, and public-safe usage evidence"
        target_path = f"/tmp/codex-{slug}"
        prepare_command = [
            "codex-harness",
            "prepare-pilot",
            target_path,
            "--brief",
            json.dumps(brief),
            "--project-name",
            json.dumps(project_name),
            "--domain",
            json.dumps(profile["domain"]),
            "--slug",
            slug,
            "--title",
            json.dumps(title),
            "--source-type",
            source_type,
            "--generation-path",
            generation_path,
            "--force",
        ]
        pilots.append(
            {
                "profile": profile["slug"],
                "domain": profile["domain"],
                "source_type": source_type,
                "generation_path": generation_path,
                "target": target_path,
                "project_name": project_name,
                "slug": slug,
                "title": title,
                "brief": brief,
                "commands": [
                    " ".join(prepare_command),
                ],
            }
        )
    return pilots


def build_payload(
    record_dir: Path,
    min_records: int = DEFAULT_TARGETS["min_records"],
    min_external_or_multi_project: int = DEFAULT_TARGETS["min_external_or_multi_project"],
    min_domains: int = DEFAULT_TARGETS["min_domains"],
    min_installed_init_brief: int = DEFAULT_TARGETS["min_installed_init_brief"],
) -> dict:
    targets = {
        "min_records": min_records,
        "min_external_or_multi_project": min_external_or_multi_project,
        "min_domains": min_domains,
        "min_installed_init_brief": min_installed_init_brief,
    }
    validation = validate_record_dir(record_dir, require_non_synthetic=True, require_success=True)
    records = load_records(record_dir)
    domains = record_domains(records)
    gaps = build_gaps(validation["summary"], targets)
    ready = validation["status"] == "pass" and not any(gaps.values())
    suggested_pilots = build_suggested_pilots(domains, gaps)
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": validation["status"],
        "readiness": "beta-exit-evidence-ready" if ready else "missing-beta-exit-evidence",
        "targets": targets,
        "summary": validation["summary"],
        "gaps": gaps,
        "domains": domains,
        "recommendations": build_recommendations(gaps),
        "suggested_pilots": suggested_pilots,
        "validation": validation,
    }


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Usage Evidence Gaps",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        "This report shows what usage evidence is still missing before the repo can",
        "honestly stop calling itself a beta.",
        "",
        "## Targets",
        "",
        f"- Total usage records: {payload['targets']['min_records']}",
        f"- External or multi-project records: {payload['targets']['min_external_or_multi_project']}",
        f"- Distinct domains: {payload['targets']['min_domains']}",
        f"- Installed brief-based generation records: {payload['targets']['min_installed_init_brief']}",
        "",
        "## Current Summary",
        "",
        f"- Total usage records: {payload['summary']['total']}",
        f"- Non-synthetic records: {payload['summary']['non_synthetic']}",
        f"- Successful records: {payload['summary']['success']}",
        f"- External or multi-project records: {payload['summary']['external_or_multi_project']}",
        f"- Distinct domains: {payload['summary']['distinct_domains']}",
        f"- Installed brief-based generation records: {payload['summary']['installed_brief_generation']}",
        "",
        "## Remaining Gaps",
        "",
        f"- Usage records: {payload['gaps']['records']}",
        f"- External or multi-project records: {payload['gaps']['external_or_multi_project']}",
        f"- Distinct domains: {payload['gaps']['domains']}",
        f"- Installed brief-based generation records: {payload['gaps']['installed_init_brief']}",
        "",
        "## Represented Domains",
        "",
    ]
    if payload["domains"]:
        lines.extend(f"- {domain}" for domain in payload["domains"])
    else:
        lines.append("- none")
    lines.extend(["", "## Suggested Pilot Targets", ""])
    if payload["suggested_pilots"]:
        for index, pilot in enumerate(payload["suggested_pilots"], start=1):
            lines.extend(
                [
                    f"### {index}. {pilot['domain']} (`{pilot['profile']}`)",
                    "",
                    f"- Source type: `{pilot['source_type']}`",
                    f"- Generation path: `{pilot['generation_path']}`",
                    f"- Brief: {pilot['brief']}",
                    "",
                    "```bash",
                    *pilot["commands"],
                    "```",
                    "",
                ]
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Recommended Next Moves", ""])
    lines.extend(f"- {item}" for item in payload["recommendations"])
    if payload["validation"]["requirement_errors"]:
        lines.extend(["", "## Validation Requirements", ""])
        lines.extend(f"- {item}" for item in payload["validation"]["requirement_errors"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix())
    parser.add_argument("--min-records", type=int, default=DEFAULT_TARGETS["min_records"])
    parser.add_argument("--min-external-or-multi-project", type=int, default=DEFAULT_TARGETS["min_external_or_multi_project"])
    parser.add_argument("--min-domains", type=int, default=DEFAULT_TARGETS["min_domains"])
    parser.add_argument("--min-installed-init-brief", type=int, default=DEFAULT_TARGETS["min_installed_init_brief"])
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    payload = build_payload(
        Path(args.record_dir),
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Usage evidence gaps: {payload['readiness']}")
        for key, value in payload["gaps"].items():
            print(f"- {key}: {value}")
        for pilot in payload["suggested_pilots"]:
            print(f"- pilot: {pilot['domain']} ({pilot['profile']}) via {pilot['generation_path']}")
        for item in payload["recommendations"]:
            print(f"- next: {item}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
