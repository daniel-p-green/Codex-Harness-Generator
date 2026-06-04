# Assumptions

- Assumption: This deterministic harness targets local LLM app code, prompts, and eval assets.
- Assumption: Model behavior claims require eval evidence and source grounding.
- Assumption: Verification means focused evals, fixtures, prompt reviews, and explicit limitations.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/eval_generated_harness.py <target>` and `python scripts/smoke_generated_harness.py <target>` from the generator repo.
