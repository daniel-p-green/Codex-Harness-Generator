# Assumptions

- Assumption: This fixture models a compact public-safe hiring-pipeline harness
  with one reviewer agent and one health-check skill.
- Assumption: All task-trial inputs are synthetic and safe to publish.
- Assumption: Hiring support notes must cite local source evidence and preserve
  criteria, fairness, privacy, and human-review limits.
- Limit: It does not prove lawful hiring compliance or real candidate decision
  quality.
- Limit: It is a high-risk task-trial fixture, not evidence of production
  hiring usage.
- Verify: Run `python scripts/eval_generated_harness.py
  examples/live-create/synthetic-hiring-pipeline`,
  `python scripts/smoke_generated_harness.py
  examples/live-create/synthetic-hiring-pipeline`, and
  `python scripts/run_live_example_task_trials.py --trial
  hiring-pipeline-synthetic-scorecard`.
