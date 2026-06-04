import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "scripts" / "check_source_freshness.py"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("check_source_freshness", SOURCE_PATH)
check_source_freshness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = check_source_freshness
spec.loader.exec_module(check_source_freshness)


class SourceFreshnessTests(unittest.TestCase):
    def test_rejects_non_official_url(self):
        with self.assertRaises(SystemExit):
            check_source_freshness.assert_official_url("https://example.com/codex")

    def test_check_sources_summarizes_failures(self):
        def fetcher(url: str, timeout: int):
            status = "fail" if url.endswith("missing") else "pass"
            return check_source_freshness.SourceResult(
                url=url,
                status=status,
                http_status=404 if status == "fail" else 200,
                final_url=url,
                error="not found" if status == "fail" else None,
            )

        payload = check_source_freshness.check_sources(
            [
                "https://developers.openai.com/codex/config-reference",
                "https://developers.openai.com/codex/missing",
            ],
            timeout=1,
            fetcher=fetcher,
        )

        self.assertEqual("fail", payload["status"])
        self.assertEqual(2, len(payload["sources"]))

    def test_write_report(self):
        payload = {
            "generated": "2026-06-04T04:30:00Z",
            "status": "pass",
            "sources": [
                {
                    "url": "https://developers.openai.com/codex/config-reference",
                    "status": "pass",
                    "http_status": 200,
                    "final_url": "https://developers.openai.com/codex/config-reference",
                    "error": None,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            report = Path(temp_dir) / "SOURCE_FRESHNESS.md"
            check_source_freshness.write_report(report, payload)

            text = report.read_text(encoding="utf-8")
            self.assertIn("Status: PASS", text)
            self.assertIn("https://developers.openai.com/codex/config-reference", text)


if __name__ == "__main__":
    unittest.main()
