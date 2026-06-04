import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "evals.yml"
PYPROJECT = REPO_ROOT / "pyproject.toml"
SCRIPTS = REPO_ROOT / "scripts"


class CiWorkflowTests(unittest.TestCase):
    def advertised_python_versions(self) -> list[str]:
        return sorted(
            re.findall(
                r'"Programming Language :: Python :: (3\.\d+)"',
                PYPROJECT.read_text(encoding="utf-8"),
            )
        )

    def workflow_python_versions(self) -> list[str]:
        text = WORKFLOW.read_text(encoding="utf-8")
        matrix_block = text.split("python-version:", 1)[1].split("steps:", 1)[0]
        return sorted(re.findall(r'"(3\.\d+)"', matrix_block))

    def test_ci_matrix_matches_advertised_python_versions(self):
        self.assertEqual(self.advertised_python_versions(), self.workflow_python_versions())

    def test_ci_preserves_gate_failure_and_uploads_payload(self):
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("Install runtime dependencies", text)
        self.assertIn("python -m pip install .", text)
        self.assertIn("set -o pipefail", text)
        self.assertIn("python scripts/run_evals.py --json | tee eval-gate-${{ matrix.python-version }}.json", text)
        self.assertIn("actions/checkout@v6", text)
        self.assertIn("actions/setup-python@v6", text)
        self.assertIn("actions/upload-artifact@v7", text)
        self.assertIn("eval-gate-python-${{ matrix.python-version }}", text)

    def test_tomli_fallback_has_python_310_runtime_dependency(self):
        script_text = "\n".join(path.read_text(encoding="utf-8") for path in SCRIPTS.glob("*.py"))
        pyproject_text = PYPROJECT.read_text(encoding="utf-8")

        self.assertIn("import tomli as tomllib", script_text)
        self.assertIn('"tomli>=2.0.1; python_version < \'3.11\'"', pyproject_text)


if __name__ == "__main__":
    unittest.main()
