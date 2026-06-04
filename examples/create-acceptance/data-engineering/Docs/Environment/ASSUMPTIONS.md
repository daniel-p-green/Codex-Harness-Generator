# Assumptions

- Assumption: This deterministic harness targets local pipeline, schema, and validation files.
- Assumption: Sensitive data may exist, so raw secrets and credentials stay denied.
- Assumption: Verification means checking schemas, sample data, validation commands, and operational limits.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
