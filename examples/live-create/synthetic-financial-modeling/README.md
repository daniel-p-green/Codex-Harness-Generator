# Synthetic Financial Modeling Example

Public-safe high-risk example for source-backed financial scenario notes.

This fixture is intentionally synthetic. It exists so the eval and live task
trial pipeline can verify that a generated Codex harness handles high-risk
financial-modeling work with explicit assumption, risk, uncertainty,
sensitivity, privacy, and not-financial-advice boundaries.

Run:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-financial-modeling
python scripts/smoke_generated_harness.py examples/live-create/synthetic-financial-modeling
python scripts/run_live_example_task_trials.py --trial financial-modeling-synthetic-scenarios
```
