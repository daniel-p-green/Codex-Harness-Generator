# RAG Quality Harness Codex Harness

This Codex harness supports LLM-powered app, RAG, agent, prompt, and eval workflow development. Verify live file state before
editing, run the narrowest meaningful check, and report any skipped verification.

## Defaults

- Prefer simple, maintainable code with clear names.
- Do not read secrets, tokens, private keys, credential files, or `.env` files.
- Treat security and privacy issues as high priority.
- Ask for clarification when correctness, data loss, or privacy depends on
  missing context.
- Run tests when they exist; otherwise use source checks, dry runs, or the
  narrowest runnable command.
- Use the reviewer for non-trivial changes before calling work done.
- Record repeated workflow friction in `Docs/Environment/IMPROVEMENT_LOG.md`
  before changing harness behavior.

## Verification

- Inspect prompts, retrieval sources, eval cases, and model boundaries before changing behavior.
- Run focused evals or fixture tests when available.
- Document hallucination, privacy, cost, latency, and safety limits.
