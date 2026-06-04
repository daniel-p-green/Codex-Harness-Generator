import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "usage-evidence-lint.yml"


class UsageEvidenceLintWorkflowTests(unittest.TestCase):
    def workflow_text(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_lints_usage_issues_without_writing_records(self):
        text = self.workflow_text()

        self.assertIn("issues:", text)
        self.assertIn("issue_comment:", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("startsWith(github.event.issue.title, 'External usage pilot:')", text)
        self.assertIn("startsWith(github.event.issue.title, '[usage]')", text)
        self.assertIn("contains(github.event.issue.labels.*.name, 'usage-evidence')", text)
        self.assertIn("usage-from-github-issue", text)
        self.assertIn("--include-comments", text)
        self.assertIn("--lint-only", text)
        self.assertIn('ISSUE_NUMBER="${ISSUE_NUMBER##*/}"', text)
        self.assertIn("usage-lint-issue-number.txt", text)
        self.assertNotIn("--no-write", text)
        self.assertNotIn("--json > usage-lint.json\n          python scripts/codex_harness.py usage-from-github-issue", text)

    def test_workflow_upserts_marker_managed_comment(self):
        text = self.workflow_text()

        self.assertIn("<!-- codex-harness-usage-lint -->", text)
        self.assertIn("gh api -X PATCH", text)
        self.assertIn("gh issue comment", text)
        self.assertIn("usage-lint-comment.md", text)
        self.assertRegex(text, re.compile(r"issues:\s+write"))


if __name__ == "__main__":
    unittest.main()
