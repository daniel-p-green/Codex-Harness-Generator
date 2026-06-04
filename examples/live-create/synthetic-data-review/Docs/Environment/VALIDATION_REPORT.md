# Validation Report

Status: READY_FOR_SCRIPTED_VALIDATION

## Manual Checks

- Required root files generated.
- Skills live under `.agents/skills`.
- Config registers agents and skills.
- Secret-like patterns are denied.
- Synthetic/public-safe constraints are present.

Scripted validation to be run from the generator repository:

- `python scripts/eval_generated_harness.py temporary synthetic target`
- `python scripts/smoke_generated_harness.py temporary synthetic target`

