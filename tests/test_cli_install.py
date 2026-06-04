import importlib.util
import json
import subprocess
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

        def fake_run(command, cwd=None):
            calls.append(command)
            stdout = ""
            if command[-2:] == ["profiles", "--json"]:
                stdout = json.dumps({"status": "pass", "profile_count": 20})
            if "usage-from-issue" in command and "--pilot-record-dir" in command:
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
        self.assertEqual(["create_venv", "install_package", "profiles", "doctor", "init", "quickstart", "demo_capture", "prepare_pilot", "validate", "inspect", "adoption_plan", "equivalence", "init_from_project", "record_task_trial", "local_eval", "public_usage_report", "evidence_packet", "pilot_pack", "usage_from_harness", "usage_from_issue_preview", "usage_from_issue", "prepare_next_pilot", "pilot_board", "pilot_update", "usage_from_issue_pilot_conversion", "usage_gaps", "beta_exit_audit", "pilot_campaign", "migration_audit", "eval"], names)
        self.assertTrue(any("pip" in command and "install" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "doctor" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "init" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "quickstart" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "demo-capture" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-pilot" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "validate" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "inspect" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "adoption-plan" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "equivalence" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "--blueprint-out" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "--copy-script" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "init" in command and "--from-project" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "local-eval" in command for command in calls))
        self.assertTrue(any("export-public-usage-report.py" in command[1] for command in calls if len(command) > 1))
        self.assertTrue(any("codex-harness" in command[0] and "evidence-packet" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-pack" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-harness" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command and "--no-write" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "prepare-next-pilot" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-board" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-update" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-from-issue" in command and "--pilot-record-dir" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "usage-gaps" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "beta-exit-audit" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "pilot-campaign" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "migration-audit" in command and "--report" in command for command in calls))
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


if __name__ == "__main__":
    unittest.main()
