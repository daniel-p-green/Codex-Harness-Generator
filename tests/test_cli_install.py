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
            return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

        with patch.object(check_cli_install, "run", side_effect=fake_run):
            payload = check_cli_install.build_payload()

        self.assertEqual("pass", payload["status"])
        names = [step["name"] for step in payload["steps"]]
        self.assertEqual(["create_venv", "install_package", "profiles", "init", "eval"], names)
        self.assertTrue(any("pip" in command and "install" in command for command in calls))
        self.assertTrue(any("codex-harness" in command[0] and "init" in command for command in calls))
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
