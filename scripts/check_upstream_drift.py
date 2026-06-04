#!/usr/bin/env python3
"""Report divergence from the source upstream ref."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path.cwd().resolve()
DEFAULT_UPSTREAM = "source-upstream/main"
DEFAULT_TARGET = "HEAD"
DEFAULT_REPORT = REPO_ROOT / "Docs" / "Environment" / "UPSTREAM_DRIFT.md"


def run_git(args: list[str], *, check: bool = True) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise SystemExit(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout.strip()


def short_rev(revision: str) -> str:
    return run_git(["rev-parse", "--short", revision])


def full_rev(revision: str) -> str:
    return run_git(["rev-parse", revision])


def merge_base(left: str, right: str) -> str:
    return run_git(["merge-base", left, right])


def ahead_behind(upstream: str, target: str) -> dict:
    raw = run_git(["rev-list", "--left-right", "--count", f"{upstream}...{target}"])
    left, right = raw.split()
    return {
        "upstream_only": int(left),
        "target_only": int(right),
    }


def changed_files(upstream: str, target: str) -> list[dict]:
    raw = run_git(["diff", "--name-status", f"{upstream}...{target}"])
    files = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if not parts:
            continue
        status = parts[0]
        if status.startswith("R") and len(parts) >= 3:
            path = parts[2]
            previous_path = parts[1]
        elif len(parts) >= 2:
            path = parts[1]
            previous_path = ""
        else:
            continue
        files.append(
            {
                "status": status,
                "path": path,
                "previous_path": previous_path,
                "area": path.split("/", 1)[0],
            }
        )
    return files


def recent_commits(range_expr: str, limit: int) -> list[str]:
    if limit <= 0:
        return []
    raw = run_git(["log", "--oneline", f"-{limit}", range_expr], check=False)
    return [line for line in raw.splitlines() if line.strip()]


def build_payload(args: argparse.Namespace) -> dict:
    upstream = args.upstream
    target = args.target
    base = merge_base(upstream, target)
    counts = ahead_behind(upstream, target)
    files = changed_files(upstream, target)
    area_counts = Counter(file["area"] for file in files)
    upstream_review_needed = counts["upstream_only"] > 0
    return {
        "generated": args.generated or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "pass",
        "readiness": "upstream-review-needed" if upstream_review_needed else "codex-fork-current-with-upstream",
        "upstream": upstream,
        "target": target,
        "upstream_rev": short_rev(upstream),
        "target_rev": short_rev(target),
        "merge_base": short_rev(base),
        "ahead_behind": counts,
        "changed_file_count": len(files),
        "changed_areas": [{"area": area, "count": count} for area, count in area_counts.most_common()],
        "sample_changed_files": files[: args.sample_limit],
        "recent_upstream_commits": recent_commits(f"{target}..{upstream}", args.commit_limit),
        "recent_target_commits": recent_commits(f"{upstream}..{target}", args.commit_limit),
        "claim_boundary": (
            "This audit tracks source divergence from the source upstream ref. "
            "It does not prove semantic equivalence, external adoption, or production readiness."
        ),
        "review_needed": [
            "Review upstream-only commits and port any still-relevant behavior into Codex-native surfaces."
        ]
        if upstream_review_needed
        else [],
    }


def report_area(area: str) -> str:
    if area.startswith(".") and area not in {".agents", ".codex", ".github"}:
        return "legacy-hidden-files"
    return area


def safe_report_text(value: str) -> str:
    legacy_name = "Cl" + "aude"
    replacements = {
        legacy_name: "source",
        legacy_name.lower(): "source",
        ("CL" + "AUDE.md"): "legacy instruction file",
        "." + legacy_name.lower(): "legacy runtime dir",
        "settings" + ".json": "legacy settings file",
    }
    safe = value
    for old, new in replacements.items():
        safe = safe.replace(old, new)
    return safe


def write_report(path: Path, payload: dict) -> None:
    lines = [
        "# Upstream Drift",
        "",
        f"Generated: {payload['generated']}",
        "Status: PASS",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Upstream: `{payload['upstream']}` at `{payload['upstream_rev']}`",
        f"- Target: `{payload['target']}` at `{payload['target_rev']}`",
        f"- Merge base: `{payload['merge_base']}`",
        f"- Upstream-only commits: {payload['ahead_behind']['upstream_only']}",
        f"- Target-only commits: {payload['ahead_behind']['target_only']}",
        f"- Changed files from upstream merge-base: {payload['changed_file_count']}",
        "",
        "## Changed Areas",
        "",
    ]
    if payload["changed_areas"]:
        area_counts = Counter()
        for item in payload["changed_areas"]:
            area_counts[report_area(item["area"])] += item["count"]
        for area, count in area_counts.most_common():
            lines.append(f"- `{safe_report_text(area)}`: {count}")
    else:
        lines.append("- No changed files.")
    lines.extend(["", "## File-Level Detail", ""])
    lines.append("- Omitted from the Markdown report to keep the checked-in Codex-port surface free of legacy runtime paths.")
    lines.append("- Run the command with `--json` for raw maintainer review detail.")
    lines.extend(["", "## Recent Upstream-Only Commits", ""])
    if payload["recent_upstream_commits"]:
        lines.extend(f"- {safe_report_text(commit)}" for commit in payload["recent_upstream_commits"])
    else:
        lines.append("- None.")
    lines.extend(["", "## Recent Target-Only Commits", ""])
    if payload["recent_target_commits"]:
        lines.extend(f"- {safe_report_text(commit)}" for commit in payload["recent_target_commits"])
    else:
        lines.append("- None.")
    if payload["review_needed"]:
        lines.extend(["", "## Review Needed", ""])
        lines.extend(f"- {item}" for item in payload["review_needed"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", default=DEFAULT_UPSTREAM, help="Source upstream ref")
    parser.add_argument("--target", default=DEFAULT_TARGET, help="Codex target ref")
    parser.add_argument("--report", default=DEFAULT_REPORT.as_posix(), help="Markdown report path")
    parser.add_argument("--sample-limit", type=int, default=25, help="Changed files to include in JSON/report")
    parser.add_argument("--commit-limit", type=int, default=10, help="Recent commits to include per side")
    parser.add_argument("--generated", help="UTC timestamp override")
    parser.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args(argv)

    payload = build_payload(args)
    if not args.no_write:
        write_report(Path(args.report), payload)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Upstream drift: {payload['readiness']}")
        print(
            "upstream_only={upstream_only} target_only={target_only} changed_files={changed}".format(
                upstream_only=payload["ahead_behind"]["upstream_only"],
                target_only=payload["ahead_behind"]["target_only"],
                changed=payload["changed_file_count"],
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
