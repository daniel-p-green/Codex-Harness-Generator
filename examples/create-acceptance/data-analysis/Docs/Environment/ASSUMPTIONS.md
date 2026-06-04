# Assumptions

- Assumption: This deterministic harness targets local analysis artifacts rather than live production data.
- Assumption: Sensitive data may exist, so credential and raw secret files stay denied.
- Assumption: Verification requires reproducible commands or explicit data-access limits.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/run-harness-evals.py` locally, or run `codex-harness validate <target>` from the generator repo.
