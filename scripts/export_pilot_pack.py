#!/usr/bin/env python3
"""Write a privacy-safe external pilot guide for a generated harness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from record_usage_case import ALLOWED_GENERATION_PATHS, find_sensitive_text


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
    return "not recorded"


def build_issue_draft(payload: dict) -> str:
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
            "_No response_",
            "",
            "### Public-safe task summary",
            "",
            "_No response_",
            "",
            "### Evidence",
            "",
            "- _No response_",
            "- _No response_",
            "",
            "### Verification performed",
            "",
            "- _No response_",
            "- _No response_",
            "",
            "### Privacy review",
            "",
            "Reporter confirmed the public summary excludes secrets, personal data, proprietary source, private repository names, local machine paths, email addresses, and raw private logs.",
            "",
            "### Limitations",
            "",
            "- One task in one generated harness; not longitudinal proof.",
        ]
    ).rstrip() + "\n"


def build_pack(payload: dict, include_issue_draft: bool) -> str:
    issue_line = ""
    if include_issue_draft:
        issue_line = "- Fill out `EXTERNAL_USAGE_ISSUE_DRAFT.md`, then paste it into the GitHub External usage report issue.\n"
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
python scripts/codex_harness.py usage-from-harness <generated-harness> --slug "{payload["slug"]}" --title "{payload["title"]}" --domain "{payload["domain"]}" --harness-label "{payload["harness_label"]}" --evidence-type private-summary --source-type {payload["source_type"]} --generation-path {payload["generation_path"]} --privacy-review "Reporter confirmed public-safe private-summary evidence only."
```

Or convert the GitHub issue body after review:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md --slug "{payload["slug"]}" --title "{payload["title"]}" --source-type {payload["source_type"]} --generation-path {payload["generation_path"]}
```

## Issue Draft

{issue_line}- Keep raw evidence private unless it is already safe for public release.
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
    return {
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


def write_outputs(args: argparse.Namespace, payload: dict) -> dict:
    out = Path(args.out) if args.out else Path(args.harness).resolve() / "Docs" / "Environment" / DEFAULT_PACK_NAME
    issue_out = Path(args.issue_out) if args.issue_out else None
    pack = build_pack(payload, include_issue_draft=issue_out is not None)
    issue = build_issue_draft(payload) if issue_out else ""
    findings = find_sensitive_text(pack + "\n" + issue)
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
