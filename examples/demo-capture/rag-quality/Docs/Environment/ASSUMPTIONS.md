# Assumptions

- Assumption: This deterministic harness targets local LLM app code, prompts, and eval assets.
- Assumption: Model behavior claims require eval evidence and source grounding.
- Assumption: Verification means focused evals, fixtures, prompt reviews, and explicit limitations.
- Limit: It is a minimal acceptance harness, not a full model-mediated custom `/create` run.
- Verify: Run `python scripts/run-harness-evals.py` locally, or run `codex-harness validate <target>` from the generator repo.
