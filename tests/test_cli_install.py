import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_CLI_INSTALL_PATH = REPO_ROOT / "scripts" / "check_cli_install.py"

spec = importlib.util.spec_from_file_location("check_cli_install", CHECK_CLI_INSTALL_PATH)
check_cli_install = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(check_cli_install)


class CheckCliInstallTests(unittest.TestCase):
    def test_build_payload_smokes_install_init_and_eval(self):
        calls = []
        run_cwds = []

        def fake_run(command, cwd=None):
            calls.append(command)
            run_cwds.append((command, cwd))
            stdout = ""
            if command[-2:] == ["profiles", "--json"]:
                stdout = json.dumps({"status": "pass", "profile_count": 20})
            if "prepare-pilot" in command:
                pilot_record_out = command[command.index("--pilot-record-out") + 1]
                Path(pilot_record_out).parent.mkdir(parents=True, exist_ok=True)
                Path(pilot_record_out).write_text('{"status": "prepared"}\n', encoding="utf-8")
                stdout = json.dumps({"status": "pass", "pilot_record": {"status": "pass", "path": pilot_record_out}})
            if "usage-from-issue" in command and "--lint-only" in command:
                stdout = json.dumps({"status": "pass", "readiness": "conversion-ready"})
            elif "prepare-pilot-batch" in command:
                stdout = json.dumps({"status": "pass", "mode": "dry-run", "selected_count": 2})
            elif "pilot-outreach" in command:
                stdout = json.dumps({"status": "pass", "readiness": "outreach-ready", "outreach_count": 1})
            elif "pilot-handoff" in command:
                output = Path(command[command.index("--out") + 1])
                (output / "llm-app-pilot").mkdir(parents=True, exist_ok=True)
                (output / "llm-app-pilot" / "README.md").write_text("# LLM app pilot Handoff\n", encoding="utf-8")
                (output / "llm-app-pilot" / "REPORTER_HANDOFF.md").write_text("# Reporter Handoff\n", encoding="utf-8")
                (output / "llm-app-pilot" / "USAGE_REPORT_DRAFT.md").write_text("### Evidence\n\n_no response_\n", encoding="utf-8")
                stdout = json.dumps({"status": "pass", "readiness": "handoff-ready", "handoff_count": 1})
            elif "pilot-handoff-audit" in command:
                report = Path(command[command.index("--report") + 1])
                report.write_text("# Pilot Handoff Audit\n", encoding="utf-8")
                stdout = json.dumps({"status": "pass", "readiness": "handoff-audit-ready", "handoff_count": 1})
            elif "pilot-reporter-replies" in command:
                output = Path(command[command.index("--out-dir") + 1])
                report = Path(command[command.index("--report") + 1])
                output.mkdir(parents=True, exist_ok=True)
                (output / "llm-app-pilot-reporter-reply.md").write_text("# Reporter Completion Reply\n", encoding="utf-8")
                report.write_text("# Pilot Reporter Replies\n", encoding="utf-8")
                stdout = json.dumps({"status": "pass", "readiness": "reporter-replies-ready", "reply_count": 1})
            elif "pilot-github-sync" in command:
                stdout = json.dumps(
                    {
                        "status": "pass",
                        "readiness": "conversion-ready",
                        "summary": {"conversion_ready": 1, "waiting_for_reporter": 0},
                    }
                )
            elif "pilot-next-action" in command:
                stdout = json.dumps(
                    {
                        "status": "pass",
                        "readiness": "conversion-ready",
                        "next_action": {"type": "preview-conversion"},
                    }
                )
            elif "upstream-drift" in command:
                stdout = json.dumps({"status": "pass", "ahead_behind": {"upstream_only": 0, "target_only": 0}})
            elif "prepare-migration" in command:
                output = Path(command[command.index("prepare-migration") + 2])
                output.mkdir(parents=True, exist_ok=True)
                (output / "README.md").write_text("# Codex Migration Packet\n", encoding="utf-8")
                (output / "copy-codex-harness-adds.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
                stdout = json.dumps({"status": "pass", "output": output.as_posix()})
            elif "usage-from-issue" in command and "--pilot-record-dir" in command:
                stdout = json.dumps(
                    {
                        "status": "pass",
                        "pilot_update": {
                            "status": "pass",
                            "board_status": "pass",
                            "record": {"status": "converted", "usage_record": "llm-app-pilot"},
                        },
                    }
                )
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        with patch.object(check_cli_install, "run", side_effect=fake_run):
            payload = check_cli_install.build_payload()

        self.assertEqual("pass", payload["status"])
        names = [step["name"] for step in payload["steps"]]
        self.assertEqual(["create_venv", "install_package", "profiles", "init", "quickstart", "demo_capture", "prepare_pilot", "validate", "inspect", "adoption_plan", "equivalence", "upstream_drift", "init_from_project", "record_task_trial", "local_eval", "public_usage_report", "evidence_packet", "pilot_pack", "usage_from_harness", "usage_from_issue_lint", "usage_from_issue_preview", "usage_from_issue", "doctor", "prepare_next_pilot", "prepare_pilot_batch_dry_run", "pilot_board", "pilot_update", "pilot_outreach", "pilot_handoff", "pilot_handoff_audit", "pilot_github_issues", "pilot_reporter_replies", "pilot_github_sync", "pilot_next_action", "usage_from_issue_pilot_conversion", "usage_from_github_issue_lint", "usage_gaps", "beta_exit_audit", "beta_status", "pilot_campaign", "proof_next", "migration_audit", "prepare_migration", "eval"], names)
        self.assertTrue(any("pip" in command and "install" in command for command in calls))
        create_venv_call = next(command for command in calls if command[0:3] == [sys.executable, "-m", "venv"])
        self.assertNotIn("--system-site-packages", create_venv_call)
        install_call = next(command for command in calls if "pip" in command and "install" in command)
        self.assertNotIn("--no-build-isolation", install_call)
        self.assertNotIn("--no-deps", install_call)
        self.assertEqual(".", install_call[-1])
        install_cwds = [cwd for command, cwd in run_cwds if "pip" in command and "install" in command]
        self.assertEqual(1, len(install_cwds))
        self.assertIsNotNone(install_cwds[0])
        self.assertNotEqual(REPO_ROOT, install_cwds[0])
        install_step = next(step for step in payload["steps"] if step["name"] == "install_package")
        self.assertEqual(install_cwds[0].as_posix(), install_step["cwd"])
        non_install_cwds = [cwd for command, cwd in run_cwds if "pip" not in command or "install" not in command]
        self.assertTrue(non_install_cwds)
        self.assertTrue(all(cwd is not None for cwd in non_install_cwds))
        doctor_step = next(step for step in payload["steps"] if step["name"] == "doctor")
        equivalence_step = next(step for step in payload["steps"] if step["name"] == "equivalence")
        upstream_step = next(step for step in payload["steps"] if step["name"] == "upstream_drift")
        self.assertNotEqual(REPO_ROOT.as_posix(), doctor_step["cwd"])
        self.assertNotEqual(REPO_ROOT.as_posix(), equivalence_step["cwd"])
        self.assertEqual(REPO_ROOT.as_posix(), upstream_step["cwd"])
        self.assertTrue(any("codex-harness" in command[0] and "doctor" in command for command in calls))
        doctor_call = next(command for command in calls if "codex-harness" in command[0] and "doctor" in command)
        self.assertNotIn((REPO_ROOT / "Docs" / "Environment" / "usage-records").as_posix(), doctor_call)
        self.assertTrue(any("codex-harness" in command[0] and "init" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "quickstart" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "demo-capture" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-pilot" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-pilot" in command and "--pilot-record-out" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "validate" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "inspect" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "adoption-plan" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "equivalence" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "upstream-drift" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "--blueprint-out" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "--copy-script" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "init" in command and "--from-project" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "local-eval" in command for command in calls))
        self.assertTrue(any("export-public-usage-report.py" in command[1] for command in calls if len(command) > 1))
        self.assertTrue(any("codex-harness" in command[0] and "evidence-packet" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-reporter-replies" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-pack" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-harness" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command and "--lint-only" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command and "--no-write" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-next-pilot" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-pilot-batch" in command and "--dry-run" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-board" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-update" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-outreach" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-handoff" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-handoff-audit" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-github-issues" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-github-sync" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-next-action" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command and "--pilot-record-dir" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-github-issue" in command and "--lint-only" in command for command in calls))
        linked_issue_calls = [
            command
            for command in calls
            if "codex-harness" in command[0]
            and "usage-from-issue" in command
            and "--pilot-record-dir" in command
        ]
        self.assertTrue(any("--slug" not in command for command in linked_issue_calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-gaps" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "beta-exit-audit" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "beta-status" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-campaign" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "proof-next" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "migration-audit" in command and "--report" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-migration" in command for command in calls))
        self.assertTrue(any("--brief" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "eval" in command for command in calls))

    def test_profile_count_mismatch_fails(self):
        def fake_run(command, cwd=None):
            stdout = json.dumps({"status": "pass", "profile_count": 19}) if command[-2:] == ["profiles", "--json"] else ""
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        with patch.object(check_cli_install, "run", side_effect=fake_run):
            payload = check_cli_install.build_payload()

        self.assertEqual("fail", payload["status"])
        self.assertEqual("profiles", payload["steps"][-1]["name"])

    def test_copy_install_source_uses_public_package_files_without_repo_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "source"

            check_cli_install.copy_install_source(destination)

            self.assertTrue((destination / "pyproject.toml").exists())
            self.assertTrue((destination / "scripts" / "codex_harness.py").exists())
            self.assertFalse((destination / ".git").exists())
            self.assertFalse((destination / "build").exists())
            self.assertFalse((destination / "dist").exists())


if __name__ == "__main__":
    unittest.main()
