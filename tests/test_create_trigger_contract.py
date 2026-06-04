import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "simulate_create_trigger.py"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_trigger(target: Path, *extra: str) -> tuple[dict, str]:
    completed = subprocess.run(
        [
            sys.executable,
            SCRIPT.as_posix(),
            target.as_posix(),
            "--created",
            "2026-06-04T12:00:00Z",
            "--json",
            *extra,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    payload = json.loads(completed.stdout)
    context = Path(payload["context_path"]).read_text(encoding="utf-8")
    return payload, context


class CreateTriggerContractTests(unittest.TestCase):
    def test_fresh_target_writes_creation_context(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "fresh-project"
            payload, context = run_trigger(target, "--project-type", "Python CLI", "--notes", "solo tool")

            self.assertEqual("CREATED_NEW", payload["directory_status"])
            self.assertEqual("NONE", payload["hub_status"])
            self.assertEqual("TRIGGER_COMPLETE", payload["pipeline_stage"])
            self.assertEqual("PROFILE_SELECTION", payload["next_step"])
            self.assertTrue((target / "Docs/Environment/CREATION_CONTEXT.md").is_file())
            self.assertIn("- Stated project type: Python CLI", context)
            self.assertIn("- Additional notes: solo tool", context)

    def test_existing_environment_is_recorded_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "existing-project"
            write(target / "AGENTS.md", "# Existing\n")
            write(target / ".codex/config.toml", 'model = "gpt-5.5"\n')

            payload, context = run_trigger(target)

            self.assertEqual("HAS_EXISTING_ENV", payload["directory_status"])
            self.assertEqual([".codex", "AGENTS.md"], payload["existing_files"])
            self.assertIn("- Existing files found: .codex, AGENTS.md", context)
            self.assertEqual("# Existing\n", (target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_hub_add_area_detection_records_hub_context(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            hub = Path(temp_dir) / "governance-hub"
            area = hub / "stakeholder-comms"
            write(
                hub / "Docs/Environment/HUB_GENESIS.md",
                """
# Hub Genesis

## Work Areas

- `policy`
- `training`
""",
            )

            payload, context = run_trigger(area)

            self.assertEqual("HUB_ADD_AREA", payload["hub_status"])
            self.assertEqual(hub.resolve().as_posix(), payload["hub_root"])
            self.assertEqual(["policy", "training"], payload["existing_area_slugs"])
            self.assertEqual("HUB_ADD_AREA_INTAKE", payload["next_step"])
            self.assertIn("- Hub root:", context)
            self.assertIn("- Existing area slugs: policy, training", context)

    def test_interrupted_generation_resumes_from_first_incomplete_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "interrupted"
            write(
                target / "Docs/Environment/GENERATION_PROGRESS.md",
                """
# Generation Progress

- Pass 1 Foundation: COMPLETE
- Pass 2 Agents: COMPLETE
- Pass 3 Skills: IN_PROGRESS
- Pass 4 Infrastructure: PENDING
""",
            )

            payload, context = run_trigger(target)

            self.assertEqual("RESUME_GENERATION", payload["pipeline_stage"])
            self.assertEqual("3", payload["resume_from_pass"])
            self.assertEqual("GENERATION_PASS_N", payload["next_step"])
            self.assertIn("- Resume From Pass: 3", context)
            self.assertIn("- Next: GENERATION_PASS_N", context)


if __name__ == "__main__":
    unittest.main()
