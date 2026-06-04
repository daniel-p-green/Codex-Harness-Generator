# Synthetic Legal Research Example

Public-safe high-risk example for source-backed legal research notes.

This fixture is intentionally synthetic. It exists so the eval and live task
trial pipeline can verify that a generated Codex harness handles high-risk
legal-research work with explicit jurisdiction, citation, uncertainty, privacy,
and not-legal-advice boundaries.

Run:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-legal-research
python scripts/smoke_generated_harness.py examples/live-create/synthetic-legal-research
python scripts/run_live_example_task_trials.py --trial legal-research-synthetic-policy
```
