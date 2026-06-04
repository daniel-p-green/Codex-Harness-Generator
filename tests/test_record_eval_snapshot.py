import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = REPO_ROOT / "scripts" / "record_eval_snapshot.py"

spec = importlib.util.spec_from_file_location("record_eval_snapshot", SNAPSHOT_PATH)
record_eval_snapshot = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = record_eval_snapshot
spec.loader.exec_module(record_eval_snapshot)


class RecordEvalSnapshotTests(unittest.TestCase):
    def test_summary_counts_steps(self):
        payload = {
            "status": "pass",
            "returncode": 0,
            "steps": [
                {"name": "one", "status": "pass", "returncode": 0},
                {"name": "two", "status": "fail", "returncode": 1},
            ],
        }

        summary = record_eval_snapshot.summarize(payload, "2026-06-04T04:15:00Z", "offline")

        self.assertEqual("pass", summary["status"])
        self.assertEqual(2, summary["step_count"])
        self.assertEqual(1, summary["passed"])
        self.assertEqual(1, summary["failed"])

    def test_writes_snapshot_and_report(self):
        summary = {
            "generated": "2026-06-04T04:15:00Z",
            "label": "offline",
            "status": "pass",
            "returncode": 0,
            "step_count": 1,
            "passed": 1,
            "failed": 0,
            "steps": [{"name": "static", "status": "pass", "returncode": 0}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            snapshot = record_eval_snapshot.write_snapshot(root / "history", summary)
            loaded = record_eval_snapshot.load_snapshots(root / "history")
            report = root / "EVAL_TRENDS.md"
            record_eval_snapshot.write_report(report, loaded)

            self.assertTrue(snapshot.is_file())
            self.assertEqual(summary, json.loads(snapshot.read_text(encoding="utf-8")))
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("| 2026-06-04T04:15:00Z | `offline` | PASS | 1 | 0 | 1 |", report_text)


if __name__ == "__main__":
    unittest.main()
