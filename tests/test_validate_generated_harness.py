import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_PATH = REPO_ROOT / "scripts" / "validate_generated_harness.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "generated_harnesses" / "software-dev-basic"

if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("validate_generated_harness", VALIDATE_PATH)
validate_generated_harness = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = validate_generated_harness
spec.loader.exec_module(validate_generated_harness)


class ValidateGeneratedHarnessTests(unittest.TestCase):
    def test_build_payload_passes_for_valid_fixture(self):
        payload = validate_generated_harness.build_payload([FIXTURE.as_posix()])

        self.assertEqual("pass", payload["status"], payload)
        result = payload["results"][0]
        self.assertEqual("pass", result["status"])
        self.assertEqual([], result["failures"])
        self.assertEqual("pass", result["eval"]["status"])
        self.assertEqual("pass", result["smoke"]["offline"]["status"])

    def test_build_payload_fails_when_eval_score_below_minimum(self):
        payload = validate_generated_harness.build_payload([FIXTURE.as_posix()], min_score=101)

        self.assertEqual("fail", payload["status"])
        self.assertEqual(["eval_score_below_minimum"], payload["results"][0]["failures"])

    def test_build_payload_fails_when_smoke_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "broken"
            shutil.copytree(FIXTURE, target)
            (target / ".codex" / "config.toml").unlink()

            payload = validate_generated_harness.build_payload([target.as_posix()])

        self.assertEqual("fail", payload["status"])
        self.assertIn("offline_smoke_failed", payload["results"][0]["failures"])

    def test_main_json_outputs_payload(self):
        output = io.StringIO()

        with redirect_stdout(output):
            status = validate_generated_harness.main(["--json", FIXTURE.as_posix()])

        payload = json.loads(output.getvalue())
        self.assertEqual(0, status)
        self.assertEqual("pass", payload["status"])

    def test_text_output_includes_eval_and_smoke_summary(self):
        output = io.StringIO()

        with redirect_stdout(output):
            status = validate_generated_harness.main([FIXTURE.as_posix()])

        text = output.getvalue()
        self.assertEqual(0, status)
        self.assertIn("Generated harness validate: PASS", text)
        self.assertIn("offline=PASS", text)


if __name__ == "__main__":
    unittest.main()
