# Assumptions

- Assumption: This deterministic harness targets local analysis artifacts rather than live production data.
- Assumption: Sensitive data may exist, so credential and raw secret files stay denied.
- Assumption: Verification requires reproducible commands or explicit data-access limits.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
