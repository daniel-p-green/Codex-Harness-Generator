import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_pack.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses" / "software-dev-basic"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_pack", SCRIPT)
export_pilot_pack = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_pack
spec.loader.exec_module(export_pilot_pack)


class ExternalPilotPackTests(unittest.TestCase):
    def base_args(self, temp_dir: Path, **overrides):
        values = {
            "harness": FIXTURE.as_posix(),
            "out": (temp_dir / "EXTERNAL_PILOT_PACK.md").as_posix(),
            "issue_out": (temp_dir / "EXTERNAL_USAGE_ISSUE_DRAFT.md").as_posix(),
            "harness_label": "public software-dev harness",
            "domain": "software development",
            "slug": "external-software-dev-pilot",
            "title": "External software-dev pilot",
            "source_type": "external",
            "generation_path": "installed-init-brief",
            "min_successes": 1,
            "prefill_from_trials": False,
            "generated": "2026-06-04T12:00:00Z",
        }
        values.update(overrides)
        return Namespace(**values)

    def test_writes_external_pilot_pack_and_issue_draft(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = self.base_args(Path(temp_dir))
            payload = export_pilot_pack.build_payload(args)
            result = export_pilot_pack.write_outputs(args, payload)

            pack = Path(result["pack"]).read_text(encoding="utf-8")
            issue = Path(result["issue_draft"]).read_text(encoding="utf-8")

        self.assertEqual("pass", result["status"])
        self.assertIn("# External Pilot Pack", pack)
        self.assertIn("Detected profile: not recorded", pack)
        self.assertIn("python scripts/check-harness.py", pack)
        self.assertIn("python scripts/record-task-trial.py", pack)
        self.assertIn("python scripts/run-harness-evals.py --min-successes 1", pack)
        self.assertIn("python scripts/codex_harness.py evidence-packet <generated-harness>", pack)
        self.assertIn("python scripts/codex_harness.py usage-from-harness <generated-harness>", pack)
        self.assertIn("--pilot-record-dir Docs/Environment/pilot-records", pack)
        self.assertIn("--pilot-board-report Docs/Environment/PILOT_BOARD.md", pack)
        self.assertIn("Fill out `EXTERNAL_USAGE_ISSUE_DRAFT.md`", pack)
        self.assertIn("Do not claim broad", pack)
        self.assertIn("adoption, production readiness", pack)
        self.assertIn("### Domain or project type", issue)
        self.assertIn("software development", issue)
        self.assertIn("private-summary", issue)
        self.assertIn("_No response_", issue)
        self.assertIn("One task in one generated harness", issue)

    def test_detects_profile_from_profile_selection_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            harness = temp_path / "harness"
            shutil.copytree(FIXTURE, harness)
            profile_selection = harness / "Docs" / "Environment" / "PROFILE_SELECTION.md"
            profile_selection.write_text(
                "# Profile Selection\n\n## Selected Profile\n\n- Profile: llm-app\n",
                encoding="utf-8",
            )
            args = self.base_args(temp_path, harness=harness.as_posix())
            payload = export_pilot_pack.build_payload(args)

        self.assertEqual("llm-app", payload["profile"])

    def test_pack_uses_custom_issue_draft_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            args = self.base_args(temp_path, issue_out=(temp_path / "LLM_APP_USAGE_ISSUE_DRAFT.md").as_posix())
            payload = export_pilot_pack.build_payload(args)
            result = export_pilot_pack.write_outputs(args, payload)

            pack = Path(result["pack"]).read_text(encoding="utf-8")

        self.assertIn("Fill out `LLM_APP_USAGE_ISSUE_DRAFT.md`", pack)

    def test_prefills_issue_draft_from_latest_complete_task_trial(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            harness = temp_path / "harness"
            shutil.copytree(FIXTURE, harness)
            task_trials = harness / "Docs" / "Environment" / "TASK_TRIALS.md"
            task_trials.write_text(
                task_trials.read_text(encoding="utf-8")
                + """
### 2026-06-04 - SUCCESS - summarize retry behavior

- Evidence: public-safe retry summary artifact
- Verification: python scripts/run-harness-evals.py
- Privacy review: public-safe summary only
- Harness helped: reviewer caught a missing verification note
- Limitations: one private-summary task, not longitudinal proof
""",
                encoding="utf-8",
            )
            args = self.base_args(temp_path, harness=harness.as_posix(), prefill_from_trials=True)
            payload = export_pilot_pack.build_payload(args)
            result = export_pilot_pack.write_outputs(args, payload)

            pack = Path(result["pack"]).read_text(encoding="utf-8")
            issue = Path(result["issue_draft"]).read_text(encoding="utf-8")

        self.assertIn("prefilled from the latest complete task-trial record", pack)
        self.assertIn("success", issue)
        self.assertIn("summarize retry behavior", issue)
        self.assertIn("public-safe retry summary artifact", issue)
        self.assertIn("Generated harness local eval report status: PASS.", issue)
        self.assertIn("python scripts/run-harness-evals.py", issue)
        self.assertIn("Copied-harness eval report was reviewed", issue)
        self.assertIn("one private-summary task, not longitudinal proof", issue)
        self.assertNotIn("_No response_", issue)

    def test_json_result_is_serializable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = self.base_args(Path(temp_dir), issue_out=None)
            payload = export_pilot_pack.build_payload(args)
            result = export_pilot_pack.write_outputs(args, payload)

        encoded = json.dumps(result, sort_keys=True)
        self.assertIn("external-software-dev-pilot", encoded)
        self.assertNotIn("issue_draft", result)

    def test_refuses_sensitive_public_label(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            args = self.base_args(Path(temp_dir), harness_label="owner@example.com")
            payload = export_pilot_pack.build_payload(args)
            with self.assertRaises(SystemExit) as raised:
                export_pilot_pack.write_outputs(args, payload)

        self.assertIn("sensitive text", str(raised.exception))

    def test_refuses_sensitive_prefill_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            harness = temp_path / "harness"
            shutil.copytree(FIXTURE, harness)
            task_trials = harness / "Docs" / "Environment" / "TASK_TRIALS.md"
            task_trials.write_text(
                task_trials.read_text(encoding="utf-8")
                + """
### 2026-06-04 - SUCCESS - summarize retry behavior

- Evidence: inspected /Users/example/private/retry.log
- Verification: python scripts/run-harness-evals.py
- Privacy review: public-safe summary only
- Harness helped: reviewer caught a missing verification note
- Limitations: one private-summary task, not longitudinal proof
""",
                encoding="utf-8",
            )
            args = self.base_args(temp_path, harness=harness.as_posix(), prefill_from_trials=True, issue_out=None)
            payload = export_pilot_pack.build_payload(args)

            with self.assertRaises(SystemExit) as raised:
                export_pilot_pack.write_outputs(args, payload)

        self.assertIn("sensitive text", str(raised.exception))

    def test_requires_generated_harness_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "empty"
            root.mkdir()
            args = self.base_args(Path(temp_dir), harness=root.as_posix())

            with self.assertRaises(SystemExit) as raised:
                export_pilot_pack.build_payload(args)

        self.assertIn("Missing generated getting started guide", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
