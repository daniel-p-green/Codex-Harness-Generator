# Generated Harness Fixtures

These are compact golden harnesses used by `scripts/eval_generated_harness.py` and mutation tests.

Each fixture represents a generated output class the product claims to support:

- `software-dev-basic`
- `knowledge-work-basic`
- `security-audit-basic`
- `nontechnical-user-basic`
- `multi-area-hub`

Keep fixtures small and explicit. When a bug escapes, add or mutate the smallest fixture that reproduces it, then update the evaluator so the issue fails before release.

