#!/usr/bin/env python3
"""Small command wrapper for common Codex Harness Generator workflows."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def python_script(script_name: str, args: list[str]) -> list[str]:
    return [sys.executable, f"scripts/{script_name}", *args]


def add_common_generation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("target", help="Target project directory")
    parser.add_argument("--profile", default="software-development", help="Starter profile")
    parser.add_argument("--project-name", help="Human-readable project name")
    parser.add_argument("--force", action="store_true", help="Replace target if it already contains files")


def build_command(args: argparse.Namespace) -> list[str]:
    if args.command == "init":
        if args.brief:
            command = [args.target, "--brief", args.brief]
            if args.project_name:
                command.extend(["--project-name", args.project_name])
            if args.notes:
                command.extend(["--notes", args.notes])
            if args.limit is not None:
                command.extend(["--limit", str(args.limit)])
            if args.allow_low_confidence:
                command.append("--allow-low-confidence")
            if args.target_label:
                command.extend(["--target-label", args.target_label])
            if args.force:
                command.append("--force")
            if args.json:
                command.append("--json")
            return python_script("run_brief_acceptance.py", command)

        command = [args.target, "--profile", args.profile]
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.force:
            command.append("--force")
        return python_script("generate_minimal_harness.py", command)

    if args.command == "profiles":
        if args.details or args.json:
            command = []
            if args.json:
                command.append("--json")
            return python_script("profile_catalog.py", command)
        return python_script("generate_minimal_harness.py", ["--list-profiles"])

    if args.command == "profile":
        command = ["--profile", args.profile]
        if args.json:
            command.append("--json")
        return python_script("profile_catalog.py", command)

    if args.command == "recommend":
        command = ["--recommend", args.brief]
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.json:
            command.append("--json")
        return python_script("profile_catalog.py", command)

    if args.command == "inspect":
        command = [args.path]
        if args.max_files is not None:
            command.extend(["--max-files", str(args.max_files)])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.json:
            command.append("--json")
        return python_script("inspect_project.py", command)

    if args.command == "generate":
        command = [args.target, "--profile", args.profile]
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.force:
            command.append("--force")
        return python_script("generate_minimal_harness.py", command)

    if args.command == "acceptance":
        command = [args.target, "--profile", args.profile]
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.project_type:
            command.extend(["--project-type", args.project_type])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.force:
            command.append("--force")
        return python_script("run_create_acceptance.py", command)

    if args.command == "brief-acceptance":
        command = [args.target, "--brief", args.brief]
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.allow_low_confidence:
            command.append("--allow-low-confidence")
        if args.target_label:
            command.extend(["--target-label", args.target_label])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("run_brief_acceptance.py", command)

    if args.command == "demo-capture":
        command = [args.target, "--brief", args.brief]
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.allow_low_confidence:
            command.append("--allow-low-confidence")
        if args.target_label:
            command.extend(["--target-label", args.target_label])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("run_demo_capture.py", command)

    if args.command == "eval":
        return python_script("eval_generated_harness.py", args.paths)

    if args.command == "smoke":
        command = list(args.paths)
        if args.codex_live:
            command.append("--codex-live")
        if args.prompt:
            command.extend(["--prompt", args.prompt])
        return python_script("smoke_generated_harness.py", command)

    if args.command == "validate":
        command = list(args.paths)
        if args.min_score is not None:
            command.extend(["--min-score", str(args.min_score)])
        if args.codex_live:
            command.append("--codex-live")
        if args.prompt:
            command.extend(["--prompt", args.prompt])
        if args.json:
            command.append("--json")
        return python_script("validate_generated_harness.py", command)

    if args.command == "local-eval":
        command = [(Path(args.path) / "scripts" / "run-harness-evals.py").as_posix()]
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return [sys.executable, *command]

    if args.command == "migration-audit":
        command = list(args.paths)
        if args.json:
            command.append("--json")
        return python_script("migration_audit.py", command)

    if args.command == "gate":
        command: list[str] = []
        if args.codex_live:
            command.append("--codex-live")
        if args.codex_live_profile:
            command.extend(["--codex-live-profile", args.codex_live_profile])
        return python_script("run_evals.py", command)

    if args.command == "live-trials":
        command = []
        if args.timeout is not None:
            command.extend(["--timeout", str(args.timeout)])
        if args.no_report:
            command.append("--no-report")
        return python_script("run_live_example_task_trials.py", command)

    if args.command == "source-freshness":
        command = []
        if args.timeout is not None:
            command.extend(["--timeout", str(args.timeout)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("check_source_freshness.py", command)

    if args.command == "semantic-alignment":
        command = []
        if args.timeout is not None:
            command.extend(["--timeout", str(args.timeout)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("check_semantic_alignment.py", command)

    if args.command == "usage-record":
        command = [
            "--slug",
            args.slug,
            "--title",
            args.title,
            "--domain",
            args.domain,
            "--harness-path",
            args.harness_path,
            "--task-summary",
            args.task_summary,
            "--outcome",
            args.outcome,
            "--evidence-type",
            args.evidence_type,
            "--privacy-review",
            args.privacy_review,
        ]
        for evidence in args.evidence:
            command.extend(["--evidence", evidence])
        for verification in args.verification:
            command.extend(["--verification", verification])
        for limitation in args.limitation:
            command.extend(["--limitation", limitation])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("record_usage_case.py", command)

    if args.command == "usage-from-harness":
        command = [
            args.harness,
            "--slug",
            args.slug,
            "--title",
            args.title,
            "--domain",
            args.domain,
            "--evidence-type",
            args.evidence_type,
            "--privacy-review",
            args.privacy_review,
        ]
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.task_summary:
            command.extend(["--task-summary", args.task_summary])
        if args.outcome:
            command.extend(["--outcome", args.outcome])
        for evidence in args.evidence:
            command.extend(["--evidence", evidence])
        for verification in args.verification:
            command.extend(["--verification", verification])
        for limitation in args.limitation:
            command.extend(["--limitation", limitation])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("usage_from_harness.py", command)

    if args.command == "usage-from-issue":
        command = [
            args.issue_body,
            "--slug",
            args.slug,
            "--title",
            args.title,
        ]
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("usage_from_issue.py", command)

    if args.command == "usage-validate":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.require_non_synthetic:
            command.append("--require-non-synthetic")
        if args.require_success:
            command.append("--require-success")
        if args.json:
            command.append("--json")
        return python_script("validate_usage_records.py", command)

    if args.command == "proof-status":
        command = []
        if args.min_live_trials is not None:
            command.extend(["--min-live-trials", str(args.min_live_trials)])
        if args.min_usage_records is not None:
            command.extend(["--min-usage-records", str(args.min_usage_records)])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("proof_status.py", command)

    if args.command == "doctor":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.min_usage_records is not None:
            command.extend(["--min-usage-records", str(args.min_usage_records)])
        if args.include_install_smoke:
            command.append("--include-install-smoke")
        if args.json:
            command.append("--json")
        return python_script("doctor.py", command)

    if args.command == "snapshot":
        return python_script("record_eval_snapshot.py", [])

    raise ValueError(f"Unsupported command: {args.command}")


def command_cwd(args: argparse.Namespace) -> Path:
    if args.command == "doctor" and (Path.cwd() / "scripts" / "doctor.py").is_file():
        return Path.cwd()
    return REPO_ROOT


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run common Codex Harness Generator workflows from one entry point.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Generate a starter harness from a brief or explicit profile")
    init.add_argument("target", help="Target project directory")
    init.add_argument("--brief", help="Short project brief; when present, recommends a profile and runs acceptance")
    init.add_argument("--profile", default="software-development", help="Starter profile used when --brief is omitted")
    init.add_argument("--project-name", help="Human-readable project name")
    init.add_argument("--notes", default="brief-based deterministic init", help="Notes for creation context when --brief is used")
    init.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record when --brief is used")
    init.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    init.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    init.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    init.add_argument("--json", action="store_true", help="Emit JSON payload when --brief is used")

    profiles = subparsers.add_parser("profiles", help="List deterministic starter profiles")
    profiles.add_argument("--details", action="store_true", help="Show profile descriptions, first tasks, and guardrails")
    profiles.add_argument("--json", action="store_true", help="Emit profile catalog JSON")

    profile = subparsers.add_parser("profile", help="Describe one deterministic starter profile")
    profile.add_argument("profile", help="Profile slug")
    profile.add_argument("--json", action="store_true", help="Emit profile JSON")

    recommend = subparsers.add_parser("recommend", help="Recommend deterministic starter profiles from a project brief")
    recommend.add_argument("brief", help="Short project brief")
    recommend.add_argument("--limit", type=int, default=3, help="Number of recommendations to show")
    recommend.add_argument("--json", action="store_true", help="Emit recommendation JSON")

    inspect = subparsers.add_parser("inspect", help="Inspect a local project and recommend starter profiles")
    inspect.add_argument("path", help="Project directory to inspect")
    inspect.add_argument("--max-files", type=int, default=800, help="Maximum files to scan before truncating")
    inspect.add_argument("--limit", type=int, default=3, help="Number of recommendations to show")
    inspect.add_argument("--json", action="store_true", help="Emit JSON payload")

    generate = subparsers.add_parser("generate", help="Generate a minimal deterministic harness")
    add_common_generation_args(generate)

    acceptance = subparsers.add_parser("acceptance", help="Run deterministic /create acceptance end to end")
    add_common_generation_args(acceptance)
    acceptance.add_argument("--project-type", default="not specified", help="Project type for creation context")
    acceptance.add_argument("--notes", default="none", help="Notes for creation context")

    brief_acceptance = subparsers.add_parser("brief-acceptance", help="Recommend a profile from a brief, then run deterministic acceptance")
    brief_acceptance.add_argument("target", help="Target project directory")
    brief_acceptance.add_argument("--brief", required=True, help="Short project brief")
    brief_acceptance.add_argument("--project-name", help="Human-readable project name")
    brief_acceptance.add_argument("--notes", default="brief-based deterministic acceptance", help="Notes for creation context")
    brief_acceptance.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    brief_acceptance.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    brief_acceptance.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    brief_acceptance.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    brief_acceptance.add_argument("--json", action="store_true", help="Emit JSON payload")

    demo_capture = subparsers.add_parser("demo-capture", help="Generate and validate a short public-safe demo capture")
    demo_capture.add_argument("target", help="Target project directory")
    demo_capture.add_argument("--brief", required=True, help="Short project brief")
    demo_capture.add_argument("--project-name", help="Human-readable project name")
    demo_capture.add_argument("--notes", default="short reproducible demo capture", help="Notes for creation context")
    demo_capture.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    demo_capture.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    demo_capture.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    demo_capture.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    demo_capture.add_argument("--json", action="store_true", help="Emit JSON payload")

    evaluate = subparsers.add_parser("eval", help="Evaluate generated harness directories")
    evaluate.add_argument("paths", nargs="+", help="Generated harness directory paths")

    smoke = subparsers.add_parser("smoke", help="Smoke-test generated harness directories")
    smoke.add_argument("paths", nargs="+", help="Generated harness directory paths")
    smoke.add_argument("--codex-live", action="store_true", help="Also run authenticated Codex CLI smoke")
    smoke.add_argument("--prompt", help="Prompt to use with --codex-live")

    validate = subparsers.add_parser("validate", help="Evaluate and smoke-test generated harness directories")
    validate.add_argument("paths", nargs="+", help="Generated harness directory paths")
    validate.add_argument("--min-score", type=int, help="Minimum passing eval score")
    validate.add_argument("--codex-live", action="store_true", help="Also run authenticated Codex CLI smoke")
    validate.add_argument("--prompt", help="Prompt to use with --codex-live")
    validate.add_argument("--json", action="store_true", help="Emit JSON payload")

    local_eval = subparsers.add_parser("local-eval", help="Run a generated harness's copied-local eval report")
    local_eval.add_argument("path", help="Generated harness directory path")
    local_eval.add_argument("--min-successes", type=int, help="Minimum passing task-trial successes required")
    local_eval.add_argument("--no-write", action="store_true", help="Do not rewrite Docs/Environment/EVAL_REPORT.md")
    local_eval.add_argument("--json", action="store_true", help="Emit JSON payload")

    migration_audit = subparsers.add_parser("migration-audit", help="Audit legacy harness directories for Codex migration work")
    migration_audit.add_argument("paths", nargs="+", help="Harness directories to audit")
    migration_audit.add_argument("--json", action="store_true", help="Emit JSON payload")

    gate = subparsers.add_parser("gate", help="Run the repo eval gate")
    gate.add_argument("--codex-live", action="store_true", help="Include authenticated Codex CLI live smoke")
    gate.add_argument("--codex-live-profile", help="Profile for --codex-live, or 'all'")

    live_trials = subparsers.add_parser("live-trials", help="Run live Codex task trials against checked-in examples")
    live_trials.add_argument("--timeout", type=int, help="Per-task Codex timeout in seconds")
    live_trials.add_argument("--no-report", action="store_true", help="Do not rewrite TASK_TRIALS.md")

    source_freshness = subparsers.add_parser("source-freshness", help="Check official OpenAI source URL reachability")
    source_freshness.add_argument("--timeout", type=int, help="HTTP timeout in seconds")
    source_freshness.add_argument("--no-write", action="store_true", help="Do not write JSON/report files")
    source_freshness.add_argument("--json", action="store_true", help="Emit JSON payload")

    semantic_alignment = subparsers.add_parser("semantic-alignment", help="Check local guidance against official Codex doc concepts")
    semantic_alignment.add_argument("--timeout", type=int, help="HTTP timeout in seconds")
    semantic_alignment.add_argument("--no-write", action="store_true", help="Do not write JSON/report files")
    semantic_alignment.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage = subparsers.add_parser("usage-record", help="Record sanitized generated-harness usage evidence")
    usage.add_argument("--slug", required=True, help="Stable record slug")
    usage.add_argument("--title", required=True, help="Short record title")
    usage.add_argument("--domain", required=True, help="Usage domain")
    usage.add_argument("--harness-path", required=True, help="Generated harness path or public label")
    usage.add_argument("--task-summary", required=True, help="Public-safe task summary")
    usage.add_argument("--outcome", choices=["failed", "inconclusive", "partial", "success"], required=True)
    usage.add_argument("--evidence-type", choices=["private-summary", "sanitized", "synthetic"], required=True)
    usage.add_argument("--evidence", action="append", required=True, help="Public-safe evidence item; repeatable")
    usage.add_argument("--verification", action="append", required=True, help="Verification item; repeatable")
    usage.add_argument("--privacy-review", required=True, help="Public-safe privacy review note")
    usage.add_argument("--limitation", action="append", default=[], help="Known limitation; repeatable")
    usage.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage.add_argument("--report", help="Usage-record Markdown report path")
    usage.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_from_harness = subparsers.add_parser("usage-from-harness", help="Create usage evidence from a generated harness's local reports")
    usage_from_harness.add_argument("harness", help="Generated harness directory")
    usage_from_harness.add_argument("--slug", required=True, help="Stable record slug")
    usage_from_harness.add_argument("--title", required=True, help="Short record title")
    usage_from_harness.add_argument("--domain", required=True, help="Usage domain")
    usage_from_harness.add_argument("--harness-label", help="Public-safe harness path label")
    usage_from_harness.add_argument("--task-summary", help="Public-safe task summary")
    usage_from_harness.add_argument("--outcome", choices=["failed", "inconclusive", "partial", "success"], help="Override derived outcome")
    usage_from_harness.add_argument("--evidence-type", choices=["private-summary", "sanitized", "synthetic"], required=True)
    usage_from_harness.add_argument("--evidence", action="append", default=[], help="Additional public-safe evidence item; repeatable")
    usage_from_harness.add_argument("--verification", action="append", default=[], help="Additional verification item; repeatable")
    usage_from_harness.add_argument("--privacy-review", required=True, help="Public-safe privacy review note")
    usage_from_harness.add_argument("--limitation", action="append", default=[], help="Additional limitation; repeatable")
    usage_from_harness.add_argument("--generated", help="UTC timestamp override")
    usage_from_harness.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage_from_harness.add_argument("--report", help="Usage-record Markdown report path")
    usage_from_harness.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage_from_harness.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_from_issue = subparsers.add_parser("usage-from-issue", help="Create usage evidence from a GitHub issue-form body")
    usage_from_issue.add_argument("issue_body", help="Markdown issue body path, or '-' for stdin")
    usage_from_issue.add_argument("--slug", required=True, help="Stable record slug")
    usage_from_issue.add_argument("--title", required=True, help="Short usage-record title")
    usage_from_issue.add_argument("--harness-label", help="Public-safe harness label override")
    usage_from_issue.add_argument("--generated", help="UTC timestamp override")
    usage_from_issue.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage_from_issue.add_argument("--report", help="Usage-record Markdown report path")
    usage_from_issue.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage_from_issue.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_validate = subparsers.add_parser("usage-validate", help="Validate checked-in generated-harness usage evidence")
    usage_validate.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    usage_validate.add_argument("--min-records", type=int, help="Fail unless at least this many valid records exist")
    usage_validate.add_argument("--require-non-synthetic", action="store_true", help="Fail unless sanitized or private-summary evidence exists")
    usage_validate.add_argument("--require-success", action="store_true", help="Fail unless at least one successful usage record exists")
    usage_validate.add_argument("--json", action="store_true", help="Emit JSON payload")

    proof_status = subparsers.add_parser("proof-status", help="Summarize checked-in product-proof readiness")
    proof_status.add_argument("--min-live-trials", type=int, help="Minimum passing live task trials required")
    proof_status.add_argument("--min-usage-records", type=int, help="Minimum valid usage records required")
    proof_status.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    proof_status.add_argument("--report", help="Proof-status Markdown report path")
    proof_status.add_argument("--no-write", action="store_true", help="Do not rewrite PROOF_STATUS.md")
    proof_status.add_argument("--json", action="store_true", help="Emit JSON payload")

    doctor = subparsers.add_parser("doctor", help="Run a fast local readiness check")
    doctor.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    doctor.add_argument("--min-usage-records", type=int, help="Minimum valid usage records required")
    doctor.add_argument("--include-install-smoke", action="store_true", help="Also run the slower non-editable CLI install smoke")
    doctor.add_argument("--json", action="store_true", help="Emit JSON payload")

    subparsers.add_parser("snapshot", help="Record an eval trend snapshot")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    command = build_command(args)
    completed = subprocess.run(command, cwd=command_cwd(args), check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
