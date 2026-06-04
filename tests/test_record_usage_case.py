import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
USAGE_PATH = REPO_ROOT / "scripts" / "record_usage_case.py"

spec = importlib.util.spec_from_file_location("record_usage_case", USAGE_PATH)
record_usage_case = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = record_usage_case
spec.loader.exec_module(record_usage_case)


class RecordUsageCaseTests(unittest.TestCase):
    def make_record(self, **overrides):
        payload = {
            "slug": "synthetic-task",
            "title": "Synthetic task",
            "generated": "2026-06-04T12:00:00Z",
            "domain": "software development",
            "harness_path": "examples/live-create/synthetic-python-cli",
            "task_summary": "Used a generated harness to summarize public-safe TODO notes.",
            "outcome": "success",
            "evidence_type": "synthetic",
            "evidence": ("reports/todo-audit.md produced",),
            "verification": ("expected terms found",),
            "privacy_review": "Synthetic inputs only; no personal data or secrets.",
            "limitations": ("Single small task.",),
        }
        payload.update(overrides)
        return record_usage_case.UsageRecord(**payload)

    def test_safe_slug_normalizes_text(self):
        self.assertEqual("my-usage-record", record_usage_case.safe_slug("My Usage Record!"))

    def test_validate_record_rejects_sensitive_text(self):
        record = self.make_record(evidence=("api_key=supersecretvalue",))

        with self.assertRaises(SystemExit):
            record_usage_case.validate_record(record)

    def test_write_record_and_report(self):
        record = self.make_record()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = record_usage_case.write_record(root / "usage-records", record)
            records = record_usage_case.load_records(root / "usage-records")
            report = root / "USAGE_RECORDS.md"
            record_usage_case.write_report(report, records)

            self.assertTrue(path.is_file())
            self.assertEqual(record.to_dict(), json.loads(path.read_text(encoding="utf-8")))
            text = report.read_text(encoding="utf-8")
            self.assertIn("synthetic-task", text)
            self.assertIn("software development", text)

    def test_write_record_requires_force_for_existing_slug(self):
        record = self.make_record()

        with tempfile.TemporaryDirectory() as temp_dir:
            record_dir = Path(temp_dir) / "usage-records"
            record_usage_case.write_record(record_dir, record)

            with self.assertRaises(SystemExit):
                record_usage_case.write_record(record_dir, record)


if __name__ == "__main__":
    unittest.main()
