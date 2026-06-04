import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_PATH = REPO_ROOT / "scripts" / "check_example_inventory.py"
sys.path.insert(0, (REPO_ROOT / "scripts").as_posix())

spec = importlib.util.spec_from_file_location("check_example_inventory", CHECK_PATH)
check_example_inventory = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = check_example_inventory
spec.loader.exec_module(check_example_inventory)


class ExampleInventoryTests(unittest.TestCase):
    def test_checked_in_example_inventory_passes(self):
        completed = subprocess.run(
            [sys.executable, "scripts/check_example_inventory.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual(20, payload["profile_count"], payload)
        self.assertEqual(4, payload["brief_example_count"], payload)
        self.assertEqual(0, payload["failure_count"], payload)

    def test_inventory_rejects_partial_and_duplicate_profile_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "examples"
            profile = root / "software-development"
            profile.mkdir(parents=True)
            (profile / "AGENTS.md").write_text("# Partial\n", encoding="utf-8")
            (root / "software-development 2").mkdir()
            (root / "README 2.md").write_text("# Duplicate\n", encoding="utf-8")

            failures = check_example_inventory.check_root(
                root,
                ("software-development",),
                check_example_inventory.REQUIRED_HARNESS_PATHS,
            )

        checks = {failure.check for failure in failures}
        self.assertIn("duplicate_directory", checks)
        self.assertIn("profile_directory", checks)
        self.assertIn("root_entry", checks)
        self.assertIn("required_path", checks)


if __name__ == "__main__":
    unittest.main()
