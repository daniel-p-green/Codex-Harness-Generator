#!/usr/bin/env python3
"""Write a privacy-safe external pilot guide for a generated harness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from record_usage_case import ALLOWED_GENERATION_PATHS, find_sensitive_text
from usage_from_harness import VALID_OUTCOMES, parse_eval_report, parse_task_entries


DEFAULT_PACK_NAME = "EXTERNAL_PILOT_PACK.md"
DEFAULT_ISSUE_NAME = "EXTERNAL_USAGE_ISSUE_DRAFT.md"


def read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def infer_profile(harness: Path) -> str:
    manifest = read_optional(harness / "Docs" / "Environment" / "MANIFEST.md").lower()
    for marker in ("profile:", "starter profile:"):
        if marker in manifest:
            line = next((line for line in manifest.splitlines() if marker in line), "")
            value = line.split(marker, 1)[-1].strip(" -*`")
            if value:
                return value
    creation_context = read_optional(harness / "Docs" / "Environment" / "CREATION_CONTEXT.md").lower()
    if "profile:" in creation_context:
        line = next((line for line in creation_context.splitlines() if "profile:" in line), "")
        value = line.split("profile:", 1)[-1].strip(" -*`")
        if value:
            return value
    profile_selection = read_optional(harness / "Docs" / "Environment" / "PROFILE_SELECTION.md").lower()
    for marker in ("- profile:", "selected profile:"):
        if marker in profile_selection:
            line = next((line for line in profile_selection.splitlines() if marker in line), "")
            value = line.split(marker, 1)[-1].strip(" -*`")
            if value:
                return value
    return "not recorded"


def complete_task_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        entry
        for entry in entries
        if entry.get("task")
        and entry.get("outcome") in VALID_OUTCOMES
        and entry.get("evidence")
        and entry.get("verification")
        and entry.get("privacy_review")
        and entry.get("limitations")
        and entry.get("limitations", "").lower() not in {"none", "none stated", "not stated"}
    ]


def task_trial_prefill(harness: Path) -> dict:
    task_trials_path = harness / "Docs" / "Environment" / "TASK_TRIALS.md"
    eval_report_path = harness / "Docs" / "Environment" / "EVAL_REPORT.md"
    if not task_trials_path.is_file():
        raise SystemExit(f"Missing task trials file for prefill: {task_trials_path}")
    if not eval_report_path.is_file():
        raise SystemExit(f"Missing eval report file for prefill: {eval_report_path}")
    entries = complete_task_entries(parse_task_entries(read_optional(task_trials_path)))
    if not entries:
        raise SystemExit("No complete task-trial entries found for prefill. Record a task trial before using --prefill-from-trials.")
    entry = entries[-1]
    eval_report = parse_eval_report(read_optional(eval_report_path))
    return {
        "outcome": entry["outcome"],
        "task_summary": entry["task"],
        "evidence": [
            entry["evidence"],
            f"Generated harness local eval report status: {eval_report.get('status', 'unknown').upper()}.",
        ],
        "verification": [
            entry["verification"],
            "Copied-harness eval report was reviewed before public reporting.",
        ],
        "privacy_review": entry["privacy_review"],
        "limitations": [entry["limitations"]],
    }


def build_issue_draft(payload: dict) -> str:
    prefill = payload.get("prefill") or {}
    evidence = prefill.get("evidence") or ["_No response_", "_No response_"]
    verification = prefill.get("verification") or ["_No response_", "_No response_"]
    limitations = prefill.get("limitations") or ["One task in one generated harness; not longitudinal proof."]
    return "\n".join(
        [
            "### Domain or project type",
            "",
            payload["domain"],
            "",
            "### Generated harness profile or label",
            "",
            payload["harness_label"],
            "",
            "### Evidence type",
            "",
            "private-summary",
            "",
            "### Source type",
            "",
            payload["source_type"],
            "",
            "### Generation path",
            "",
            payload["generation_path"],
            "",
            "### Outcome",
            "",
            prefill.get("outcome", "_No response_"),
            "",
            "### Public-safe task summary",
            "",
            prefill.get("task_summary", "_No response_"),
            "",
            "### Evidence",
            "",
            *[f"- {item}" for item in evidence],
            "",
            "### Verification performed",
            "",
            *[f"- {item}" for item in verification],
            "",
            "### Privacy review",
            "",
            prefill.get(
                "privacy_review",
                "Reporter confirmed the public summary excludes secrets, personal data, proprietary source, private repository names, local machine paths, email addresses, and raw private logs.",
            ),
            "",
            "### Limitations",
            "",
            *[f"- {item}" for item in limitations],
        ]
    ).rstrip() + "\n"


def build_pack(payload: dict, issue_draft_name: str | None) -> str:
    issue_line = ""
    if issue_draft_name:
        issue_line = f"- Fill out `{issue_draft_name}`, then paste it into the GitHub External usage report issue.\n"
    prefill_note = "This issue draft is blank until the reporter fills it in."
    if payload.get("prefill"):
        prefill_note = "This issue draft is prefilled from the latest complete task-trial record; review and redact it before sharing."
    return f"""
# External Pilot Pack

Generated: {payload["generated_at"]}
Harness label: {payload["harness_label"]}
Domain: {payload["domain"]}
Source type: {payload["source_type"]}
Generation path: {payload["generation_path"]}
Detected profile: {payload["profile"]}

This pack helps a reporter try one real Codex task with a generated harness and
produce public-safe evidence. It is a pilot workflow, not a production-readiness
claim.

## Privacy Boundary

Do not share secrets, tokens, API keys, passwords, private keys, customer data,
candidate data, payment data, health data, personal data, proprietary source,
private repository names, local machine paths, email addresses, raw private logs,
or raw private transcripts.

Use `private-summary` when the raw evidence cannot be public. The public report
should describe what happened, how it was verified, the privacy review, and the
limits.

## Reporter Steps

Run these commands from the copied generated harness directory:

```bash
python scripts/check-harness.py
```

Pick one small real task from `Docs/GETTING_STARTED.md`, complete it with Codex,
then record the result:

```bash
python scripts/record-task-trial.py --task "short public-safe task" --outcome success --evidence "public-safe artifact or private-summary" --verification "command or reviewer check" --privacy-review "public-safe summary only" --limitations "one pilot task"
```

Then run the copied-harness eval:

```bash
python scripts/run-harness-evals.py --min-successes {payload["min_successes"]}
```

## Maintainer Commands

From this generator repo, export a public-safe packet:

```bash
python scripts/codex_harness.py evidence-packet <generated-harness> --harness-label "{payload["harness_label"]}" --min-successes {payload["min_successes"]}
```

If the packet is public-safe and complete, convert the copied-harness evidence:

```bash
python scripts/codex_harness.py usage-from-harness <generated-harness> --slug "{payload["slug"]}" --title "{payload["title"]}" --domain "{payload["domain"]}" --harness-label "{payload["harness_label"]}" --evidence-type private-summary --source-type {payload["source_type"]} --generation-path {payload["generation_path"]} --privacy-review "Reporter confirmed public-safe private-summary evidence only." --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md
```

Or convert the GitHub issue body after review:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md --slug "{payload["slug"]}" --title "{payload["title"]}" --source-type {payload["source_type"]} --generation-path {payload["generation_path"]} --pilot-record-dir Docs/Environment/pilot-records --pilot-board-report Docs/Environment/PILOT_BOARD.md
```

## Issue Draft

{issue_line}- Keep raw evidence private unless it is already safe for public release.
- {prefill_note}
- Include at least two evidence bullets, two verification bullets, one privacy
  review, and one limitation.

## Claim Discipline

One pilot is evidence for one generated harness on one task. Do not claim broad
adoption, production readiness, compliance, or long-term reliability from this
pack alone.
""".strip() + "\n"


def build_payload(args: argparse.Namespace) -> dict:
    harness = Path(args.harness).resolve()
    if not harness.is_dir():
        raise SystemExit(f"Harness path must be an existing directory: {harness}")
    if not (harness / "Docs" / "GETTING_STARTED.md").is_file():
        raise SystemExit(f"Missing generated getting started guide: {harness / 'Docs' / 'GETTING_STARTED.md'}")
    if not (harness / "scripts" / "record-task-trial.py").is_file():
        raise SystemExit(f"Missing task-trial recorder: {harness / 'scripts' / 'record-task-trial.py'}")
    if not (harness / "scripts" / "run-harness-evals.py").is_file():
        raise SystemExit(f"Missing copied-harness eval script: {harness / 'scripts' / 'run-harness-evals.py'}")
    if args.generation_path not in ALLOWED_GENERATION_PATHS:
        raise SystemExit(f"Unsupported generation path: {args.generation_path}")
    payload = {
        "generated_at": args.generated,
        "harness_label": args.harness_label or harness.name,
        "domain": args.domain,
        "source_type": args.source_type,
        "generation_path": args.generation_path,
        "profile": infer_profile(harness),
        "min_successes": args.min_successes,
        "slug": args.slug,
        "title": args.title,
    }
    if args.prefill_from_trials:
        payload["prefill"] = task_trial_prefill(harness)
    return payload


def write_outputs(args: argparse.Namespace, payload: dict) -> dict:
    out = Path(args.out) if args.out else Path(args.harness).resolve() / "Docs" / "Environment" / DEFAULT_PACK_NAME
    issue_out = Path(args.issue_out) if args.issue_out else None
    pack = build_pack(payload, issue_draft_name=issue_out.name if issue_out else None)
    issue = build_issue_draft(payload) if issue_out else ""
    findings = find_sensitive_text(pack + "\n" + issue + "\n" + json.dumps(payload, sort_keys=True))
    if findings:
        raise SystemExit("Refusing to write pilot pack with sensitive text: " + ", ".join(findings))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(pack, encoding="utf-8")
    result = {"status": "pass", **payload, "pack": out.as_posix()}
    if issue_out:
        issue_out.parent.mkdir(parents=True, exist_ok=True)
        issue_out.write_text(issue, encoding="utf-8")
        result["issue_draft"] = issue_out.as_posix()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", help="Generated harness directory")
    parser.add_argument("--out", help=f"Pilot pack path; defaults to Docs/Environment/{DEFAULT_PACK_NAME} inside the harness")
    parser.add_argument("--issue-out", help=f"Optional issue-body draft path, for example Docs/Environment/{DEFAULT_ISSUE_NAME}")
    parser.add_argument("--harness-label", help="Public-safe harness label; defaults to directory name")
    parser.add_argument("--domain", required=True, help="Public-safe usage domain")
    parser.add_argument("--slug", required=True, help="Suggested usage-record slug")
    parser.add_argument("--title", required=True, help="Suggested usage-record title")
    parser.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], default="external")
    parser.add_argument("--generation-path", choices=sorted(ALLOWED_GENERATION_PATHS), default="unknown")
    parser.add_argument("--min-successes", type=int, default=1)
    parser.add_argument("--prefill-from-trials", action="store_true", help="Prefill the issue draft from the latest complete task-trial record")
    parser.add_argument("--generated", default=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    result = write_outputs(args, payload)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("External pilot pack: PASS")
        print(f"- pack: {result['pack']}")
        if "issue_draft" in result:
            print(f"- issue draft: {result['issue_draft']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
