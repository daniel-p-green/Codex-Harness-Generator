import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
TRIALS_PATH = REPO_ROOT / "scripts" / "run_live_example_task_trials.py"

spec = importlib.util.spec_from_file_location("run_live_example_task_trials", TRIALS_PATH)
run_live_example_task_trials = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = run_live_example_task_trials
spec.loader.exec_module(run_live_example_task_trials)


class LiveExampleTaskTrialTests(unittest.TestCase):
    def test_trial_specs_cover_checked_in_live_examples(self):
        examples = {trial.example for trial in run_live_example_task_trials.TRIALS}

        self.assertIn("synthetic-markdown-notes", examples)
        self.assertIn("synthetic-python-cli", examples)
        self.assertIn("synthetic-data-review", examples)
        self.assertIn("synthetic-security-audit", examples)
        self.assertIn("synthetic-legal-research", examples)

    def test_seed_and_verify_trial_output(self):
        trial = run_live_example_task_trials.selected_trials(["python-cli-todo-audit"])[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_live_example_task_trials.seed_trial(root, trial)
            output = root / trial.expected_file
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                "obsolete parser branch\nregression fixture\nsetup instructions\n",
                encoding="utf-8",
            )

            result = run_live_example_task_trials.verify_trial(root, trial)

        self.assertEqual("pass", result["status"], result)

    def test_run_codex_uses_non_interactive_exec(self):
        completed = subprocess.CompletedProcess(args=[], returncode=0, stdout="done\n", stderr="")
        with patch.object(run_live_example_task_trials.shutil, "which", return_value="/usr/local/bin/codex"):
            with patch.object(run_live_example_task_trials.subprocess, "run", return_value=completed) as run:
                result = run_live_example_task_trials.run_codex(
                    Path("/tmp/example-harness"),
                    "write the report",
                    timeout=60,
                    model="gpt-5.5-codex",
                )

        self.assertEqual(0, result["returncode"])
        command = run.call_args.args[0]
        self.assertEqual("/usr/local/bin/codex", command[0])
        self.assertEqual("exec", command[1])
        self.assertIn("--cd", command)
        self.assertIn("/tmp/example-harness", command)
        self.assertIn("--config", command)
        self.assertIn('approval_policy="never"', command)
        self.assertIn("--ephemeral", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)


if __name__ == "__main__":
    unittest.main()
