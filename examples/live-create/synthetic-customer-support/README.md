# Synthetic Customer Support Example

Public-safe high-risk example for source-backed customer support notes.

This fixture is intentionally synthetic. It exists so the eval and live task
trial pipeline can verify that a generated Codex harness handles high-risk
customer-support work with explicit source grounding, `[VERIFY]` gaps,
`[PROPOSED]` commitments, privacy, PII, escalation, and human-review boundaries.

Run:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-customer-support
python scripts/smoke_generated_harness.py examples/live-create/synthetic-customer-support
python scripts/run_live_example_task_trials.py --trial customer-support-synthetic-escalation
```
