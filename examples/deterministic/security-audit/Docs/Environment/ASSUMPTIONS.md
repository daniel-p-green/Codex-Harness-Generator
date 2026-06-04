# Assumptions

- Assumption: This deterministic harness targets defensive security audit artifacts.
- Assumption: Security work requires authorization, source evidence, and safe remediation.
- Assumption: Verification means checking affected paths, permissions, secrets, active-testing limits, and destructive-work boundaries.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
