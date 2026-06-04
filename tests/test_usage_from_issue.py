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

import pilot_board


ISSUE_BODY = """### Domain or project type

LLM app

### Generated harness profile or label

llm-app profile

### Evidence type

private-summary

### Source type

external

### Generation path

installed-init-brief

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
    def write_matching_pilot_record(self, pilot_record_dir: Path) -> Path:
        payload = {
            "generated": "2026-06-04T00:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": "external-llm-app",
                "title": "External LLM app report",
                "domain": "LLM app",
                "profile": "llm-app",
                "source_type": "external",
                "generation_path": "installed-init-brief",
                "project_name": "External LLM App Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/external-llm-app",
                "pilot_pack": {
                    "harness_label": "llm-app profile",
                    "pack": "/tmp/PILOT_PACK.md",
                    "issue_draft": "/tmp/ISSUE.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }
        pilot_record_dir.mkdir(parents=True, exist_ok=True)
        record_path = pilot_record_dir / "external-llm-app.json"
        pilot_board.write_record(record_path, pilot_board.build_record(payload), force=True)
        return record_path

    def test_parse_issue_sections_maps_github_issue_form_labels(self):
        sections = usage_from_issue.parse_issue_sections(ISSUE_BODY)

        self.assertEqual("LLM app", sections["domain"])
        self.assertEqual("llm-app profile", sections["harness_label"])
        self.assertEqual("private-summary", sections["evidence_type"])
        self.assertEqual("external", sections["source_type"])
        self.assertEqual("installed-init-brief", sections["generation_path"])
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
            self.assertEqual("external", record["source_type"])
            self.assertEqual("installed-init-brief", record["generation_path"])
            self.assertEqual("llm-app profile", record["harness_path"])
            self.assertEqual(2, len(record["evidence"]))
            self.assertEqual(2, len(record["verification"]))
            self.assertTrue((record_dir / "external-llm-app.json").is_file())
            self.assertIn("external-llm-app", report.read_text(encoding="utf-8"))
            self.assertIsNone(payload["pilot_update"])

    def test_usage_from_issue_can_convert_matching_pilot_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            issue = temp_path / "issue.md"
            issue.write_text(ISSUE_BODY, encoding="utf-8")
            record_dir = temp_path / "records"
            report = temp_path / "USAGE_RECORDS.md"
            pilot_record_dir = temp_path / "pilot-records"
            board_report = temp_path / "PILOT_BOARD.md"
            pilot_record_path = self.write_matching_pilot_record(pilot_record_dir)

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
                    "--pilot-record-dir",
                    pilot_record_dir.as_posix(),
                    "--pilot-board-report",
                    board_report.as_posix(),
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual("pass", payload["pilot_update"]["status"])
            self.assertEqual("pass", payload["pilot_update"]["board_status"])
            self.assertEqual("external-llm-app", payload["pilot_update"]["record"]["usage_record"])

            pilot_record = json.loads(pilot_record_path.read_text(encoding="utf-8"))
            self.assertEqual("converted", pilot_record["status"])
            self.assertEqual("external-llm-app", pilot_record["usage_record"])
            self.assertTrue(pilot_record["validated_usage_record"].endswith("external-llm-app.json"))
            self.assertIn("converted from external usage issue", pilot_record["notes"])
            self.assertIn(
                "Converted with validated usage records: 1",
                board_report.read_text(encoding="utf-8"),
            )

    def test_usage_from_issue_no_write_validates_without_writing_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            issue = temp_path / "issue.md"
            issue.write_text(ISSUE_BODY, encoding="utf-8")
            record_dir = temp_path / "records"
            report = temp_path / "USAGE_RECORDS.md"
            pilot_record_dir = temp_path / "pilot-records"
            pilot_record_path = self.write_matching_pilot_record(pilot_record_dir)

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
                    "--pilot-record-dir",
                    pilot_record_dir.as_posix(),
                    "--no-write",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertFalse(payload["written"])
            self.assertIsNone(payload["path"])
            self.assertEqual("external-llm-app", payload["record"]["slug"])
            self.assertIsNone(payload["pilot_update"])
            self.assertFalse((record_dir / "external-llm-app.json").exists())
            self.assertFalse(report.exists())
            pilot_record = json.loads(pilot_record_path.read_text(encoding="utf-8"))
            self.assertEqual("prepared", pilot_record["status"])

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

    def test_usage_from_issue_rejects_unfilled_no_response_bullets(self):
        body = ISSUE_BODY.replace("- Generated AGENTS.md matched the project shape.\n- The harness made verification steps explicit.", "- _No response_\n- _No response_")
        body = body.replace("- Ran the generated smoke check successfully.\n- Completed one real task using the generated reviewer guidance.", "- _No response_\n- _No response_")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            issue = temp_path / "issue.md"
            issue.write_text(body, encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    SCRIPT.as_posix(),
                    issue.as_posix(),
                    "--slug",
                    "unfilled-external-report",
                    "--title",
                    "Unfilled external report",
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
            self.assertIn("At least one evidence item is required", completed.stderr + completed.stdout)


if __name__ == "__main__":
    unittest.main()
