import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "format_usage_lint_comment.py"
USAGE_FROM_ISSUE_SCRIPT = REPO_ROOT / "scripts" / "usage_from_issue.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("format_usage_lint_comment", SCRIPT)
format_usage_lint_comment = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = format_usage_lint_comment
spec.loader.exec_module(format_usage_lint_comment)

usage_spec = importlib.util.spec_from_file_location("usage_from_issue", USAGE_FROM_ISSUE_SCRIPT)
usage_from_issue = importlib.util.module_from_spec(usage_spec)
assert usage_spec.loader is not None
sys.modules[usage_spec.name] = usage_from_issue
usage_spec.loader.exec_module(usage_from_issue)


class FormatUsageLintCommentTests(unittest.TestCase):
    def test_formats_conversion_ready_comment_without_claiming_proof(self):
        payload = {
            "status": "pass",
            "readiness": "conversion-ready",
            "errors": [],
            "warnings": [],
            "missing_fields": [],
            "counts": {"evidence": 2, "verification": 2, "limitations": 1},
            "github_issue": {
                "number": 12,
                "url": "https://github.com/example/repo/issues/12",
                "comments_included": True,
                "comment_count": 1,
            },
        }

        comment = format_usage_lint_comment.format_comment(payload)

        self.assertIn("<!-- codex-harness-usage-lint -->", comment)
        self.assertIn("Readiness: `conversion-ready`", comment)
        self.assertIn("ready for maintainer preview", comment)
        self.assertIn("does not write usage records", comment)
        self.assertIn("does not write usage records, convert pilots, or count as adoption proof", comment)
        self.assertIn("Evidence bullets: `2`", comment)
        self.assertNotIn("Reporter reply template", comment)

    def test_formats_missing_fields_comment(self):
        payload = {
            "status": "fail",
            "readiness": "needs-input",
            "errors": ["Missing required issue field(s): outcome, evidence"],
            "warnings": ["Synthetic usage can validate tooling but does not count as external beta-exit proof"],
            "missing_fields": ["outcome", "evidence"],
            "counts": {"evidence": 0, "verification": 1, "limitations": 0},
            "github_issue": {
                "number": 13,
                "comments_included": True,
                "comment_count": 0,
            },
        }

        comment = format_usage_lint_comment.format_comment(payload)

        self.assertIn("Readiness: `needs-input`", comment)
        self.assertIn("- outcome", comment)
        self.assertIn("- evidence", comment)
        self.assertIn("Missing required issue field", comment)
        self.assertIn("Evidence bullets: `0`", comment)
        self.assertIn("Privacy boundary", comment)
        self.assertIn("Reporter reply template", comment)
        self.assertIn("Copy this into a new issue comment", comment)
        self.assertIn("### Outcome", comment)
        self.assertIn("Use `success`, `partial`, `failed`, or `inconclusive`.", comment)
        self.assertIn("### Evidence", comment)
        self.assertIn("Add at least two public-safe bullets", comment)

    def test_reporter_reply_template_matches_usage_issue_importer_headings(self):
        missing_fields = ["outcome", "task_summary", "evidence", "verification", "privacy_review", "limitations"]
        template = "\n".join(format_usage_lint_comment.reply_template_lines(missing_fields))

        sections = usage_from_issue.parse_issue_sections(template)

        for field in missing_fields:
            self.assertIn(field, sections)
            self.assertTrue(sections[field].strip())


if __name__ == "__main__":
    unittest.main()
