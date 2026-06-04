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
            "source_type": "self-dogfood",
            "generation_path": "installed-init-brief",
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
        self.assertEqual(0, payload["summary"]["total"])

    def test_validate_record_dir_can_require_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = validate_usage_records.validate_record_dir(Path(temp_dir) / "missing", min_records=1)

        self.assertEqual("fail", payload["status"])
        self.assertIn("at least 1", payload["requirement_errors"][0])

    def test_validate_record_file_accepts_valid_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self.write_payload(Path(temp_dir), "synthetic-task", self.valid_payload())

            result = validate_usage_records.validate_record_file(path)

        self.assertEqual("pass", result["status"], result)

    def test_validate_record_dir_can_require_non_synthetic_success(self):
        payload = self.valid_payload()
        payload["slug"] = "private-task"
        payload["evidence_type"] = "private-summary"
        payload["evidence"] = ["private summary reviewed", "sanitized artifact checklist completed"]
        payload["verification"] = ["expected artifact exists", "privacy scan passed"]
        payload["limitations"] = ["Raw project files are private."]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, "private-task", payload)

            result = validate_usage_records.validate_record_dir(
                root,
                min_records=1,
                require_non_synthetic=True,
                require_success=True,
            )

        self.assertEqual("pass", result["status"], result)
        self.assertEqual(1, result["summary"]["non_synthetic"])

    def test_validate_record_dir_can_enforce_beta_evidence_thresholds(self):
        first = self.valid_payload()
        first["slug"] = "external-llm-app"
        first["domain"] = "LLM app"
        first["source_type"] = "external"
        first["evidence_type"] = "private-summary"
        first["evidence"] = ["private summary reviewed", "sanitized artifact checklist completed"]
        first["verification"] = ["expected artifact exists", "privacy scan passed"]
        first["limitations"] = ["Raw project files are private."]
        second = self.valid_payload()
        second["slug"] = "multi-project-docs"
        second["domain"] = "Documentation"
        second["source_type"] = "multi-project"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, "external-llm-app", first)
            self.write_payload(root, "multi-project-docs", second)

            result = validate_usage_records.validate_record_dir(
                root,
                min_records=2,
                min_external_or_multi_project=2,
                min_domains=2,
                min_installed_init_brief=2,
            )

        self.assertEqual("pass", result["status"], result)
        self.assertEqual(2, result["summary"]["external_or_multi_project"])
        self.assertEqual(2, result["summary"]["distinct_domains"])
        self.assertEqual(2, result["summary"]["installed_brief_generation"])

    def test_installed_quickstart_counts_toward_installed_brief_generation_threshold(self):
        first = self.valid_payload()
        first["slug"] = "external-quickstart"
        first["source_type"] = "external"
        first["generation_path"] = "installed-quickstart"
        second = self.valid_payload()
        second["slug"] = "external-init"
        second["source_type"] = "external"
        second["generation_path"] = "installed-init-brief"

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, "external-quickstart", first)
            self.write_payload(root, "external-init", second)

            result = validate_usage_records.validate_record_dir(root, min_installed_init_brief=2)

        self.assertEqual("pass", result["status"], result)
        self.assertEqual(1, result["summary"]["installed_quickstart"])
        self.assertEqual(1, result["summary"]["installed_init_brief"])
        self.assertEqual(2, result["summary"]["installed_brief_generation"])

    def test_validate_record_dir_fails_beta_evidence_thresholds_for_self_dogfood(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, "synthetic-task", self.valid_payload())

            result = validate_usage_records.validate_record_dir(
                root,
                min_external_or_multi_project=1,
                min_domains=2,
                min_installed_init_brief=2,
            )

        self.assertEqual("fail", result["status"])
        self.assertEqual(3, len(result["requirement_errors"]))
        self.assertIn("external or multi-project", result["requirement_errors"][0])

    def test_validate_record_dir_fails_non_synthetic_requirement_for_synthetic_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_payload(root, "synthetic-task", self.valid_payload())

            result = validate_usage_records.validate_record_dir(root, require_non_synthetic=True)

        self.assertEqual("fail", result["status"])
        self.assertIn("non-synthetic", result["requirement_errors"][0])

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
