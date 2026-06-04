# Assumptions

- Assumption: This fixture models a compact public-safe financial-modeling
  harness with one reviewer agent and one health-check skill.
- Assumption: All task-trial inputs are synthetic and safe to publish.
- Assumption: Analysis notes must cite local source assumptions and preserve
  risk, uncertainty, and sensitivity limits.
- Limit: It does not prove professional investment, tax, accounting, valuation,
  or capital-allocation judgment.
- Limit: It is a high-risk task-trial fixture, not evidence of production
  financial analysis usage.
- Verify: Run `python scripts/eval_generated_harness.py
  examples/live-create/synthetic-financial-modeling`,
  `python scripts/smoke_generated_harness.py
  examples/live-create/synthetic-financial-modeling`, and
  `python scripts/run_live_example_task_trials.py --trial
  financial-modeling-synthetic-scenarios`.
