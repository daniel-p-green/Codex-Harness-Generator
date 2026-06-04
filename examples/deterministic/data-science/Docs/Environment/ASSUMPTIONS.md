# Assumptions

- Assumption: This deterministic harness targets offline data science artifacts.
- Assumption: Model and metric claims require reproducible source evidence.
- Assumption: Verification means checking data splits, metrics, scripts, and limitations.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
