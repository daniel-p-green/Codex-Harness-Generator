import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "usage_from_issue.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("usage_from_issue", SCRIPT)
usage_from_issue = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = usage_from_issue
spec.loader.exec_module(usage_from_issue)


ISSUE_BODY = """### Domain or project type

LLM app

### Generated harness profile or label

llm-app profile

### Evidence type

private-summary

### Outcome

success

### Public-safe task summary

The generated harness helped organize prompts, evals, and source-grounded review steps.

### Evidence

- Generated AGENTS.md matched the project shape.
- The harness made verification steps explicit.

### Verification performed

- Ran the generated smoke check successfully.
- Completed one real task using the generated reviewer guidance.

### Privacy review

Removed private repo names, local paths, customer details, credentials, and raw logs.

### Limitations

- One project and one task.
"""


class UsageFromIssueTests(unittest.TestCase):
    def test_parse_issue_sections_maps_github_issue_form_labels(self):
        sections = usage_from_issue.parse_issue_sections(ISSUE_BODY)

        self.assertEqual("LLM app", sections["domain"])
        self.assertEqual("llm-app profile", sections["harness_label"])
        self.assertEqual("private-summary", sections["evidence_type"])
        self.assertEqual("success", sections["outcome"])
        self.assertEqual(
            (
                "Generated AGENTS.md matched the project shape.",
                "The harness made verification steps explicit.",
            ),
            usage_from_issue.parse_items(sections["evidence"]),
        )

    def test_usage_from_issue_writes_privacy_checked_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            issue = temp_path / "issue.md"
            issue.write_text(ISSUE_BODY, encoding="utf-8")
            record_dir = temp_path / "records"
            report = temp_path / "USAGE_RECORDS.md"

            completed = subprocess.run(
                [
                    sys.executable,
                    SCRIPT.as_posix(),
                    issue.as_posix(),
                    "--slug",
                    "external-llm-app",
                    "--title",
                    "External LLM app report",
                    "--record-dir",
                    record_dir.as_posix(),
                    "--report",
                    report.as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            record = payload["record"]
            self.assertEqual("pass", payload["status"])
            self.assertEqual("external-llm-app", record["slug"])
            self.assertEqual("private-summary", record["evidence_type"])
            self.assertEqual("llm-app profile", record["harness_path"])
            self.assertEqual(2, len(record["evidence"]))
            self.assertEqual(2, len(record["verification"]))
            self.assertTrue((record_dir / "external-llm-app.json").is_file())
            self.assertIn("external-llm-app", report.read_text(encoding="utf-8"))

    def test_usage_from_issue_rejects_sensitive_issue_body(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            issue = temp_path / "issue.md"
            issue.write_text(ISSUE_BODY.replace("llm-app profile", "/Users/example/private-repo"), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    SCRIPT.as_posix(),
                    issue.as_posix(),
                    "--slug",
                    "bad-external-report",
                    "--title",
                    "Bad external report",
                    "--record-dir",
                    (temp_path / "records").as_posix(),
                    "--report",
                    (temp_path / "USAGE_RECORDS.md").as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(0, completed.returncode)
            self.assertIn("sensitive text", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
