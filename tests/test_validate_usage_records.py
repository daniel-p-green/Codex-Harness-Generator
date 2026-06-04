import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_PATH = REPO_ROOT / "scripts" / "validate_usage_records.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("validate_usage_records", VALIDATE_PATH)
validate_usage_records = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = validate_usage_records
spec.loader.exec_module(validate_usage_records)


class ValidateUsageRecordsTests(unittest.TestCase):
    def valid_payload(self):
        return {
            "slug": "synthetic-task",
            "title": "Synthetic task",
            "generated": "2026-06-04T12:00:00Z",
            "domain": "software development",
            "harness_path": "examples/live-create/synthetic-python-cli",
            "task_summary": "Used a generated harness on public-safe TODO notes.",
            "outcome": "success",
            "evidence_type": "synthetic",
            "evidence": ["reports/todo-audit.md produced"],
            "verification": ["expected terms found"],
            "privacy_review": "Synthetic inputs only; no personal data or secrets.",
            "limitations": ["Single small task."],
        }

    def write_payload(self, root: Path, name: str, payload: dict) -> Path:
        path = root / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def test_validate_record_dir_passes_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = validate_usage_records.validate_record_dir(Path(temp_dir) / "missing")

        self.assertEqual("pass", payload["status"])
        self.assertEqual(0, payload["record_count"])

    def test_validate_record_file_accepts_valid_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_payload(Path(temp_dir), "synthetic-task", self.valid_payload())

            result = validate_usage_records.validate_record_file(path)

        self.assertEqual("pass", result["status"], result)

    def test_validate_record_file_rejects_slug_filename_mismatch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_payload(Path(temp_dir), "wrong-name", self.valid_payload())

            result = validate_usage_records.validate_record_file(path)

        self.assertEqual("fail", result["status"])
        self.assertIn("filename stem", result["error"])

    def test_validate_record_file_rejects_sensitive_text(self):
        payload = self.valid_payload()
        payload["evidence"] = ["Contact user@example.com for details."]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_payload(Path(temp_dir), "synthetic-task", payload)

            result = validate_usage_records.validate_record_file(path)

        self.assertEqual("fail", result["status"])
        self.assertIn("email address", result["error"])


if __name__ == "__main__":
    unittest.main()
