# Assumptions

- Assumption: This fixture models a compact public-safe security-audit harness
  with one reviewer agent and one health-check skill.
- Assumption: All task-trial inputs are synthetic and safe to publish.
- Assumption: Review work should stay defensive unless a user explicitly scopes
  authorized active testing.
- Limit: It does not prove professional penetration-testing quality,
  organization-level security controls, or vulnerability scoring judgment.
- Limit: It is a high-risk task-trial fixture, not evidence of real-world
  production security review usage.
- Verify: Run `python scripts/eval_generated_harness.py
  examples/live-create/synthetic-security-audit`,
  `python scripts/smoke_generated_harness.py
  examples/live-create/synthetic-security-audit`, and
  `python scripts/run_live_example_task_trials.py --trial
  security-review-synthetic-code`.
