# Synthetic Security Audit Example

Public-safe high-risk example for defensive security review tasks.

This fixture is intentionally synthetic. It exists so the eval and live task
trial pipeline can verify that a generated Codex harness handles high-risk
security-audit work with explicit authorization, secret-handling, and
destructive-testing boundaries.

Run:

```bash
python scripts/eval_generated_harness.py examples/live-create/synthetic-security-audit
python scripts/smoke_generated_harness.py examples/live-create/synthetic-security-audit
python scripts/run_live_example_task_trials.py --trial security-review-synthetic-code
```
