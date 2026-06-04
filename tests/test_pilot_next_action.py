import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "pilot_next_action.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("pilot_next_action", SCRIPT)
pilot_next_action = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = pilot_next_action
spec.loader.exec_module(pilot_next_action)


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


class PilotNextActionTests(unittest.TestCase):
    def args(self, root: Path, **overrides) -> argparse.Namespace:
        values = {
            "record_dir": (root / "pilot-records").as_posix(),
            "usage_record_dir": (root / "usage-records").as_posix(),
            "usage_report": (root / "USAGE_RECORDS.md").as_posix(),
            "pilot_board_report": (root / "PILOT_BOARD.md").as_posix(),
            "sync_report": (root / "PILOT_GITHUB_SYNC.md").as_posix(),
            "report": (root / "PILOT_NEXT_ACTION.md").as_posix(),
            "followup_dir": (root / "pilot-github-followups").as_posix(),
            "repo": "example/repo",
            "gh_bin": "/tmp/fake-gh",
            "generated": "2026-06-04T00:00:00Z",
            "reminder_after_hours": 72,
            "status": None,
            "slug": None,
            "no_write": False,
            "json": True,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def write_pilot_record(self, root: Path) -> None:
        record = {
            "claim_boundary": "Preparing a pilot is not usage proof until converted into checked usage evidence.",
            "domain": "LLM app",
            "generated": "2026-06-04T00:00:00Z",
            "generation_path": "installed-quickstart",
            "harness_label": "LLM App Workspace Pilot",
            "issue_draft": "Docs/Environment/issue.md",
            "notes": "opened public pilot issue https://github.com/example/repo/issues/42",
            "pilot_pack": "Docs/Environment/pack.md",
            "profile": "llm-app",
            "selected_index": 1,
            "slug": "llm-app-pilot",
            "source_type": "external",
            "status": "invited",
            "status_history": [{"notes": "opened public pilot issue https://github.com/example/repo/issues/42"}],
            "target": "generated pilot harness: llm-app-pilot",
            "title": "LLM app pilot",
            "usage_record": "",
        }
        record_dir = root / "pilot-records"
        record_dir.mkdir(parents=True, exist_ok=True)
        (record_dir / "llm-app-pilot.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def github_payload(self, comments: list[dict] | None = None) -> dict:
        return {
            "number": 42,
            "title": "External usage pilot: LLM app pilot",
            "url": "https://github.com/example/repo/issues/42",
            "state": "OPEN",
            "body": INCOMPLETE_BODY,
            "comments": comments or [],
        }

    def test_waiting_issue_next_action_posts_reporter_followup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = pilot_next_action.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("waiting-for-reporters", payload["readiness"])
        self.assertEqual("post-reporter-followup", payload["next_action"]["type"])
        self.assertEqual("llm-app-pilot", payload["next_action"]["slug"])
        self.assertIn("gh issue comment https://github.com/example/repo/issues/42", payload["next_action"]["command"])
        self.assertIn("--body-file", payload["next_action"]["command"])
        self.assertEqual(1, len(payload["waiting_followups"]))
        self.assertIn("outcome", payload["waiting_followups"][0]["missing_fields"])

    def test_posted_followup_next_action_waits_for_reporter_response(self):
        maintainer_comment = f"{pilot_next_action.sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = pilot_next_action.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("waiting-for-reporters", payload["readiness"])
        self.assertEqual("wait-for-reporter-response", payload["next_action"]["type"])
        self.assertEqual("llm-app-pilot", payload["next_action"]["slug"])
        self.assertIn("pilot-github-sync", payload["next_action"]["command"])
        self.assertEqual("https://github.com/example/repo/issues/42#issuecomment-1", payload["next_action"]["maintainer_followup_comment"]["url"])
        self.assertEqual("2026-06-04T19:38:17Z", payload["next_action"]["maintainer_followup_comment"]["created_at"])
        self.assertFalse(payload["next_action"]["reminder_due"])
        self.assertEqual("2026-06-07T19:38:17Z", payload["next_action"]["next_reminder_at"])
        self.assertEqual(1, len(payload["waiting_followups"]))
        self.assertTrue(payload["waiting_followups"][0]["maintainer_followup_posted"])
        self.assertEqual("https://github.com/example/repo/issues/42#issuecomment-1", payload["waiting_followups"][0]["maintainer_followup_comment"]["url"])
        self.assertEqual(0, payload["waiting_followups"][0]["reporter_replies"]["count"])
        self.assertEqual("", payload["waiting_followups"][0]["command"])

    def test_usage_lint_comment_after_followup_still_waits_for_reporter_response(self):
        maintainer_comment = f"{pilot_next_action.sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        lint_comment = f"{pilot_next_action.sync_pilot_github_issues.USAGE_LINT_MARKER}\n\nReporter comment count: `0`"
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

            payload = pilot_next_action.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=comments),
            )

        self.assertEqual("wait-for-reporter-response", payload["next_action"]["type"])
        self.assertIn("pilot-github-sync", payload["next_action"]["command"])
        self.assertNotIn("gh issue comment", payload["next_action"]["command"])
        self.assertFalse(payload["next_action"]["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertEqual(0, payload["next_action"]["reporter_replies"]["count"])
        self.assertEqual(0, payload["waiting_followups"][0]["reporter_replies"]["count"])
        self.assertEqual("", payload["waiting_followups"][0]["command"])

    def test_stale_followup_next_action_requires_review_not_auto_comment(self):
        maintainer_comment = f"{pilot_next_action.sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comment_payload = {
            "author": {"login": "maintainer"},
            "body": maintainer_comment,
            "createdAt": "2026-06-04T19:38:17Z",
            "url": "https://github.com/example/repo/issues/42#issuecomment-1",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = pilot_next_action.build_payload(
                self.args(root, generated="2026-06-08T00:00:00Z"),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[comment_payload]),
            )

        self.assertEqual("review-stale-followup", payload["next_action"]["type"])
        self.assertEqual("medium", payload["next_action"]["priority"])
        self.assertEqual("llm-app-pilot", payload["next_action"]["slug"])
        self.assertTrue(payload["next_action"]["reminder_due"])
        self.assertEqual(76.36, payload["next_action"]["maintainer_followup_age_hours"])
        self.assertIn("pilot-github-sync", payload["next_action"]["command"])
        self.assertNotIn("gh issue comment", payload["next_action"]["command"])
        self.assertEqual("", payload["waiting_followups"][0]["command"])
        self.assertTrue(payload["waiting_followups"][0]["reminder_due"])

    def test_reporter_reply_after_followup_next_action_posts_clarification(self):
        maintainer_comment = f"{pilot_next_action.sync_pilot_github_issues.MAINTAINER_FOLLOWUP_MARKER}\n\nPlease add the missing fields."
        comments = [
            {
                "author": {"login": "maintainer"},
                "body": maintainer_comment,
                "createdAt": "2026-06-04T19:38:17Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-1",
            },
            {
                "author": {"login": "reporter"},
                "body": "I ran it, but I have not filled out every section yet.",
                "createdAt": "2026-06-04T20:00:00Z",
                "url": "https://github.com/example/repo/issues/42#issuecomment-2",
            },
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = pilot_next_action.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=comments),
            )

        self.assertEqual("post-reporter-clarification", payload["next_action"]["type"])
        self.assertIn("gh issue comment https://github.com/example/repo/issues/42", payload["next_action"]["command"])
        self.assertTrue(payload["next_action"]["reporter_replies"]["after_latest_maintainer_followup"])
        self.assertEqual("https://github.com/example/repo/issues/42#issuecomment-2", payload["next_action"]["reporter_replies"]["latest"]["url"])

    def test_conversion_ready_issue_next_action_previews_before_writing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)

            payload = pilot_next_action.build_payload(
                self.args(root),
                fetch_issue=lambda *args, **kwargs: self.github_payload(comments=[{"body": COMPLETION_COMMENT}]),
            )

        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("conversion-ready", payload["readiness"])
        self.assertEqual("preview-conversion", payload["next_action"]["type"])
        self.assertIn("usage-from-github-issue https://github.com/example/repo/issues/42", payload["next_action"]["command"])
        self.assertIn("--no-write", payload["next_action"]["command"])
        self.assertEqual(1, len(payload["conversion_ready"]))
        self.assertEqual([], payload["waiting_followups"])

    def test_write_report_includes_boundary_and_selected_action(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_pilot_record(root)
            args = self.args(root)
            payload = pilot_next_action.build_payload(
                args,
                fetch_issue=lambda *fetch_args, **kwargs: self.github_payload(),
            )

            pilot_next_action.write_report(Path(args.report), payload)
            text = Path(args.report).read_text(encoding="utf-8")

        self.assertIn("# Pilot Next Action", text)
        self.assertIn("post-reporter-followup", text)
        self.assertIn("GitHub comments fetched: 0", text)
        self.assertIn("Count only converted, validated usage records", text)
        self.assertIn("gh issue comment https://github.com/example/repo/issues/42", text)

    def test_sync_fallback_command_renders_repo_local_paths_as_relative(self):
        args = argparse.Namespace(
            record_dir=(REPO_ROOT / "Docs" / "Environment" / "pilot-records").as_posix(),
            usage_record_dir=(REPO_ROOT / "Docs" / "Environment" / "usage-records").as_posix(),
            usage_report=(REPO_ROOT / "Docs" / "Environment" / "USAGE_RECORDS.md").as_posix(),
            pilot_board_report=(REPO_ROOT / "Docs" / "Environment" / "PILOT_BOARD.md").as_posix(),
            sync_report=(REPO_ROOT / "Docs" / "Environment" / "PILOT_GITHUB_SYNC.md").as_posix(),
            followup_dir=(REPO_ROOT / "Docs" / "Environment" / "pilot-github-followups").as_posix(),
            repo=None,
            gh_bin="gh",
            reminder_after_hours=72,
        )

        command = pilot_next_action.sync_command(args)

        self.assertIn("--record-dir Docs/Environment/pilot-records", command)
        self.assertIn("--usage-record-dir Docs/Environment/usage-records", command)
        self.assertIn("--report Docs/Environment/PILOT_GITHUB_SYNC.md", command)
        self.assertIn("--followup-dir Docs/Environment/pilot-github-followups", command)
        self.assertNotIn(REPO_ROOT.as_posix(), command)


if __name__ == "__main__":
    unittest.main()
