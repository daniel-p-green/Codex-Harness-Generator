# Synthetic Hiring Pipeline Example

Public-safe high-risk example for source-backed hiring support notes.

This fixture is intentionally synthetic. It exists so the eval and live task
trial pipeline can verify that a generated Codex harness handles high-risk
hiring-pipeline work with explicit structured criteria, job-related evidence,
bias, privacy, protected-class, and human-review boundaries.

Run:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-hiring-pipeline
python scripts/smoke_generated_harness.py examples/live-create/synthetic-hiring-pipeline
python scripts/run_live_example_task_trials.py --trial hiring-pipeline-synthetic-scorecard
```
