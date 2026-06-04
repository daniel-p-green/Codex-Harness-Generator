#!/usr/bin/env python3
"""Build shareable pilot handoff folders from active pilot-board records."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import export_pilot_outreach
from record_usage_case import find_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "Docs" / "Environment" / "pilot-handoffs"


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-").lower()
    return slug or "pilot"


def resolve_material_path(value: str) -> Path | None:
    text = str(value or "").strip()
    if not text or text == "not recorded":
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def ensure_output(path: Path, force: bool) -> None:
    if path.exists() and not path.is_dir():
        raise SystemExit(f"Output path exists and is not a directory: {path}")
    if path.exists() and any(path.iterdir()):
        if not force:
            raise SystemExit(f"Output directory is not empty. Re-run with --force to replace it: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def safe_write(path: Path, text: str) -> None:
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit(f"Refusing to write sensitive pilot handoff text to {path.as_posix()}: {', '.join(findings)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_material(source_text: str, destination: Path) -> dict:
    source = resolve_material_path(source_text)
    if source is None:
        return {"status": "missing", "source": source_text, "path": destination.as_posix(), "reason": "not recorded"}
    if not source.exists() or not source.is_file():
        return {"status": "missing", "source": source_text, "path": destination.as_posix(), "reason": "source file not found"}
    text = source.read_text(encoding="utf-8")
    findings = find_sensitive_text(text)
    if findings:
        raise SystemExit(f"Refusing to copy sensitive pilot material from {source.as_posix()}: {', '.join(findings)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    return {"status": "copied", "source": source_text, "path": destination.as_posix()}


def command_markdown(commands: dict) -> str:
    return "\n".join(
        [
            "# Maintainer Commands",
            "",
            "## Tracking",
            "",
            "```bash",
            commands["mark_invited"],
            commands["mark_completed"],
            "```",
            "",
            "## Issue-Body Conversion",
            "",
            "```bash",
            commands["lint_issue"],
            commands["preview_issue"],
            commands["convert_issue"],
            "```",
            "",
            "## Copied-Harness Conversion",
            "",
            "```bash",
            commands["preview_harness"],
            commands["convert_harness"],
            "```",
            "",
        ]
    )


def readme_markdown(record: dict, files: dict, payload: dict) -> str:
    missing = [name for name, item in files.items() if item["status"] != "copied"]
    lines = [
        f"# {record['title']} Handoff",
        "",
        f"Generated: {payload['generated']}",
        f"Pilot slug: `{record['slug']}`",
        f"Status: `{record['status']}`",
        f"Domain: {record['domain']}",
        f"Source type: `{record['source_type']}`",
        f"Generation path: `{record['generation_path']}`",
        "",
        "## Reporter Files",
        "",
        "- `REPORTER_MESSAGE.txt`: message to send with the pilot.",
        "- `PILOT_PACK.md`: one-task pilot guide, copied when available.",
        "- `USAGE_ISSUE_DRAFT.md`: issue-body evidence template, copied when available.",
        "",
        "## Maintainer Files",
        "",
        "- `MAINTAINER_COMMANDS.md`: tracking, preview, and conversion commands.",
        "",
        "## Claim Boundary",
        "",
        payload["claim_boundary"],
        "",
    ]
    if missing:
        lines.extend(
            [
                "## Missing Materials",
                "",
                "The handoff was prepared, but these source files were not copied:",
                "",
            ]
        )
        for name in missing:
            item = files[name]
            lines.append(f"- {name}: {item['reason']} (`{item['source']}`)")
        lines.append("")
    return "\n".join(lines)


def reporter_handoff_markdown(record: dict, files: dict, payload: dict, directory: Path) -> str:
    lines = [
        f"# {record['title']} Reporter Handoff",
        "",
        "## Message",
        "",
        record["reporter_message"],
        "",
        "## Pilot Pack",
        "",
    ]
    pilot_pack = files["pilot_pack"]
    if pilot_pack["status"] == "copied":
        lines.append((directory / "PILOT_PACK.md").read_text(encoding="utf-8").rstrip())
    else:
        lines.append(f"_Pilot pack not copied: {pilot_pack['reason']}._")
    lines.extend(["", "## Usage Issue Draft", ""])
    issue_draft = files["issue_draft"]
    if issue_draft["status"] == "copied":
        lines.append((directory / "USAGE_ISSUE_DRAFT.md").read_text(encoding="utf-8").rstrip())
    else:
        lines.append(f"_Usage issue draft not copied: {issue_draft['reason']}._")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            payload["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def build_outreach_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        record_dir=args.record_dir,
        usage_record_dir=args.usage_record_dir,
        usage_report=args.usage_report,
        pilot_board_report=args.pilot_board_report,
        out="",
        status=args.status,
        slug=args.slug,
    )


def build_payload(args: argparse.Namespace) -> dict:
    outreach = export_pilot_outreach.build_payload(build_outreach_args(args))
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": outreach["status"],
        "readiness": "handoff-ready" if outreach["records"] else "no-active-pilots",
        "out": args.out,
        "record_dir": args.record_dir,
        "usage_record_dir": args.usage_record_dir,
        "statuses": outreach["statuses"],
        "slugs": outreach["slugs"],
        "handoff_count": len(outreach["records"]),
        "records": [
            {
                "slug": record["slug"],
                "title": record["title"],
                "status": record["status"],
                "domain": record["domain"],
                "source_type": record["source_type"],
                "generation_path": record["generation_path"],
                "directory": (Path(args.out) / safe_slug(record["slug"])).as_posix(),
                "source_materials": {
                    "pilot_pack": record["pilot_pack"],
                    "issue_draft": record["issue_draft"],
                },
                "reporter_message": record["reporter_message"],
                "commands": record["commands"],
            }
            for record in outreach["records"]
        ],
        "pilot_board": outreach["pilot_board"],
        "claim_boundary": (
            "Pilot handoff folders help send and track pilots; they are not usage proof until a real task "
            "is completed and converted into a validated usage record."
        ),
    }


def write_handoff(output_root: Path, payload: dict, force: bool) -> None:
    ensure_output(output_root, force)
    index_lines = [
        "# Pilot Handoffs",
        "",
        f"Generated: {payload['generated']}",
        f"Status: {payload['status'].upper()}",
        f"Readiness: {payload['readiness']}",
        "",
        payload["claim_boundary"],
        "",
        "## Handoffs",
        "",
    ]
    if not payload["records"]:
        index_lines.append("- none")
    for record in payload["records"]:
        directory = output_root / safe_slug(record["slug"])
        files = {
            "pilot_pack": copy_material(record["source_materials"]["pilot_pack"], directory / "PILOT_PACK.md"),
            "issue_draft": copy_material(record["source_materials"]["issue_draft"], directory / "USAGE_ISSUE_DRAFT.md"),
        }
        safe_write(directory / "REPORTER_MESSAGE.txt", record["reporter_message"] + "\n")
        safe_write(directory / "MAINTAINER_COMMANDS.md", command_markdown(record["commands"]))
        safe_write(directory / "README.md", readme_markdown(record, files, payload))
        safe_write(directory / "REPORTER_HANDOFF.md", reporter_handoff_markdown(record, files, payload, directory))
        index_lines.append(f"- `{record['slug']}`: `{Path(record['directory']).name}/`")
        record["files"] = {
            "README.md": (directory / "README.md").as_posix(),
            "REPORTER_HANDOFF.md": (directory / "REPORTER_HANDOFF.md").as_posix(),
            "REPORTER_MESSAGE.txt": (directory / "REPORTER_MESSAGE.txt").as_posix(),
            "MAINTAINER_COMMANDS.md": (directory / "MAINTAINER_COMMANDS.md").as_posix(),
            "PILOT_PACK.md": files["pilot_pack"],
            "USAGE_ISSUE_DRAFT.md": files["issue_draft"],
        }
    safe_write(output_root / "README.md", "\n".join(index_lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-dir", default=export_pilot_outreach.DEFAULT_RECORD_DIR_TEXT)
    parser.add_argument("--usage-record-dir", default=export_pilot_outreach.DEFAULT_USAGE_RECORD_DIR_TEXT)
    parser.add_argument("--usage-report", default=export_pilot_outreach.DEFAULT_USAGE_REPORT_TEXT)
    parser.add_argument("--pilot-board-report", default=export_pilot_outreach.DEFAULT_PILOT_BOARD_REPORT_TEXT)
    parser.add_argument("--out", default=DEFAULT_OUT.as_posix(), help="Output directory for handoff folders")
    parser.add_argument("--status", action="append", choices=sorted(export_pilot_outreach.pilot_board.ALLOWED_STATUSES), help="Pilot status to include; repeatable")
    parser.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    parser.add_argument("--force", action="store_true", help="Replace output directory contents")
    parser.add_argument("--no-write", action="store_true", help="Preview without writing handoff folders")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(args)
    if not args.no_write:
        write_handoff(Path(args.out), payload, args.force)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Pilot handoff: {payload['readiness']}")
        print(f"- handoff folders: {payload['handoff_count']}")
        for record in payload["records"]:
            print(f"- {record['slug']}: {record['directory']}")
        print(f"- boundary: {payload['claim_boundary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
