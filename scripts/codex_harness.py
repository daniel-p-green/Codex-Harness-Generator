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
        if args.from_project:
            command = [args.target, "--from-project", args.from_project]
            if args.project_name:
                command.extend(["--project-name", args.project_name])
            if args.notes:
                command.extend(["--notes", args.notes])
            if args.limit is not None:
                command.extend(["--limit", str(args.limit)])
            if args.max_files is not None:
                command.extend(["--max-files", str(args.max_files)])
            if args.allow_low_confidence:
                command.append("--allow-low-confidence")
            if args.target_label:
                command.extend(["--target-label", args.target_label])
            if args.source_label:
                command.extend(["--source-label", args.source_label])
            if args.force:
                command.append("--force")
            if args.json:
                command.append("--json")
            return python_script("run_inspected_acceptance.py", command)

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

    if args.command == "quickstart":
        command = [args.target]
        if args.brief:
            command.extend(["--brief", args.brief])
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
        if args.min_score is not None:
            command.extend(["--min-score", str(args.min_score)])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("run_quickstart.py", command)

    if args.command == "prepare-pilot":
        command = [args.target]
        if args.brief:
            command.extend(["--brief", args.brief])
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.notes:
            command.extend(["--notes", args.notes])
        command.extend(["--domain", args.domain])
        command.extend(["--slug", args.slug])
        command.extend(["--title", args.title])
        if args.source_type:
            command.extend(["--source-type", args.source_type])
        if args.generation_path:
            command.extend(["--generation-path", args.generation_path])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.out:
            command.extend(["--out", args.out])
        if args.issue_out:
            command.extend(["--issue-out", args.issue_out])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.min_score is not None:
            command.extend(["--min-score", str(args.min_score)])
        if args.target_label:
            command.extend(["--target-label", args.target_label])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.allow_low_confidence:
            command.append("--allow-low-confidence")
        if args.generated_date:
            command.extend(["--generated-date", args.generated_date])
        if args.created:
            command.extend(["--created", args.created])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_record_out:
            command.extend(["--pilot-record-out", args.pilot_record_out])
        if args.pilot_status:
            command.extend(["--pilot-status", args.pilot_status])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("prepare_pilot.py", command)

    if args.command == "prepare-next-pilot":
        command = []
        if args.target:
            command.append(args.target)
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.index is not None:
            command.extend(["--index", str(args.index)])
        if args.brief:
            command.extend(["--brief", args.brief])
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.domain:
            command.extend(["--domain", args.domain])
        if args.slug:
            command.extend(["--slug", args.slug])
        if args.title:
            command.extend(["--title", args.title])
        if args.source_type:
            command.extend(["--source-type", args.source_type])
        if args.generation_path:
            command.extend(["--generation-path", args.generation_path])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.out:
            command.extend(["--out", args.out])
        if args.issue_out:
            command.extend(["--issue-out", args.issue_out])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.min_score is not None:
            command.extend(["--min-score", str(args.min_score)])
        if args.target_label:
            command.extend(["--target-label", args.target_label])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.allow_low_confidence:
            command.append("--allow-low-confidence")
        if args.generated_date:
            command.extend(["--generated-date", args.generated_date])
        if args.created:
            command.extend(["--created", args.created])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_record_out:
            command.extend(["--pilot-record-out", args.pilot_record_out])
        if args.pilot_status:
            command.extend(["--pilot-status", args.pilot_status])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("prepare_next_pilot.py", command)

    if args.command == "prepare-pilot-batch":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.target_root:
            command.extend(["--target-root", args.target_root])
        if args.use_suggested_targets:
            command.append("--use-suggested-targets")
        if args.out_dir:
            command.extend(["--out-dir", args.out_dir])
        if args.max_pilots is not None:
            command.extend(["--max-pilots", str(args.max_pilots)])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.min_score is not None:
            command.extend(["--min-score", str(args.min_score)])
        if args.target_label:
            command.extend(["--target-label", args.target_label])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.allow_low_confidence:
            command.append("--allow-low-confidence")
        if args.generated_date:
            command.extend(["--generated-date", args.generated_date])
        if args.created:
            command.extend(["--created", args.created])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_status:
            command.extend(["--pilot-status", args.pilot_status])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.dry_run:
            command.append("--dry-run")
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("prepare_pilot_batch.py", command)

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

    if args.command == "adoption-plan":
        command = [args.project]
        if args.profile:
            command.extend(["--profile", args.profile])
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.harness:
            command.extend(["--harness", args.harness])
        if args.blueprint_out:
            command.extend(["--blueprint-out", args.blueprint_out])
        if args.force_blueprint:
            command.append("--force-blueprint")
        if args.max_files is not None:
            command.extend(["--max-files", str(args.max_files)])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.source_label:
            command.extend(["--source-label", args.source_label])
        if args.report:
            command.extend(["--report", args.report])
        if args.copy_script:
            command.extend(["--copy-script", args.copy_script])
        if args.json:
            command.append("--json")
        return python_script("plan_project_adoption.py", command)

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
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("migration_audit.py", command)

    if args.command == "prepare-migration":
        command = [args.source, args.output]
        if args.profile:
            command.extend(["--profile", args.profile])
        if args.project_name:
            command.extend(["--project-name", args.project_name])
        if args.source_label:
            command.extend(["--source-label", args.source_label])
        if args.max_files is not None:
            command.extend(["--max-files", str(args.max_files)])
        if args.limit is not None:
            command.extend(["--limit", str(args.limit)])
        if args.generated_date:
            command.extend(["--generated-date", args.generated_date])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.force:
            command.append("--force")
        if args.json:
            command.append("--json")
        return python_script("prepare_migration.py", command)

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

    if args.command == "equivalence":
        command = []
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("check_codex_equivalence.py", command)

    if args.command == "upstream-drift":
        command = []
        if args.upstream:
            command.extend(["--upstream", args.upstream])
        if args.target:
            command.extend(["--target", args.target])
        if args.report:
            command.extend(["--report", args.report])
        if args.sample_limit is not None:
            command.extend(["--sample-limit", str(args.sample_limit)])
        if args.commit_limit is not None:
            command.extend(["--commit-limit", str(args.commit_limit)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("check_upstream_drift.py", command)

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
            "--source-type",
            args.source_type,
            "--generation-path",
            args.generation_path,
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
        ]
        if args.title:
            command.extend(["--title", args.title])
        if args.domain:
            command.extend(["--domain", args.domain])
        if args.evidence_type:
            command.extend(["--evidence-type", args.evidence_type])
        if args.source_type:
            command.extend(["--source-type", args.source_type])
        if args.generation_path:
            command.extend(["--generation-path", args.generation_path])
        if args.privacy_review:
            command.extend(["--privacy-review", args.privacy_review])
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
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.force:
            command.append("--force")
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("usage_from_harness.py", command)

    if args.command == "evidence-packet":
        command = [args.harness]
        if args.out:
            command.extend(["--out", args.out])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.json:
            command.append("--json")
        return python_script("export_evidence_packet.py", command)

    if args.command == "pilot-pack":
        command = [
            args.harness,
            "--domain",
            args.domain,
            "--slug",
            args.slug,
            "--title",
            args.title,
            "--source-type",
            args.source_type,
            "--generation-path",
            args.generation_path,
        ]
        if args.out:
            command.extend(["--out", args.out])
        if args.issue_out:
            command.extend(["--issue-out", args.issue_out])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.min_successes is not None:
            command.extend(["--min-successes", str(args.min_successes)])
        if args.prefill_from_trials:
            command.append("--prefill-from-trials")
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.json:
            command.append("--json")
        return python_script("export_pilot_pack.py", command)

    if args.command == "pilot-campaign":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.out:
            command.extend(["--out", args.out])
        if args.max_pilots is not None:
            command.extend(["--max-pilots", str(args.max_pilots)])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("export_pilot_campaign.py", command)

    if args.command == "pilot-board":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("pilot_board.py", command)

    if args.command == "pilot-update":
        command = ["--update", args.slug, "--status", args.status]
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.notes:
            command.extend(["--notes", args.notes])
        if args.usage_record:
            command.extend(["--usage-record", args.usage_record])
        if args.updated:
            command.extend(["--updated", args.updated])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("pilot_board.py", command)

    if args.command == "pilot-outreach":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.usage_report:
            command.extend(["--usage-report", args.usage_report])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.out:
            command.extend(["--out", args.out])
        for status in args.status or []:
            command.extend(["--status", status])
        for slug in args.slug or []:
            command.extend(["--slug", slug])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("export_pilot_outreach.py", command)

    if args.command == "pilot-handoff":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.usage_report:
            command.extend(["--usage-report", args.usage_report])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.out:
            command.extend(["--out", args.out])
        for status in args.status or []:
            command.extend(["--status", status])
        for slug in args.slug or []:
            command.extend(["--slug", slug])
        if args.force:
            command.append("--force")
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("export_pilot_handoff.py", command)

    if args.command == "pilot-handoff-audit":
        command = []
        if args.handoff_dir:
            command.extend(["--handoff-dir", args.handoff_dir])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.usage_report:
            command.extend(["--usage-report", args.usage_report])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.report:
            command.extend(["--report", args.report])
        for status in args.status or []:
            command.extend(["--status", status])
        for slug in args.slug or []:
            command.extend(["--slug", slug])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("audit_pilot_handoffs.py", command)

    if args.command == "pilot-github-issues":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.usage_report:
            command.extend(["--usage-report", args.usage_report])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.out_dir:
            command.extend(["--out-dir", args.out_dir])
        if args.report:
            command.extend(["--report", args.report])
        for status in args.status or []:
            command.extend(["--status", status])
        for slug in args.slug or []:
            command.extend(["--slug", slug])
        for label in args.label or []:
            command.extend(["--label", label])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("export_pilot_github_issues.py", command)

    if args.command == "beta-exit-audit":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.usage_record_dir:
            command.extend(["--usage-record-dir", args.usage_record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("beta_exit_audit.py", command)

    if args.command == "usage-from-issue":
        command = [args.issue_body]
        if args.slug:
            command.extend(["--slug", args.slug])
        if args.title:
            command.extend(["--title", args.title])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.source_type:
            command.extend(["--source-type", args.source_type])
        if args.generation_path:
            command.extend(["--generation-path", args.generation_path])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.force:
            command.append("--force")
        if args.lint_only:
            command.append("--lint-only")
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("usage_from_issue.py", command)

    if args.command == "usage-from-github-issue":
        command = [args.issue]
        if args.repo:
            command.extend(["--repo", args.repo])
        if args.gh_bin:
            command.extend(["--gh-bin", args.gh_bin])
        if args.include_comments:
            command.append("--include-comments")
        if args.slug:
            command.extend(["--slug", args.slug])
        if args.title:
            command.extend(["--title", args.title])
        if args.harness_label:
            command.extend(["--harness-label", args.harness_label])
        if args.source_type:
            command.extend(["--source-type", args.source_type])
        if args.generation_path:
            command.extend(["--generation-path", args.generation_path])
        if args.generated:
            command.extend(["--generated", args.generated])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.pilot_notes:
            command.extend(["--pilot-notes", args.pilot_notes])
        if args.force:
            command.append("--force")
        if args.lint_only:
            command.append("--lint-only")
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("usage_from_github_issue.py", command)

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
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.json:
            command.append("--json")
        return python_script("validate_usage_records.py", command)

    if args.command == "usage-gaps":
        command = []
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("usage_gaps.py", command)

    if args.command == "proof-next":
        command = []
        if args.target:
            command.append(args.target)
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.pilot_record_dir:
            command.extend(["--pilot-record-dir", args.pilot_record_dir])
        if args.pilot_board_report:
            command.extend(["--pilot-board-report", args.pilot_board_report])
        if args.usage_report:
            command.extend(["--usage-report", args.usage_report])
        if args.pilot_handoff_out:
            command.extend(["--pilot-handoff-out", args.pilot_handoff_out])
        if args.pilot_github_issues_out:
            command.extend(["--pilot-github-issues-out", args.pilot_github_issues_out])
        if args.pilot_github_issues_report:
            command.extend(["--pilot-github-issues-report", args.pilot_github_issues_report])
        if args.pilot_pack_out:
            command.extend(["--pilot-pack-out", args.pilot_pack_out])
        if args.issue_out:
            command.extend(["--issue-out", args.issue_out])
        if args.report:
            command.extend(["--report", args.report])
        if args.min_records is not None:
            command.extend(["--min-records", str(args.min_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("proof_next.py", command)

    if args.command == "proof-status":
        command = []
        if args.beta_exit:
            command.append("--beta-exit")
        if args.min_live_trials is not None:
            command.extend(["--min-live-trials", str(args.min_live_trials)])
        if args.min_usage_records is not None:
            command.extend(["--min-usage-records", str(args.min_usage_records)])
        if args.min_external_or_multi_project is not None:
            command.extend(["--min-external-or-multi-project", str(args.min_external_or_multi_project)])
        if args.min_domains is not None:
            command.extend(["--min-domains", str(args.min_domains)])
        if args.min_installed_init_brief is not None:
            command.extend(["--min-installed-init-brief", str(args.min_installed_init_brief)])
        if args.record_dir:
            command.extend(["--record-dir", args.record_dir])
        if args.report:
            command.extend(["--report", args.report])
        if args.no_write:
            command.append("--no-write")
        if args.json:
            command.append("--json")
        return python_script("proof_status.py", command)

    if args.command == "refresh-examples":
        command = []
        for surface in args.surface or []:
            command.extend(["--surface", surface])
        if args.fixture_root:
            command.extend(["--fixture-root", args.fixture_root])
        if args.deterministic_root:
            command.extend(["--deterministic-root", args.deterministic_root])
        if args.create_acceptance_root:
            command.extend(["--create-acceptance-root", args.create_acceptance_root])
        if args.brief_acceptance_root:
            command.extend(["--brief-acceptance-root", args.brief_acceptance_root])
        if args.generated_date:
            command.extend(["--generated-date", args.generated_date])
        if args.created:
            command.extend(["--created", args.created])
        if args.json:
            command.append("--json")
        return python_script("refresh_generated_surfaces.py", command)

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
    checkout_audit_commands = {
        "doctor": "doctor.py",
        "equivalence": "check_codex_equivalence.py",
        "upstream-drift": "check_upstream_drift.py",
    }
    script_name = checkout_audit_commands.get(args.command)
    if script_name and (Path.cwd() / "scripts" / script_name).is_file():
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
    init.add_argument("--from-project", help="Inspect an existing project directory, then generate from inferred metadata")
    init.add_argument("--profile", default="software-development", help="Starter profile used when --brief is omitted")
    init.add_argument("--project-name", help="Human-readable project name")
    init.add_argument("--notes", default="brief-based deterministic init", help="Notes for creation context when --brief or --from-project is used")
    init.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record when --brief is used")
    init.add_argument("--max-files", type=int, default=800, help="Maximum source files to inspect before truncating with --from-project")
    init.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    init.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    init.add_argument("--source-label", help="Public-safe label for --from-project inspection report")
    init.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    init.add_argument("--json", action="store_true", help="Emit JSON payload when --brief or --from-project is used")

    profiles = subparsers.add_parser("profiles", help="List deterministic starter profiles")
    profiles.add_argument("--details", action="store_true", help="Show profile descriptions, first tasks, and guardrails")
    profiles.add_argument("--json", action="store_true", help="Emit profile catalog JSON")

    quickstart = subparsers.add_parser("quickstart", help="Generate, validate, and locally eval a starter harness")
    quickstart.add_argument("target", nargs="?", default="/tmp/codex-quickstart-harness", help="Generated harness target directory")
    quickstart.add_argument("--brief", default="RAG app with prompts, evals, and retrieval checks", help="Short project brief")
    quickstart.add_argument("--project-name", default="Quickstart Harness", help="Human-readable project name")
    quickstart.add_argument("--notes", default="quickstart path", help="Notes for creation context")
    quickstart.add_argument("--limit", type=int, default=3, help="Number of profile recommendations to record")
    quickstart.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    quickstart.add_argument("--target-label", help="Override the target path written inside CREATION_CONTEXT.md")
    quickstart.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    quickstart.add_argument("--min-score", type=int, default=90, help="Minimum validation score")
    quickstart.add_argument("--min-successes", type=int, default=0, help="Minimum success task trials expected by local eval")
    quickstart.add_argument("--no-write", action="store_true", help="Do not write QUICKSTART_REPORT.md")
    quickstart.add_argument("--json", action="store_true", help="Emit JSON payload")

    prepare_pilot = subparsers.add_parser("prepare-pilot", help="Generate a pilot harness and external evidence kit")
    prepare_pilot.add_argument("target", nargs="?", default="/tmp/codex-external-pilot", help="Generated pilot harness target directory")
    prepare_pilot.add_argument("--brief", help="Short pilot project brief")
    prepare_pilot.add_argument("--project-name", help="Human-readable project name")
    prepare_pilot.add_argument("--notes", help="Notes for creation context")
    prepare_pilot.add_argument("--domain", required=True, help="Public-safe usage domain")
    prepare_pilot.add_argument("--slug", required=True, help="Suggested usage-record slug")
    prepare_pilot.add_argument("--title", required=True, help="Suggested usage-record title")
    prepare_pilot.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Usage source type")
    prepare_pilot.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        help="Usage generation path",
    )
    prepare_pilot.add_argument("--harness-label", help="Public-safe harness label")
    prepare_pilot.add_argument("--out", help="Pilot pack path")
    prepare_pilot.add_argument("--issue-out", help="Issue-body draft path")
    prepare_pilot.add_argument("--min-successes", type=int, help="Minimum passing success task trials expected for the later pilot")
    prepare_pilot.add_argument("--min-score", type=int, help="Minimum generated harness validation score")
    prepare_pilot.add_argument("--target-label", help="Override target path written inside CREATION_CONTEXT.md")
    prepare_pilot.add_argument("--limit", type=int, help="Number of profile recommendations to record")
    prepare_pilot.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    prepare_pilot.add_argument("--generated-date", help="Stable generated date for generated docs")
    prepare_pilot.add_argument("--created", help="Stable created timestamp for CREATION_CONTEXT.md")
    prepare_pilot.add_argument("--generated", help="UTC timestamp for pilot pack metadata")
    prepare_pilot.add_argument("--pilot-record-dir", help="Optional directory where a prepared-pilot tracking record is written")
    prepare_pilot.add_argument("--pilot-record-out", help="Optional explicit prepared-pilot tracking record path")
    prepare_pilot.add_argument("--pilot-status", choices=["completed", "converted", "dropped", "invited", "prepared"], help="Status for optional pilot-board record")
    prepare_pilot.add_argument("--pilot-notes", help="Optional public-safe note for the pilot-board record")
    prepare_pilot.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    prepare_pilot.add_argument("--json", action="store_true", help="Emit JSON payload")

    prepare_next_pilot = subparsers.add_parser("prepare-next-pilot", help="Prepare the next pilot from usage evidence gaps")
    prepare_next_pilot.add_argument("target", nargs="?", help="Override generated pilot harness target directory")
    prepare_next_pilot.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    prepare_next_pilot.add_argument("--index", type=int, help="1-based suggested pilot index from usage-gaps")
    prepare_next_pilot.add_argument("--brief", help="Override selected pilot brief")
    prepare_next_pilot.add_argument("--project-name", help="Override selected pilot project name")
    prepare_next_pilot.add_argument("--notes", help="Notes for creation context")
    prepare_next_pilot.add_argument("--domain", help="Override selected pilot domain")
    prepare_next_pilot.add_argument("--slug", help="Override selected pilot usage-record slug")
    prepare_next_pilot.add_argument("--title", help="Override selected pilot usage-record title")
    prepare_next_pilot.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Override selected pilot source type")
    prepare_next_pilot.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        help="Override selected pilot generation path",
    )
    prepare_next_pilot.add_argument("--harness-label", help="Public-safe harness label")
    prepare_next_pilot.add_argument("--out", help="Pilot pack path")
    prepare_next_pilot.add_argument("--issue-out", help="Issue-body draft path")
    prepare_next_pilot.add_argument("--min-successes", type=int, help="Minimum passing success task trials expected for the later pilot")
    prepare_next_pilot.add_argument("--min-score", type=int, help="Minimum generated harness validation score")
    prepare_next_pilot.add_argument("--target-label", help="Override target path written inside CREATION_CONTEXT.md")
    prepare_next_pilot.add_argument("--limit", type=int, help="Number of profile recommendations to record")
    prepare_next_pilot.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    prepare_next_pilot.add_argument("--generated-date", help="Stable generated date for generated docs")
    prepare_next_pilot.add_argument("--created", help="Stable created timestamp for CREATION_CONTEXT.md")
    prepare_next_pilot.add_argument("--generated", help="UTC timestamp for pilot metadata")
    prepare_next_pilot.add_argument("--min-records", type=int, help="Target valid usage records")
    prepare_next_pilot.add_argument("--min-external-or-multi-project", type=int, help="Target external or multi-project records")
    prepare_next_pilot.add_argument("--min-domains", type=int, help="Target distinct domains")
    prepare_next_pilot.add_argument("--min-installed-init-brief", type=int, help="Target records generated via installed brief-based generation")
    prepare_next_pilot.add_argument("--pilot-record-dir", help="Optional directory where a prepared-pilot tracking record is written")
    prepare_next_pilot.add_argument("--pilot-record-out", help="Optional explicit prepared-pilot tracking record path")
    prepare_next_pilot.add_argument(
        "--pilot-status",
        choices=["completed", "converted", "dropped", "invited", "prepared"],
        help="Status for optional pilot-board record",
    )
    prepare_next_pilot.add_argument("--pilot-notes", help="Optional public-safe note for the pilot-board record")
    prepare_next_pilot.add_argument("--force", action="store_true", help="Replace target if it already contains files")
    prepare_next_pilot.add_argument("--json", action="store_true", help="Emit JSON payload")

    prepare_pilot_batch = subparsers.add_parser("prepare-pilot-batch", help="Prepare suggested beta-exit pilots as a batch")
    prepare_pilot_batch.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    prepare_pilot_batch.add_argument("--target-root", help="Directory where generated pilot harnesses are prepared")
    prepare_pilot_batch.add_argument("--use-suggested-targets", action="store_true", help="Use each suggested pilot's target path instead of --target-root")
    prepare_pilot_batch.add_argument("--out-dir", help="Optional directory for pilot packs and issue drafts")
    prepare_pilot_batch.add_argument("--max-pilots", type=int, help="Maximum suggested pilots to prepare; 0 means all")
    prepare_pilot_batch.add_argument("--notes", help="Notes for creation context")
    prepare_pilot_batch.add_argument("--min-successes", type=int, help="Minimum passing success task trials expected for later pilots")
    prepare_pilot_batch.add_argument("--min-score", type=int, help="Minimum generated harness validation score")
    prepare_pilot_batch.add_argument("--target-label", help="Override target label written inside generated creation contexts")
    prepare_pilot_batch.add_argument("--limit", type=int, help="Number of profile recommendations to record")
    prepare_pilot_batch.add_argument("--allow-low-confidence", action="store_true", help="Allow generation when no profile scores above zero")
    prepare_pilot_batch.add_argument("--generated-date", help="Stable generated date for generated docs")
    prepare_pilot_batch.add_argument("--created", help="Stable created timestamp for CREATION_CONTEXT.md")
    prepare_pilot_batch.add_argument("--generated", help="UTC timestamp for batch metadata")
    prepare_pilot_batch.add_argument("--min-records", type=int, help="Target valid usage records")
    prepare_pilot_batch.add_argument("--min-external-or-multi-project", type=int, help="Target external or multi-project records")
    prepare_pilot_batch.add_argument("--min-domains", type=int, help="Target distinct domains")
    prepare_pilot_batch.add_argument("--min-installed-init-brief", type=int, help="Target records generated via installed brief-based generation")
    prepare_pilot_batch.add_argument("--pilot-record-dir", help="Optional directory where prepared-pilot tracking records are written")
    prepare_pilot_batch.add_argument(
        "--pilot-status",
        choices=["completed", "converted", "dropped", "invited", "prepared"],
        help="Status for optional pilot-board records",
    )
    prepare_pilot_batch.add_argument("--pilot-notes", help="Optional public-safe note for pilot-board records")
    prepare_pilot_batch.add_argument("--dry-run", action="store_true", help="Only print the batch plan")
    prepare_pilot_batch.add_argument("--force", action="store_true", help="Replace generated targets and pilot records when they already exist")
    prepare_pilot_batch.add_argument("--json", action="store_true", help="Emit JSON payload")

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

    adoption_plan = subparsers.add_parser("adoption-plan", help="Plan non-destructive harness adoption for an existing project")
    adoption_plan.add_argument("project", help="Existing project directory")
    adoption_plan.add_argument("--profile", help="Starter profile override; defaults to inspection recommendation")
    adoption_plan.add_argument("--project-name", help="Project name for generated blueprint docs")
    adoption_plan.add_argument("--harness", help="Existing generated harness blueprint to compare")
    adoption_plan.add_argument("--blueprint-out", help="Persist the generated blueprint to this directory")
    adoption_plan.add_argument("--force-blueprint", action="store_true", help="Replace --blueprint-out when it already contains files")
    adoption_plan.add_argument("--max-files", type=int, default=800, help="Maximum files to inspect before truncating")
    adoption_plan.add_argument("--limit", type=int, default=3, help="Number of inspection recommendations to consider")
    adoption_plan.add_argument("--source-label", help="Public-safe project label")
    adoption_plan.add_argument("--report", help="Write a Markdown adoption plan to this path")
    adoption_plan.add_argument("--copy-script", help="Write an executable add-only copy script; requires --harness or --blueprint-out")
    adoption_plan.add_argument("--json", action="store_true", help="Emit JSON payload")

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
    migration_audit.add_argument("--report", help="Optional Markdown migration plan report path")
    migration_audit.add_argument("--no-write", action="store_true", help="Do not write --report")
    migration_audit.add_argument("--json", action="store_true", help="Emit JSON payload")

    prepare_migration = subparsers.add_parser(
        "prepare-migration",
        help="Prepare a Codex migration packet for a legacy harness",
    )
    prepare_migration.add_argument("source", help="Legacy harness or project directory")
    prepare_migration.add_argument("output", help="Output directory for the migration packet")
    prepare_migration.add_argument("--profile", help="Starter profile override; defaults to inspection recommendation")
    prepare_migration.add_argument("--project-name", help="Project name for generated blueprint docs")
    prepare_migration.add_argument("--source-label", help="Public-safe label for the source project")
    prepare_migration.add_argument("--max-files", type=int, help="Maximum source files to inspect")
    prepare_migration.add_argument("--limit", type=int, help="Number of inspection recommendations to consider")
    prepare_migration.add_argument("--generated-date", help="Stable generated date for blueprint docs")
    prepare_migration.add_argument("--generated", help="UTC timestamp for packet metadata")
    prepare_migration.add_argument("--force", action="store_true", help="Replace output directory contents")
    prepare_migration.add_argument("--json", action="store_true", help="Emit JSON payload")

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

    equivalence = subparsers.add_parser("equivalence", help="Check the Codex-native equivalence matrix")
    equivalence.add_argument("--report", help="Equivalence matrix Markdown report path")
    equivalence.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    equivalence.add_argument("--json", action="store_true", help="Emit JSON payload")

    upstream_drift = subparsers.add_parser("upstream-drift", help="Report divergence from the source upstream ref")
    upstream_drift.add_argument("--upstream", help="Source upstream ref")
    upstream_drift.add_argument("--target", help="Codex target ref")
    upstream_drift.add_argument("--report", help="Upstream drift Markdown report path")
    upstream_drift.add_argument("--sample-limit", type=int, help="Changed files to include in the report")
    upstream_drift.add_argument("--commit-limit", type=int, help="Recent commits to include per side")
    upstream_drift.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    upstream_drift.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage = subparsers.add_parser("usage-record", help="Record sanitized generated-harness usage evidence")
    usage.add_argument("--slug", required=True, help="Stable record slug")
    usage.add_argument("--title", required=True, help="Short record title")
    usage.add_argument("--domain", required=True, help="Usage domain")
    usage.add_argument("--harness-path", required=True, help="Generated harness path or public label")
    usage.add_argument("--task-summary", required=True, help="Public-safe task summary")
    usage.add_argument("--outcome", choices=["failed", "inconclusive", "partial", "success"], required=True)
    usage.add_argument("--evidence-type", choices=["private-summary", "sanitized", "synthetic"], required=True)
    usage.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], default="self-dogfood")
    usage.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        default="unknown",
    )
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
    usage_from_harness.add_argument("--title", help="Short record title; inferred from matching pilot record when available")
    usage_from_harness.add_argument("--domain", help="Usage domain; inferred from matching pilot record when available")
    usage_from_harness.add_argument("--harness-label", help="Public-safe harness path label")
    usage_from_harness.add_argument("--task-summary", help="Public-safe task summary")
    usage_from_harness.add_argument("--outcome", choices=["failed", "inconclusive", "partial", "success"], help="Override derived outcome")
    usage_from_harness.add_argument("--evidence-type", choices=["private-summary", "sanitized", "synthetic"])
    usage_from_harness.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Source type; inferred from matching pilot record when available")
    usage_from_harness.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        help="Generation path; inferred from matching pilot record when available",
    )
    usage_from_harness.add_argument("--evidence", action="append", default=[], help="Additional public-safe evidence item; repeatable")
    usage_from_harness.add_argument("--verification", action="append", default=[], help="Additional verification item; repeatable")
    usage_from_harness.add_argument("--privacy-review", help="Public-safe privacy review note")
    usage_from_harness.add_argument("--limitation", action="append", default=[], help="Additional limitation; repeatable")
    usage_from_harness.add_argument("--generated", help="UTC timestamp override")
    usage_from_harness.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage_from_harness.add_argument("--report", help="Usage-record Markdown report path")
    usage_from_harness.add_argument(
        "--pilot-record-dir",
        help="Optional pilot-board record directory; matching pilot slug is prevalidated before conversion",
    )
    usage_from_harness.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for linked conversion")
    usage_from_harness.add_argument("--pilot-notes", help="Public-safe note for linked pilot-board conversion")
    usage_from_harness.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage_from_harness.add_argument("--no-write", action="store_true", help="Validate and preview without writing files")
    usage_from_harness.add_argument("--json", action="store_true", help="Emit JSON payload")

    evidence_packet = subparsers.add_parser("evidence-packet", help="Export a public-safe evidence packet from a generated harness")
    evidence_packet.add_argument("harness", help="Generated harness directory")
    evidence_packet.add_argument("--out", help="Packet path; defaults inside the harness Docs/Environment directory")
    evidence_packet.add_argument("--harness-label", help="Public-safe harness label; defaults to directory name")
    evidence_packet.add_argument("--min-successes", type=int, default=0, help="Minimum passing success task trials expected")
    evidence_packet.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_pack = subparsers.add_parser("pilot-pack", help="Write an external pilot guide and optional issue-body draft")
    pilot_pack.add_argument("harness", help="Generated harness directory")
    pilot_pack.add_argument("--out", help="Pilot pack path; defaults inside the harness Docs/Environment directory")
    pilot_pack.add_argument("--issue-out", help="Optional GitHub issue-body draft path")
    pilot_pack.add_argument("--harness-label", help="Public-safe harness label; defaults to directory name")
    pilot_pack.add_argument("--domain", required=True, help="Public-safe usage domain")
    pilot_pack.add_argument("--slug", required=True, help="Suggested usage-record slug")
    pilot_pack.add_argument("--title", required=True, help="Suggested usage-record title")
    pilot_pack.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], default="external")
    pilot_pack.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        default="unknown",
    )
    pilot_pack.add_argument("--min-successes", type=int, default=1, help="Minimum passing success task trials expected")
    pilot_pack.add_argument("--prefill-from-trials", action="store_true", help="Prefill the issue draft from the latest complete task-trial record")
    pilot_pack.add_argument("--generated", help="UTC timestamp override")
    pilot_pack.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_campaign = subparsers.add_parser("pilot-campaign", help="Write a pilot campaign plan from usage evidence gaps")
    pilot_campaign.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    pilot_campaign.add_argument("--out", help="Pilot campaign Markdown path")
    pilot_campaign.add_argument("--max-pilots", type=int, help="Maximum suggested pilot slots to include")
    pilot_campaign.add_argument("--min-records", type=int, help="Target valid usage records")
    pilot_campaign.add_argument("--min-external-or-multi-project", type=int, help="Target external or multi-project records")
    pilot_campaign.add_argument("--min-domains", type=int, help="Target distinct domains")
    pilot_campaign.add_argument("--min-installed-init-brief", type=int, help="Target records generated via installed brief-based generation")
    pilot_campaign.add_argument("--no-write", action="store_true", help="Do not write the Markdown campaign")
    pilot_campaign.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_board = subparsers.add_parser("pilot-board", help="Summarize prepared pilot tracking records")
    pilot_board.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_board.add_argument("--usage-record-dir", help="Directory where converted usage record JSON files are read")
    pilot_board.add_argument("--report", help="Pilot board Markdown path")
    pilot_board.add_argument("--no-write", action="store_true", help="Do not write the Markdown board")
    pilot_board.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_update = subparsers.add_parser("pilot-update", help="Update one prepared pilot record and refresh the pilot board")
    pilot_update.add_argument("slug", help="Pilot record slug")
    pilot_update.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], required=True)
    pilot_update.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_update.add_argument("--usage-record-dir", help="Directory where converted usage record JSON files are read")
    pilot_update.add_argument("--report", help="Pilot board Markdown path")
    pilot_update.add_argument("--notes", help="Public-safe status update note")
    pilot_update.add_argument("--usage-record", help="Usage record slug or path required when --status converted")
    pilot_update.add_argument("--updated", help="UTC timestamp override")
    pilot_update.add_argument("--no-write", action="store_true", help="Do not write the Markdown board")
    pilot_update.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_outreach = subparsers.add_parser("pilot-outreach", help="Write reporter outreach copy from active pilot records")
    pilot_outreach.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_outreach.add_argument("--usage-record-dir", help="Directory where usage record JSON files are read")
    pilot_outreach.add_argument("--usage-report", help="Usage-record Markdown report path for conversion commands")
    pilot_outreach.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for tracking commands")
    pilot_outreach.add_argument("--out", help="Pilot outreach Markdown path")
    pilot_outreach.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], action="append", help="Pilot status to include; repeatable")
    pilot_outreach.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    pilot_outreach.add_argument("--no-write", action="store_true", help="Do not write the Markdown outreach packet")
    pilot_outreach.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_handoff = subparsers.add_parser("pilot-handoff", help="Write shareable handoff folders from active pilot records")
    pilot_handoff.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_handoff.add_argument("--usage-record-dir", help="Directory where usage record JSON files are read")
    pilot_handoff.add_argument("--usage-report", help="Usage-record Markdown report path for conversion commands")
    pilot_handoff.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for tracking commands")
    pilot_handoff.add_argument("--out", help="Output directory for handoff folders")
    pilot_handoff.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], action="append", help="Pilot status to include; repeatable")
    pilot_handoff.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    pilot_handoff.add_argument("--force", action="store_true", help="Replace output directory contents")
    pilot_handoff.add_argument("--no-write", action="store_true", help="Preview without writing handoff folders")
    pilot_handoff.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_handoff_audit = subparsers.add_parser("pilot-handoff-audit", help="Audit shareable handoff folders before sending")
    pilot_handoff_audit.add_argument("--handoff-dir", help="Pilot handoff folder root")
    pilot_handoff_audit.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_handoff_audit.add_argument("--usage-record-dir", help="Directory where usage record JSON files are read")
    pilot_handoff_audit.add_argument("--usage-report", help="Usage-record Markdown report path for conversion commands")
    pilot_handoff_audit.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for tracking commands")
    pilot_handoff_audit.add_argument("--report", help="Pilot handoff audit Markdown path")
    pilot_handoff_audit.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], action="append", help="Pilot status to include; repeatable")
    pilot_handoff_audit.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    pilot_handoff_audit.add_argument("--no-write", action="store_true", help="Do not write the Markdown audit")
    pilot_handoff_audit.add_argument("--json", action="store_true", help="Emit JSON payload")

    pilot_github_issues = subparsers.add_parser("pilot-github-issues", help="Write GitHub-ready issue bodies from active pilot records")
    pilot_github_issues.add_argument("--record-dir", help="Directory where prepared pilot JSON records are read")
    pilot_github_issues.add_argument("--usage-record-dir", help="Directory where usage record JSON files are read")
    pilot_github_issues.add_argument("--usage-report", help="Usage-record Markdown report path for conversion commands")
    pilot_github_issues.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for tracking commands")
    pilot_github_issues.add_argument("--out-dir", help="Directory for GitHub issue body files")
    pilot_github_issues.add_argument("--report", help="Markdown issue queue report path")
    pilot_github_issues.add_argument("--status", choices=["completed", "converted", "dropped", "invited", "prepared"], action="append", help="Pilot status to include; repeatable")
    pilot_github_issues.add_argument("--slug", action="append", help="Pilot slug to include; repeatable")
    pilot_github_issues.add_argument("--label", action="append", help="Optional GitHub label to include; repeatable")
    pilot_github_issues.add_argument("--no-write", action="store_true", help="Do not write issue bodies or report")
    pilot_github_issues.add_argument("--json", action="store_true", help="Emit JSON payload")

    beta_exit_audit = subparsers.add_parser("beta-exit-audit", help="Write a non-gating beta-exit readiness audit")
    beta_exit_audit.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    beta_exit_audit.add_argument("--pilot-record-dir", help="Directory where prepared pilot JSON records are read")
    beta_exit_audit.add_argument("--usage-record-dir", help="Directory where converted usage record JSON files are read")
    beta_exit_audit.add_argument("--report", help="Beta-exit audit Markdown path")
    beta_exit_audit.add_argument("--no-write", action="store_true", help="Do not write the Markdown audit")
    beta_exit_audit.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_from_issue = subparsers.add_parser("usage-from-issue", help="Create usage evidence from a GitHub issue-form body")
    usage_from_issue.add_argument("issue_body", help="Markdown issue body path, or '-' for stdin")
    usage_from_issue.add_argument("--slug", help="Stable record slug; inferred from issue body when omitted")
    usage_from_issue.add_argument("--title", help="Short usage-record title; inferred from matching pilot record when available")
    usage_from_issue.add_argument("--harness-label", help="Public-safe harness label override; inferred from matching pilot record when available")
    usage_from_issue.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Fallback source type; inferred from matching pilot record when available")
    usage_from_issue.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        help="Fallback generation path; inferred from matching pilot record when available",
    )
    usage_from_issue.add_argument("--generated", help="UTC timestamp override")
    usage_from_issue.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage_from_issue.add_argument("--report", help="Usage-record Markdown report path")
    usage_from_issue.add_argument(
        "--pilot-record-dir",
        help="Optional pilot-board record directory; matching pilot slug is prevalidated before conversion",
    )
    usage_from_issue.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for linked conversion")
    usage_from_issue.add_argument("--pilot-notes", help="Public-safe note for linked pilot-board conversion")
    usage_from_issue.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage_from_issue.add_argument("--lint-only", action="store_true", help="Check issue-body readiness without writing files")
    usage_from_issue.add_argument("--no-write", action="store_true", help="Validate and preview without writing files")
    usage_from_issue.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_from_github_issue = subparsers.add_parser("usage-from-github-issue", help="Create usage evidence from a GitHub issue fetched with gh")
    usage_from_github_issue.add_argument("issue", help="GitHub issue number, URL, or selector accepted by gh")
    usage_from_github_issue.add_argument("--repo", help="Optional GitHub repository in owner/name form")
    usage_from_github_issue.add_argument("--gh-bin", help="GitHub CLI executable")
    usage_from_github_issue.add_argument("--include-comments", action="store_true", help="Include issue comments when linting or converting")
    usage_from_github_issue.add_argument("--slug", help="Stable record slug; inferred from issue body when omitted")
    usage_from_github_issue.add_argument("--title", help="Short usage-record title; inferred from matching pilot record when available")
    usage_from_github_issue.add_argument("--harness-label", help="Public-safe harness label override; inferred from matching pilot record when available")
    usage_from_github_issue.add_argument("--source-type", choices=["external", "multi-project", "self-dogfood"], help="Fallback source type; inferred from matching pilot record when available")
    usage_from_github_issue.add_argument(
        "--generation-path",
        choices=[
            "adoption-plan",
            "installed-init-brief",
            "installed-init-from-project",
            "installed-quickstart",
            "live-create",
            "manual-migration",
            "repo-dogfood",
            "unknown",
        ],
        help="Fallback generation path; inferred from matching pilot record when available",
    )
    usage_from_github_issue.add_argument("--generated", help="UTC timestamp override")
    usage_from_github_issue.add_argument("--record-dir", help="Directory where usage record JSON files are written")
    usage_from_github_issue.add_argument("--report", help="Usage-record Markdown report path")
    usage_from_github_issue.add_argument(
        "--pilot-record-dir",
        help="Optional pilot-board record directory; matching pilot slug is prevalidated before conversion",
    )
    usage_from_github_issue.add_argument("--pilot-board-report", help="Pilot-board Markdown report path for linked conversion")
    usage_from_github_issue.add_argument("--pilot-notes", help="Public-safe note for linked pilot-board conversion")
    usage_from_github_issue.add_argument("--force", action="store_true", help="Replace existing record with same slug")
    usage_from_github_issue.add_argument("--lint-only", action="store_true", help="Check issue-body readiness without writing files")
    usage_from_github_issue.add_argument("--no-write", action="store_true", help="Validate and preview without writing files")
    usage_from_github_issue.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_validate = subparsers.add_parser("usage-validate", help="Validate checked-in generated-harness usage evidence")
    usage_validate.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    usage_validate.add_argument("--min-records", type=int, help="Fail unless at least this many valid records exist")
    usage_validate.add_argument("--require-non-synthetic", action="store_true", help="Fail unless sanitized or private-summary evidence exists")
    usage_validate.add_argument("--require-success", action="store_true", help="Fail unless at least one successful usage record exists")
    usage_validate.add_argument("--min-external-or-multi-project", type=int, help="Minimum external or multi-project usage records")
    usage_validate.add_argument("--min-domains", type=int, help="Minimum distinct usage domains")
    usage_validate.add_argument("--min-installed-init-brief", type=int, help="Minimum usage records generated via installed brief-based generation")
    usage_validate.add_argument("--json", action="store_true", help="Emit JSON payload")

    usage_gaps = subparsers.add_parser("usage-gaps", help="Report remaining beta-exit usage evidence gaps")
    usage_gaps.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    usage_gaps.add_argument("--report", help="Usage-gaps Markdown report path")
    usage_gaps.add_argument("--min-records", type=int, help="Target valid usage records")
    usage_gaps.add_argument("--min-external-or-multi-project", type=int, help="Target external or multi-project records")
    usage_gaps.add_argument("--min-domains", type=int, help="Target distinct domains")
    usage_gaps.add_argument("--min-installed-init-brief", type=int, help="Target records generated via installed brief-based generation")
    usage_gaps.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    usage_gaps.add_argument("--json", action="store_true", help="Emit JSON payload")

    proof_next = subparsers.add_parser("proof-next", help="Write the next beta-exit proof actions")
    proof_next.add_argument("target", nargs="?", help="Optional next pilot target directory")
    proof_next.add_argument("--record-dir", help="Usage record JSON directory")
    proof_next.add_argument("--pilot-record-dir", help="Prepared-pilot tracking directory")
    proof_next.add_argument("--pilot-board-report", help="Pilot board Markdown path")
    proof_next.add_argument("--usage-report", help="Usage records Markdown path")
    proof_next.add_argument("--pilot-handoff-out", help="Pilot handoff output directory")
    proof_next.add_argument("--pilot-github-issues-out", help="Pilot GitHub issue body output directory")
    proof_next.add_argument("--pilot-github-issues-report", help="Pilot GitHub issue queue report path")
    proof_next.add_argument("--pilot-pack-out", help="Pilot pack output path for the next prepare command")
    proof_next.add_argument("--issue-out", help="Issue draft output path for the next prepare command")
    proof_next.add_argument("--report", help="Proof-next Markdown path")
    proof_next.add_argument("--min-records", type=int, help="Target valid usage records")
    proof_next.add_argument("--min-external-or-multi-project", type=int, help="Target external or multi-project records")
    proof_next.add_argument("--min-domains", type=int, help="Target distinct domains")
    proof_next.add_argument("--min-installed-init-brief", type=int, help="Target records generated via installed brief-based generation")
    proof_next.add_argument("--no-write", action="store_true", help="Do not write the Markdown report")
    proof_next.add_argument("--json", action="store_true", help="Emit JSON payload")

    proof_status = subparsers.add_parser("proof-status", help="Summarize checked-in product-proof readiness")
    proof_status.add_argument("--beta-exit", action="store_true", help="Apply roadmap beta-exit thresholds")
    proof_status.add_argument("--min-live-trials", type=int, help="Minimum passing live task trials required")
    proof_status.add_argument("--min-usage-records", type=int, help="Minimum valid usage records required")
    proof_status.add_argument("--min-external-or-multi-project", type=int, help="Minimum external or multi-project usage records")
    proof_status.add_argument("--min-domains", type=int, help="Minimum distinct usage domains")
    proof_status.add_argument("--min-installed-init-brief", type=int, help="Minimum usage records generated via installed brief-based generation")
    proof_status.add_argument("--record-dir", help="Directory where usage record JSON files are read")
    proof_status.add_argument("--report", help="Proof-status Markdown report path")
    proof_status.add_argument("--no-write", action="store_true", help="Do not rewrite PROOF_STATUS.md")
    proof_status.add_argument("--json", action="store_true", help="Emit JSON payload")

    refresh_examples = subparsers.add_parser("refresh-examples", help="Refresh checked-in generated examples and fixtures")
    refresh_examples.add_argument(
        "--surface",
        action="append",
        choices=["fixtures", "deterministic", "create-acceptance", "brief-acceptance"],
        help="Surface to refresh; repeatable. Defaults to all.",
    )
    refresh_examples.add_argument("--fixture-root", help="Generated fixture root")
    refresh_examples.add_argument("--deterministic-root", help="Deterministic example root")
    refresh_examples.add_argument("--create-acceptance-root", help="Create-acceptance example root")
    refresh_examples.add_argument("--brief-acceptance-root", help="Brief-acceptance example root")
    refresh_examples.add_argument("--generated-date", help="Stable generated date")
    refresh_examples.add_argument("--created", help="Stable creation timestamp for acceptance examples")
    refresh_examples.add_argument("--json", action="store_true", help="Emit JSON payload")

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
    if args.command == "init" and args.brief and args.from_project:
        parser.error("init accepts either --brief or --from-project, not both")
    command = build_command(args)
    completed = subprocess.run(command, cwd=command_cwd(args), check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
