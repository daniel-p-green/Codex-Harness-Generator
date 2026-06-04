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
    if args.command == "profiles":
        return python_script("generate_minimal_harness.py", ["--list-profiles"])

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

    if args.command == "eval":
        return python_script("eval_generated_harness.py", args.paths)

    if args.command == "smoke":
        command = list(args.paths)
        if args.codex_live:
            command.append("--codex-live")
        if args.prompt:
            command.extend(["--prompt", args.prompt])
        return python_script("smoke_generated_harness.py", command)

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

    if args.command == "snapshot":
        return python_script("record_eval_snapshot.py", [])

    raise ValueError(f"Unsupported command: {args.command}")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run common Codex Harness Generator workflows from one entry point.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("profiles", help="List deterministic starter profiles")

    generate = subparsers.add_parser("generate", help="Generate a minimal deterministic harness")
    add_common_generation_args(generate)

    acceptance = subparsers.add_parser("acceptance", help="Run deterministic /create acceptance end to end")
    add_common_generation_args(acceptance)
    acceptance.add_argument("--project-type", default="not specified", help="Project type for creation context")
    acceptance.add_argument("--notes", default="none", help="Notes for creation context")

    evaluate = subparsers.add_parser("eval", help="Evaluate generated harness directories")
    evaluate.add_argument("paths", nargs="+", help="Generated harness directory paths")

    smoke = subparsers.add_parser("smoke", help="Smoke-test generated harness directories")
    smoke.add_argument("paths", nargs="+", help="Generated harness directory paths")
    smoke.add_argument("--codex-live", action="store_true", help="Also run authenticated Codex CLI smoke")
    smoke.add_argument("--prompt", help="Prompt to use with --codex-live")

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

    subparsers.add_parser("snapshot", help="Record an eval trend snapshot")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = make_parser()
    args = parser.parse_args(argv)
    command = build_command(args)
    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
