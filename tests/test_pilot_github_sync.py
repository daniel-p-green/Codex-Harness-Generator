import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sync_pilot_github_issues.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("sync_pilot_github_issues", SCRIPT)
sync_pilot_github_issues = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = sync_pilot_github_issues
spec.loader.exec_module(sync_pilot_github_issues)

usage_spec = importlib.util.spec_from_file_location(
    "usage_from_issue",
    REPO_ROOT / "scripts" / "usage_from_issue.py",
)
usage_from_issue = importlib.util.module_from_spec(usage_spec)
assert usage_spec.loader is not None
sys.modules[usage_spec.name] = usage_from_issue
usage_spec.loader.exec_module(usage_from_issue)


INCOMPLETE_BODY = """### Pilot or usage-record slug

llm-app-pilot

### Domain or project type

LLM app

### Generated harness profile or label

LLM App Workspace Pilot

### Evidence type

private-summary

### Source type

external

### Generation path

installed-quickstart

### Outcome

_no response_

### Public-safe task summary

_no response_

### Evidence

_no response_

### Verification performed

_no response_

### Privacy review

_no response_

### Limitations

_no response_
"""


COMPLETION_COMMENT = """### Outcome

success

### Public-safe task summary

Reporter completed one privacy-safe LLM app task using the generated harness.

### Evidence

- The generated AGENTS.md fit the task shape.
- The harness checklist made verification explicit.

### Verification performed

- Ran the generated smoke check.
- Reviewed the task output against the generated reviewer instructions.

### Privacy review

Only public-safe summary evidence was shared; no secrets, personal data, local paths, or raw logs.

### Limitations

- One reporter and one task.
"""


class PilotGithubSyncTests(unittest.TestCase):
    def args(self, root: Path, **overrides) -> argparse.Namespace:
        values = {
            "record_dir": (root / "pilot-records").as_posix(),
            "usage_record_dir": (root / "usage-records").as_posix(),
            "usage_report": (root / "USAGE_RECORDS.md").as_posix(),
            "pilot_board_report": (root / "PILOT_BOARD.md").as_posix(),
            "report": (root / "PILOT_GITHUB_SYNC.md").as_posix(),
            "followup_dir": (root / "pilot-github-followups").as_posix(),
            "repo": None,
            "gh_bin": "gh",
            "generated": "2026-06-04T00:00:00Z",
            "reminder_after_hours": 72,
            "status": None,
            "slug": None,
            "no_write": False,
            "json": True,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def write_pilot_record(self, root: Path, slug: str = "llm-app-pilot", issue: str = "42") -> None:
        record = {
            "claim_boundary": "Preparing a pilot is not usage proof until converted into checked usage evidence.",
            "domain": "LLM app",
            "generated": "2026-06-04T00:00:00Z",
            "generation_path": "installed-quickstart",
            "harness_label": "LLM App Workspace Pilot",
            "issue_draft": "Docs/Environment/issue.md",
            "notes": f"opened public pilot issue https://github.com/example/repo/issues/{issue}",
            "pilot_pack": "Docs/Environment/pack.md",
            "profile": "llm-app",
            "selected_index": 1,
            "slug": slug,
            "source_type": "external",
            "status": "invited",
            "status_history": [{"notes": f"opened public pilot issue https://github.com/example/repo/issues/{issue}"}],
            "target": "generated pilot harness: llm-app-pilot",
            "title": "LLM app pilot",
            "usage_record": "",
        }
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / f"{slug}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def github_payload(self, comments: list[dict] | None = None) -> dict:
        return {
            "number": 42,
            "title": "External usage pilot: LLM app pilot",
            "url": "https://github.com/example/repo/issues/42",
            "state": "OPEN",
            "body": INCOMPLETE_BODY,
            "comments": comments or [],
        }

    def test_pending_issue_reports_waiting_for_reporter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root, repo="example/repo", gh_bin="/tmp/fake-gh"),
                fetch_issue=lambda *args, **kwargs: self.github_payload(),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("waiting-for-reporters", payload["readiness"])
        self.assertEqual(1, payload["summary"]["waiting_for_reporter"])
        record = payload["records"][0]
        self.assertEqual("waiting-for-reporter", record["readiness"])
        self.assertIn("outcome", record["missing_fields"])
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", record["commands"]["convert"])
        self.assertIn("--repo example/repo", record["commands"]["convert"])
        self.assertIn("--gh-bin /tmp/fake-gh", record["commands"]["convert"])
        self.assertIn("Please reply with the missing public-safe sections", record["reporter_followup"])
        self.assertIn("Reporter reply template", record["reporter_followup"])
        self.assertIn("Copy this into a new issue comment", record["reporter_followup"])
        self.assertIn("converted, validated usage record counts", record["reporter_followup"])
        self.assertIn("codex-harness-maintainer-followup", record["reporter_followup"])
        self.assertIn("### Evidence", record["reporter_followup"])
        self.assertIn("at least two public-safe bullets", record["reporter_followup"])
        sections = usage_from_issue.parse_issue_sections(record["reporter_followup"])
        for field in ("outcome", "task_summary", "evidence", "verification", "privacy_review", "limitations"):
            self.assertIn(field, sections)
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("gh issue comment https://github.com/example/repo/issues/42", record["commands"]["comment_followup"])
        self.assertIn("--body-file", record["commands"]["comment_followup"])

    def test_posted_maintainer_followup_does_not_recommend_duplicate_comment(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("waiting-for-reporters", payload["readiness"])
        self.assertEqual(1, payload["summary"]["waiting_for_reporter"])
        self.assertEqual(1, payload["summary"]["maintainer_followups_posted"])
        self.assertEqual(1, payload["summary"]["github_comment_count"])
        self.assertEqual(1, payload["summary"]["excluded_comment_count"])
        record = payload["records"][0]
        self.assertEqual("waiting-for-reporter", record["readiness"])
        self.assertTrue(record["maintainer_followup_posted"])
        self.assertEqual("https://github.com/example/repo/issues/42#issuecomment-1", record["maintainer_followup_comment"]["url"])
        self.assertEqual("2026-06-04T19:38:17Z", record["maintainer_followup_comment"]["created_at"])
        self.assertEqual("maintainer", record["maintainer_followup_comment"]["author"])
        self.assertEqual(0, record["github_issue"]["comment_count"])
        self.assertEqual(0, record["github_issue"]["reporter_comment_count"])
        self.assertEqual(1, record["github_issue"]["total_comment_count"])
        self.assertEqual(1, record["github_issue"]["excluded_comment_count"])
        self.assertEqual(0, record["reporter_replies"]["count"])
        self.assertFalse(record["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertEqual(72, record["reminder_after_hours"])
        self.assertFalse(record["reminder_due"])
        self.assertEqual("2026-06-07T19:38:17Z", record["next_reminder_at"])
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("Reporter reply template", record["followup_template"])
        self.assertNotIn("comment_followup", record["commands"])
        self.assertIn("already posted", record["reporter_followup"])

    def test_usage_lint_comment_does_not_count_as_reporter_reply(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        lint_comment = f"{sync_pilot_github_issues.USAGE_LINT_MARKER}\n\nReporter comment count: `0`"
        comments = [
            {
                "author": {"login": "maintainer"},
                "body": maintainer_comment,
                "createdAt": "2026-06-04T19:38:17Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-1",
            },
            {
                "author": {"login": "github-actions"},
                "body": lint_comment,
                "createdAt": "2026-06-04T20:33:52Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-2",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=comments),
            )

        record = payload["records"][0]
        self.assertEqual("waiting-for-reporter", record["readiness"])
        self.assertEqual(2, payload["summary"]["github_comment_count"])
        self.assertEqual(2, payload["summary"]["excluded_comment_count"])
        self.assertEqual(0, record["github_issue"]["comment_count"])
        self.assertEqual(0, record["github_issue"]["reporter_comment_count"])
        self.assertEqual(2, record["github_issue"]["total_comment_count"])
        self.assertEqual(2, record["github_issue"]["excluded_comment_count"])
        self.assertEqual(0, record["reporter_replies"]["count"])
        self.assertFalse(record["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("Reporter reply template", record["followup_template"])
        self.assertNotIn("comment_followup", record["commands"])

    def test_unmarked_owner_comment_does_not_count_as_reporter_reply(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comments = [
            {
                "author": {"login": "maintainer"},
                "authorAssociation": "OWNER",
                "body": maintainer_comment,
                "createdAt": "2026-06-04T19:38:17Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-1",
            },
            {
                "author": {"login": "maintainer"},
                "authorAssociation": "OWNER",
                "body": "I checked the queue manually; still waiting on reporter evidence.",
                "createdAt": "2026-06-04T20:00:00Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-2",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=comments),
            )

        record = payload["records"][0]
        self.assertEqual("waiting-for-reporter", record["readiness"])
        self.assertEqual(2, payload["summary"]["github_comment_count"])
        self.assertEqual(2, payload["summary"]["excluded_comment_count"])
        self.assertEqual(0, record["github_issue"]["reporter_comment_count"])
        self.assertEqual(2, record["github_issue"]["total_comment_count"])
        self.assertEqual(2, record["github_issue"]["excluded_comment_count"])
        self.assertEqual(0, record["reporter_replies"]["count"])
        self.assertFalse(record["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("Reporter reply template", record["followup_template"])
        self.assertNotIn("comment_followup", record["commands"])

    def test_stale_maintainer_followup_flags_reminder_due_without_comment_command(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root, generated="2026-06-08T00:00:00Z"),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

        record = payload["records"][0]
        self.assertEqual(1, payload["summary"]["reminders_due"])
        self.assertTrue(record["reminder_due"])
        self.assertEqual(76.36, record["maintainer_followup_age_hours"])
        self.assertEqual("2026-06-07T19:38:17Z", record["next_reminder_at"])
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("Reporter reply template", record["followup_template"])
        self.assertNotIn("comment_followup", record["commands"])

    def test_reporter_reply_after_followup_reenables_targeted_comment(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comments = [
            {
                "author": {"login": "maintainer"},
                "body": maintainer_comment,
                "createdAt": "2026-06-04T19:38:17Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-1",
            },
            {
                "author": {"login": "reporter"},
                "authorAssociation": "NONE",
                "body": "I ran it, but I have not filled out every section yet.",
                "createdAt": "2026-06-04T20:00:00Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-2",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=comments),
            )

        record = payload["records"][0]
        self.assertEqual("waiting-for-reporter", record["readiness"])
        self.assertEqual(1, record["github_issue"]["comment_count"])
        self.assertEqual(1, record["github_issue"]["reporter_comment_count"])
        self.assertEqual(2, record["github_issue"]["total_comment_count"])
        self.assertEqual(1, record["reporter_replies"]["count"])
        self.assertEqual("https://github.com/example/repo/issues/42#issuecomment-2", record["reporter_replies"]["latest"]["url"])
        self.assertEqual("NONE", record["reporter_replies"]["latest"]["author_association"])
        self.assertTrue(record["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertFalse(record["reminder_due"])
        self.assertTrue(record["followup_file"].endswith("llm-app-pilot-followup.md"))
        self.assertIn("comment_followup", record["commands"])

    def test_repo_local_default_paths_render_as_relative_commands(self):
        args = argparse.Namespace(
            usage_record_dir=(REPO_ROOT / "Docs" / "Environment" / "usage-records").as_posix(),
            usage_report=(REPO_ROOT / "Docs" / "Environment" / "USAGE_RECORDS.md").as_posix(),
            record_dir=(REPO_ROOT / "Docs" / "Environment" / "pilot-records").as_posix(),
            pilot_board_report=(REPO_ROOT / "Docs" / "Environment" / "PILOT_BOARD.md").as_posix(),
            repo=None,
            gh_bin="gh",
        )

        command = sync_pilot_github_issues.conversion_command(
            "https://github.com/example/repo/issues/42",
            args,
            lint_only=True,
        )

        self.assertIn("--record-dir Docs/Environment/usage-records", command)
        self.assertIn("--report Docs/Environment/USAGE_RECORDS.md", command)
        self.assertIn("--pilot-record-dir Docs/Environment/pilot-records", command)
        self.assertIn("--pilot-board-report Docs/Environment/PILOT_BOARD.md", command)
        self.assertNotIn(REPO_ROOT.as_posix(), command)

    def test_comment_completed_issue_reports_conversion_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[{"body": COMPLETION_COMMENT}]),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("conversion-ready", payload["readiness"])
        self.assertEqual(1, payload["summary"]["conversion_ready"])
        record = payload["records"][0]
        self.assertEqual("conversion-ready", record["readiness"])
        self.assertEqual([], record["missing_fields"])
        self.assertEqual(1, record["github_issue"]["comment_count"])
        self.assertEqual(1, record["github_issue"]["reporter_comment_count"])
        self.assertEqual(1, record["github_issue"]["total_comment_count"])
        self.assertIn("No reporter follow-up needed", record["reporter_followup"])
        self.assertEqual("", record["followup_file"])
        self.assertNotIn("comment_followup", record["commands"])

    def test_conversion_ready_issue_can_be_converted_and_updates_pilot_board(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            github_payload = self.github_payload(comments=[{"body": COMPLETION_COMMENT}])

            sync_payload = sync_pilot_github_issues.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: github_payload,
            )
            convert_payload = sync_pilot_github_issues.usage_from_github_issue.build_payload(
                argparse.Namespace(
                    issue=sync_payload["records"][0]["issue_url"],
                    repo=None,
                    gh_bin="gh",
                    include_comments=True,
                    slug=None,
                    title=None,
                    harness_label=None,
                    source_type=None,
                    generation_path=None,
                    generated="2026-06-04T00:00:00Z",
                    record_dir=(root / "usage-records").as_posix(),
                    report=(root / "USAGE_RECORDS.md").as_posix(),
                    pilot_record_dir=(root / "pilot-records").as_posix(),
                    pilot_board_report=(root / "PILOT_BOARD.md").as_posix(),
                    pilot_notes="converted after pilot GitHub sync",
                    force=False,
                    lint_only=False,
                    no_write=False,
                    json=True,
                ),
                github_payload=github_payload,
            )
            usage_record = root / "usage-records" / "llm-app-pilot.json"
            usage_record_exists = usage_record.exists()
            pilot_record = json.loads((root / "pilot-records" / "llm-app-pilot.json").read_text(encoding="utf-8"))

        self.assertEqual("conversion-ready", sync_payload["readiness"], sync_payload)
        self.assertEqual("pass", convert_payload["status"], convert_payload)
        self.assertTrue(convert_payload["written"])
        self.assertTrue(usage_record_exists)
        self.assertEqual("llm-app-pilot", convert_payload["record"]["slug"])
        self.assertEqual("converted", pilot_record["status"])
        self.assertEqual("llm-app-pilot", pilot_record["usage_record"])
        self.assertEqual("pass", convert_payload["pilot_update"]["board_status"])

    def test_write_report_includes_claim_boundary_and_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = sync_pilot_github_issues.build_payload(
                args,
                fetch_issue=lambda *fetch_args, **kwargs: self.github_payload(comments=[{"body": COMPLETION_COMMENT}]),
            )

            sync_pilot_github_issues.write_report(Path(args.report), payload)

            report = Path(args.report).read_text(encoding="utf-8")

        self.assertIn("# Pilot GitHub Issue Sync", report)
        self.assertIn("Conversion-ready issues: 1", report)
        self.assertIn("GitHub comments fetched: 1", report)
        self.assertIn("Reporter comments included: 1", report)
        self.assertIn("Maintainer/automation comments excluded: 0", report)
        self.assertIn("Do not count live issues", report)
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", report)
        self.assertIn("Reporter follow-up:", report)
        self.assertIn("No reporter follow-up needed", report)

    def test_write_report_distinguishes_refreshed_template_from_public_comment(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = sync_pilot_github_issues.build_payload(
                args,
                fetch_issue=lambda *fetch_args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

            sync_pilot_github_issues.write_report(Path(args.report), payload)
            report = Path(args.report).read_text(encoding="utf-8")

        self.assertIn("- Follow-up file: `", report)
        self.assertIn("- Follow-up action: template refreshed; no duplicate public comment", report)
        self.assertNotIn("gh issue comment", report)

    def test_write_followups_writes_waiting_issue_files_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = sync_pilot_github_issues.build_payload(
                args,
                fetch_issue=lambda *fetch_args, **kwargs: self.github_payload(),
            )

            sync_pilot_github_issues.write_followups(payload)

            followup = root / "pilot-github-followups" / "llm-app-pilot-followup.md"
            text = followup.read_text(encoding="utf-8")

        self.assertIn("Please reply with the missing public-safe sections", text)
        self.assertIn("Reporter reply template", text)
        self.assertIn("Copy this into a new issue comment", text)
        self.assertIn("### Privacy review", text)

    def test_write_followups_refreshes_template_even_after_posted_comment(self):
        maintainer_comment = f"{sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = sync_pilot_github_issues.build_payload(
                args,
                fetch_issue=lambda *fetch_args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

            sync_pilot_github_issues.write_followups(payload)

            record = payload["records"][0]
            followup = Path(record["followup_file"])
            text = followup.read_text(encoding="utf-8")

        self.assertTrue(record["maintainer_followup_posted"])
        self.assertNotIn("comment_followup", record["commands"])
        self.assertIn("already posted", record["reporter_followup"])
        self.assertIn("Reporter reply template", text)
        self.assertIn("converted, validated usage record counts", text)


if __name__ == "__main__":
    unittest.main()
