# Assumptions

- Assumption: This fixture models a compact public-safe customer-support harness
  with one reviewer agent and one health-check skill.
- Assumption: All task-trial inputs are synthetic and safe to publish.
- Assumption: Support notes must cite local source evidence and preserve
  grounding, privacy, escalation, and commitment limits.
- Limit: It does not prove production support operations, policy approval, or
  regulated customer handling.
- Limit: It is a high-risk task-trial fixture, not evidence of real customer
  support usage.
- Verify: Run `python scripts/eval_generated_harness.py
  examples/live-create/synthetic-customer-support`,
  `python scripts/smoke_generated_harness.py
  examples/live-create/synthetic-customer-support`, and
  `python scripts/run_live_example_task_trials.py --trial
  customer-support-synthetic-escalation`.
