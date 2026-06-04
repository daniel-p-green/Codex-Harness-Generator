import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_PATH = REPO_ROOT / "scripts" / "check_semantic_alignment.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("check_semantic_alignment", SEMANTIC_PATH)
check_semantic_alignment = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = check_semantic_alignment
spec.loader.exec_module(check_semantic_alignment)


class SemanticAlignmentTests(unittest.TestCase):
    def test_normalize_text_strips_html_noise(self):
        text = check_semantic_alignment.normalize_text("<main>AGENTS.md <script>ignore()</script>&amp; SKILL.md</main>")

        self.assertIn("AGENTS.md", text)
        self.assertIn("&", text)
        self.assertNotIn("ignore", text)

    def test_evaluate_checks_passes_when_official_and_local_terms_match(self):
        check = check_semantic_alignment.ConceptCheck(
            name="Test concept",
            url="https://developers.openai.com/codex/test",
            official_terms=("AGENTS.md", "SKILL.md"),
            local_terms=("AGENTS.md", "SKILL.md"),
            local_paths=("guide.md",),
        )

        def fetcher(url: str, timeout: int):
            return check_semantic_alignment.FetchedDoc(
                url=url,
                status="pass",
                text="Official docs mention AGENTS.md and SKILL.md.",
                http_status=200,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "guide.md").write_text("Local guidance mentions AGENTS.md and SKILL.md.\n", encoding="utf-8")

            payload = check_semantic_alignment.evaluate_checks([check], timeout=1, fetcher=fetcher, root=root)

        self.assertEqual("pass", payload["status"], payload)

    def test_evaluate_checks_fails_when_official_term_disappears(self):
        check = check_semantic_alignment.ConceptCheck(
            name="Test concept",
            url="https://developers.openai.com/codex/test",
            official_terms=("default_permissions",),
            local_terms=("default_permissions",),
            local_paths=("guide.md",),
        )

        def fetcher(url: str, timeout: int):
            return check_semantic_alignment.FetchedDoc(
                url=url,
                status="pass",
                text="Official docs changed.",
                http_status=200,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "guide.md").write_text("Local guidance mentions default_permissions.\n", encoding="utf-8")

            payload = check_semantic_alignment.evaluate_checks([check], timeout=1, fetcher=fetcher, root=root)

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["default_permissions"], payload["checks"][0]["official_missing_terms"])

    def test_evaluate_checks_fails_when_local_path_is_missing(self):
        check = check_semantic_alignment.ConceptCheck(
            name="Test concept",
            url="https://developers.openai.com/codex/test",
            official_terms=("AGENTS.md",),
            local_terms=("AGENTS.md",),
            local_paths=("missing.md",),
        )

        def fetcher(url: str, timeout: int):
            return check_semantic_alignment.FetchedDoc(
                url=url,
                status="pass",
                text="Official docs mention AGENTS.md.",
                http_status=200,
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            payload = check_semantic_alignment.evaluate_checks(
                [check],
                timeout=1,
                fetcher=fetcher,
                root=Path(temp_dir),
            )

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["missing.md"], payload["checks"][0]["local_missing_paths"])

    def test_write_report_includes_review_needed(self):
        payload = {
            "generated": "2026-06-04T05:00:00Z",
            "status": "fail",
            "checks": [
                {
                    "name": "Config permission schema",
                    "status": "fail",
                    "url": "https://developers.openai.com/codex/permissions",
                    "http_status": 200,
                    "error": None,
                    "official_missing_terms": ["default_permissions"],
                    "local_missing_paths": [],
                    "local_missing_terms": [],
                    "local_paths": ["guide.md"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "SEMANTIC_ALIGNMENT.md"
            check_semantic_alignment.write_report(report, payload)

            text = report.read_text(encoding="utf-8")

        self.assertIn("Status: FAIL", text)
        self.assertIn("Review Needed", text)
        self.assertIn("default_permissions", text)


if __name__ == "__main__":
    unittest.main()
