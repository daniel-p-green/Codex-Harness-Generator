# Examples

This directory contains checked-in example generated environments.

- `deterministic/` contains minimal generated harnesses for each deterministic
  starter profile. These are refreshed by
  `python scripts/refresh_deterministic_examples.py` and verified by
  `python scripts/run_evals.py`.
- `create-acceptance/` contains a deterministic preset `/create` acceptance
  snapshot with `CREATION_CONTEXT.md`, generated harness files, and
  `CREATE_ACCEPTANCE_REPORT.md`. Refresh it with
  `python scripts/refresh_create_acceptance_examples.py`.
- `live-create/` is reserved for sanitized examples from live, model-mediated
  `/create` runs. Package them with
  `python scripts/capture_live_create_example.py`; see
  `live-create/INDEX.md` for checked-in captures.

For fast local examples without waiting on the full model-mediated path, use the
deterministic profile generator:

```bash
python scripts/generate_minimal_harness.py --list-profiles
python scripts/generate_minimal_harness.py /tmp/codex-harness-example --force
python scripts/eval_generated_harness.py /tmp/codex-harness-example
python scripts/smoke_generated_harness.py /tmp/codex-harness-example
```

Supported deterministic profiles:

- `software-development`
- `knowledge-work`
- `data-analysis`
- `devops-infrastructure`

Example:

```bash
python scripts/generate_minimal_harness.py /tmp/codex-knowledge-example \
  --profile knowledge-work \
  --force
python scripts/eval_generated_harness.py /tmp/codex-knowledge-example
python scripts/smoke_generated_harness.py /tmp/codex-knowledge-example
```
