# Assumptions

- Assumption: This fixture models a compact public-safe legal-research harness
  with one reviewer agent and one health-check skill.
- Assumption: All task-trial inputs are synthetic and safe to publish.
- Assumption: Research notes must cite local sources and preserve jurisdiction
  uncertainty.
- Limit: It does not prove attorney-grade legal judgment, compliance review, or
  real-world legal advice quality.
- Limit: It is a high-risk task-trial fixture, not evidence of production legal
  research usage.
- Verify: Run `python scripts/eval_generated_harness.py
  examples/live-create/synthetic-legal-research`,
  `python scripts/smoke_generated_harness.py
  examples/live-create/synthetic-legal-research`, and
  `python scripts/run_live_example_task_trials.py --trial
  legal-research-synthetic-policy`.
