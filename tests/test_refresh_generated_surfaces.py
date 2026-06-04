import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REFRESH_PATH = REPO_ROOT / "scripts" / "refresh_generated_surfaces.py"
sys.path.insert(0, (REPO_ROOT / "scripts").as_posix())

spec = importlib.util.spec_from_file_location("refresh_generated_surfaces", REFRESH_PATH)
refresh_generated_surfaces = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = refresh_generated_surfaces
spec.loader.exec_module(refresh_generated_surfaces)


class RefreshGeneratedSurfacesTests(unittest.TestCase):
    def test_refreshes_fixture_surface_and_validates_inventory_contract(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir) / "fixtures"

            payload = refresh_generated_surfaces.build_payload(
                ("fixtures",),
                fixture_root,
                Path(temp_dir) / "deterministic",
                Path(temp_dir) / "create-acceptance",
                Path(temp_dir) / "brief-acceptance",
                "2026-06-04",
                "2026-06-04T12:00:00Z",
            )

            recorder = fixture_root / "software-dev-basic" / "scripts" / "record-task-trial.py"
            task_trials = fixture_root / "software-dev-basic" / "Docs" / "Environment" / "TASK_TRIALS.md"
            recorder_text = recorder.read_text(encoding="utf-8")
            task_trials_text = task_trials.read_text(encoding="utf-8")

            self.assertEqual("pass", payload["status"], payload)
            self.assertEqual("fixtures", payload["refreshed"][0]["surface"])
            self.assertEqual(5, payload["refreshed"][0]["count"])
            self.assertEqual(0, payload["inventory"]["failure_count"], payload)
            self.assertIn('parser.add_argument("--limitations", required=True', recorder_text)
            self.assertIn('parser.add_argument("--json", action="store_true"', recorder_text)
            self.assertIn("--limitations", task_trials_text)


if __name__ == "__main__":
    unittest.main()
