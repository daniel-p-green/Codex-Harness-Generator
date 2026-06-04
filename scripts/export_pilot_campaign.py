#!/usr/bin/env python3
"""Write a shareable pilot campaign plan from current usage-evidence gaps."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from record_usage_case import DEFAULT_RECORD_DIR, find_sensitive_text
from usage_gaps import DEFAULT_TARGETS, build_payload as build_usage_gap_payload


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "PILOT_CAMPAIGN.md"


def build_payload(
    record_dir: Path,
    max_pilots: int = 3,
    min_records: int = DEFAULT_TARGETS["min_records"],
    min_external_or_multi_project: int = DEFAULT_TARGETS["min_external_or_multi_project"],
    min_domains: int = DEFAULT_TARGETS["min_domains"],
    min_installed_init_brief: int = DEFAULT_TARGETS["min_installed_init_brief"],
) -> dict:
    usage_gaps = build_usage_gap_payload(
        record_dir,
        min_records=min_records,
        min_external_or_multi_project=min_external_or_multi_project,
        min_domains=min_domains,
        min_installed_init_brief=min_installed_init_brief,
    )
    suggested_pilots = usage_gaps["suggested_pilots"][:max(max_pilots, 0)]
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": usage_gaps["status"],
        "readiness": usage_gaps["readiness"],
        "usage_gaps": usage_gaps,
        "pilot_count": len(suggested_pilots),
        "pilots": suggested_pilots,
    }


def write_report(path: Path, payload: dict) -> None:
    gaps = payload["usage_gaps"]["gaps"]
    summary = payload["usage_gaps"]["summary"]
    lines = [
        "# External Pilot Campaign",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        "This campaign packet turns the current beta-exit evidence gaps into",
        "concrete external or multi-project pilot asks. It is an evidence",
        "collection plan, not adoption proof.",
        "Use `codex-harness prepare-next-pilot <target>` to prepare the first",
        "suggested pilot directly from the current gaps.",
        "",
        "## Current Evidence Gap",
        "",
        f"- Valid usage records: {summary['total']}",
        f"- External or multi-project records: {summary['external_or_multi_project']}",
        f"- Distinct domains: {summary['distinct_domains']}",
        f"- Installed brief-based generation records: {summary['installed_brief_generation']}",
        "",
        "## Remaining Targets",
        "",
        f"- Usage records to add: {gaps['records']}",
        f"- External or multi-project records to add: {gaps['external_or_multi_project']}",
        f"- Distinct domains to add: {gaps['domains']}",
        f"- Installed brief-based generation records to add: {gaps['installed_init_brief']}",
        "",
        "## Pilot Slots",
        "",
    ]
    if payload["pilots"]:
        for index, pilot in enumerate(payload["pilots"], start=1):
            lines.extend(
                [
                    f"### {index}. {pilot['domain']} (`{pilot['profile']}`)",
                    "",
                    f"- Source type: `{pilot['source_type']}`",
                    f"- Generation path: `{pilot['generation_path']}`",
                    f"- Pilot ask: try one privacy-safe task, run local eval, then submit a public-safe issue-body report.",
                    "",
                    "```bash",
                    *pilot["commands"],
                    "```",
                    "",
                    "Reporter evidence checklist:",
                    "",
                    "- One concrete task summary.",
                    "- At least two evidence bullets.",
                    "- At least two verification bullets.",
                    "- A privacy review confirming no secrets, personal data, private paths, proprietary source, or raw private logs.",
                    "- One limitation that keeps the claim scoped to this pilot.",
                    "",
                ]
            )
    else:
        lines.append("- none")
        lines.append("")
    lines.extend(
        [
            "## Maintainer Follow-Up",
            "",
            "After each pilot:",
            "",
            "1. Review the pilot pack and issue draft for privacy-sensitive text.",
            "2. Convert acceptable evidence with `codex-harness usage-from-harness` or `codex-harness usage-from-issue`.",
            "3. Re-run `codex-harness usage-gaps` and refresh this campaign only if gaps remain.",
            "4. Do not drop the beta label until `codex-harness proof-status` passes with the beta-exit thresholds.",
            "",
            "## Claim Boundary",
            "",
            "These pilots can support narrow usage evidence. They do not prove broad external adoption, longitudinal private-repo performance, production security, compliance, or every future live `/create` run.",
        ]
    )
    text = "\n".join(lines).rstrip() + "\n"
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit("Refusing to write pilot campaign with sensitive text: " + ", ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=DEFAULT_RECORD_DIR.as_posix())
    parser.add_argument("--out", default=DEFAULT_REPORT.as_posix(), help="Pilot campaign Markdown path")
    parser.add_argument("--max-pilots", type=int, default=3, help="Maximum suggested pilot slots to include")
    parser.add_argument("--min-records", type=int, default=DEFAULT_TARGETS["min_records"])
    parser.add_argument("--min-external-or-multi-project", type=int, default=DEFAULT_TARGETS["min_external_or_multi_project"])
    parser.add_argument("--min-domains", type=int, default=DEFAULT_TARGETS["min_domains"])
    parser.add_argument("--min-installed-init-brief", type=int, default=DEFAULT_TARGETS["min_installed_init_brief"])
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown campaign")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(
        Path(args.record_dir),
        max_pilots=args.max_pilots,
        min_records=args.min_records,
        min_external_or_multi_project=args.min_external_or_multi_project,
        min_domains=args.min_domains,
        min_installed_init_brief=args.min_installed_init_brief,
    )
    if not args.no_write:
        write_report(Path(args.out), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot campaign: {payload['readiness']}")
        for pilot in payload["pilots"]:
            print(f"- {pilot['domain']} ({pilot['profile']}): {pilot['source_type']} / {pilot['generation_path']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
