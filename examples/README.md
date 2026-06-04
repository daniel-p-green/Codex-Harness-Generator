# Examples

This directory contains checked-in example generated environments.

- `deterministic/` contains minimal generated harnesses for each deterministic
  starter profile. These are refreshed by
  `python scripts/refresh_deterministic_examples.py` and verified by
  `python scripts/run_evals.py`.
- `create-acceptance/` contains a deterministic preset `/create` acceptance
  snapshot with `CREATION_CONTEXT.md`, generated harness files, and
  `CREATE_ACCEPTANCE_REPORT.md`. Refresh it with
  `python scripts/refresh_create_acceptance_examples.py`.
- `brief-acceptance/` contains deterministic brief-to-harness acceptance
  snapshots with `CREATION_CONTEXT.md`, generated harness files,
  `CREATE_ACCEPTANCE_REPORT.md`, and `PROFILE_SELECTION.md` including the
  recommendation confidence. Refresh it with
  `python scripts/refresh_brief_acceptance_examples.py`.
- `live-create/` is reserved for sanitized examples from live, model-mediated
  `/create` runs. Package them with
  `python scripts/capture_live_create_example.py`; see
  `live-create/INDEX.md` for checked-in captures.

For fast local examples without waiting on the full model-mediated path, use the
deterministic profile generator:

```bash
python scripts/codex_harness.py profiles
python scripts/codex_harness.py profiles --details
python scripts/codex_harness.py recommend "RAG app with prompts, evals, and retrieval checks"
python scripts/codex_harness.py brief-acceptance /tmp/codex-rag-example \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --force
python scripts/codex_harness.py eval /tmp/codex-rag-example
python scripts/codex_harness.py smoke /tmp/codex-rag-example
```

Supported deterministic profiles include the four base starter profiles and 16
bundled domain presets:

- `software-development`
- `knowledge-work`
- `data-analysis`
- `devops-infrastructure`
- `api-design`
- `book-publishing`
- `course-design`
- `customer-support`
- `data-engineering`
- `data-science`
- `financial-modeling`
- `game-development`
- `grant-writing`
- `hiring-pipeline`
- `legal-research`
- `llm-app`
- `market-research`
- `product-management`
- `security-audit`
- `social-media`

Example:

```bash
python scripts/codex_harness.py generate /tmp/codex-knowledge-example \
  --profile knowledge-work \
  --force
python scripts/codex_harness.py eval /tmp/codex-knowledge-example
python scripts/codex_harness.py smoke /tmp/codex-knowledge-example
```
