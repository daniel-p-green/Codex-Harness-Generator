import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "export_pilot_github_issues.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("export_pilot_github_issues", SCRIPT)
export_pilot_github_issues = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = export_pilot_github_issues
spec.loader.exec_module(export_pilot_github_issues)

import pilot_board
import usage_from_issue


class PilotGithubIssuesTests(unittest.TestCase):
    def pilot_payload(self, slug: str = "llm-app-pilot", domain: str = "LLM app") -> dict:
        return {
            "generated": "2026-06-04T12:00:00Z",
            "selected_index": 1,
            "selected_pilot": {
                "slug": slug,
                "title": slug.replace("-", " "),
                "domain": domain,
                "profile": "llm-app",
                "source_type": "external",
                "generation_path": "installed-quickstart",
                "project_name": "LLM App Workspace Pilot",
            },
            "prepared_pilot": {
                "target": "/tmp/codex-llm-app-pilot",
                "pilot_pack": {
                    "harness_label": "LLM App Workspace Pilot",
                    "pack": "Docs/Environment/LLM_APP_PILOT_PACK.md",
                    "issue_draft": "Docs/Environment/LLM_APP_USAGE_ISSUE_DRAFT.md",
                },
            },
            "claim_boundary": "Preparing the next pilot is not usage proof until converted into a checked usage record.",
        }

    def args(self, root: Path, **overrides) -> Namespace:
        values = {
            "record_dir": (root / "pilot-records").as_posix(),
            "usage_record_dir": (root / "usage-records").as_posix(),
            "usage_report": "Docs/Environment/USAGE_RECORDS.md",
            "pilot_board_report": "Docs/Environment/PILOT_BOARD.md",
            "out_dir": (root / "pilot-github-issues").as_posix(),
            "report": (root / "PILOT_GITHUB_ISSUES.md").as_posix(),
            "status": None,
            "slug": None,
            "label": None,
        }
        values.update(overrides)
        return Namespace(**values)

    def write_pilot_record(
        self,
        root: Path,
        status: str = "prepared",
        slug: str = "llm-app-pilot",
        notes: str = "",
    ) -> None:
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        record = pilot_board.build_record(self.pilot_payload(slug=slug), status=status)
        if notes:
            record["notes"] = notes
            record["status_history"] = [{"notes": notes}]
        (record_dir / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def test_build_payload_writes_github_issue_command(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = export_pilot_github_issues.build_payload(self.args(root, label=["pilot", "external-usage"]))

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("github-issue-ready", payload["readiness"])
        self.assertEqual(1, payload["issue_count"])
        record = payload["records"][0]
        self.assertIn("gh issue create", record["gh_issue_create"])
        self.assertIn("--body-file", record["gh_issue_create"])
        self.assertIn("--label pilot", record["gh_issue_create"])
        self.assertIn("pilot-update llm-app-pilot --status invited", record["mark_invited"])
        self.assertIn("usage-from-github-issue <issue-number-or-url>", record["convert_github_issue"])
        self.assertIn("--include-comments", record["convert_github_issue"])
        self.assertIn("### Pilot or usage-record slug", record["body"])
        self.assertIn("llm-app-pilot", record["body"])
        self.assertIn("## Reporter Completion Reply Template", record["body"])
        self.assertIn("reply to this issue with the completion template", record["body"])
        self.assertIn("reporter_reply_template", record)
        self.assertIn("GitHub issue drafts help open public pilot intake issues", payload["claim_boundary"])

    def test_reporter_reply_template_matches_importer_headings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = export_pilot_github_issues.build_payload(self.args(root))

        record = payload["records"][0]
        sections = usage_from_issue.parse_issue_sections(record["reporter_reply_template"])

        for field in ("outcome", "task_summary", "evidence", "verification", "privacy_review", "limitations"):
            self.assertIn(field, sections)
            self.assertTrue(sections[field].strip())
        self.assertGreaterEqual(len(usage_from_issue.parse_items(sections["evidence"])), 2)
        self.assertGreaterEqual(len(usage_from_issue.parse_items(sections["verification"])), 2)
        self.assertGreaterEqual(len(usage_from_issue.parse_items(sections["limitations"])), 1)

    def test_build_payload_uses_live_issue_url_from_pilot_notes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(
                root,
                status="invited",
                notes="opened public pilot issue https://github.com/example/repo/issues/42",
            )

            payload = export_pilot_github_issues.build_payload(self.args(root))

        record = payload["records"][0]
        self.assertEqual("https://github.com/example/repo/issues/42", record["live_issue_url"])
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", record["convert_github_issue"])
        self.assertNotIn("<issue-number-or-url>", record["convert_github_issue"])

    def test_write_outputs_creates_body_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = export_pilot_github_issues.build_payload(args)

            export_pilot_github_issues.write_outputs(payload)

            body = root / "pilot-github-issues" / "llm-app-pilot-github-issue.md"
            report = root / "PILOT_GITHUB_ISSUES.md"
            body_text = body.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")

        self.assertIn("# External Usage Pilot", body_text)
        self.assertIn("### Outcome", body_text)
        self.assertIn("_no response_", body_text)
        self.assertIn("Reporter Completion Reply Template", body_text)
        self.assertIn("# Pilot GitHub Issue Queue", report_text)
        self.assertIn("Create public issue:", report_text)
        self.assertIn("After the reporter completes the public issue", report_text)
        self.assertIn("usage-from-github-issue <issue-number-or-url>", report_text)
        self.assertIn("--include-comments", report_text)
        self.assertIn("Reporter completion reply template:", report_text)
        self.assertIn("Opening an issue or marking a pilot invited is not adoption evidence", report_text)

    def test_report_with_live_issue_warns_not_to_duplicate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(
                root,
                status="invited",
                notes="opened public pilot issue https://github.com/example/repo/issues/42",
            )
            args = self.args(root)
            payload = export_pilot_github_issues.build_payload(args)

            export_pilot_github_issues.write_outputs(payload)

            report_text = (root / "PILOT_GITHUB_ISSUES.md").read_text(encoding="utf-8")

        self.assertIn("- Live issue: https://github.com/example/repo/issues/42", report_text)
        self.assertIn("Do not create a duplicate", report_text)
        self.assertNotIn("Create public issue:", report_text)
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", report_text)

    def test_no_active_pilots_is_still_a_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "pilot-records").mkdir()

            payload = export_pilot_github_issues.build_payload(self.args(root))

        self.assertEqual("pass", payload["status"])
        self.assertEqual("no-active-pilots", payload["readiness"])
        self.assertEqual(0, payload["issue_count"])


if __name__ == "__main__":
    unittest.main()
