# Demo Capture

Purpose: show the reproducible `codex-harness init --brief` path without private data.

## Command

```bash
python scripts/codex_harness.py demo-capture examples/demo-capture/rag-quality --brief "RAG app with prompts, evals, and retrieval checks" --project-name "RAG Quality Harness" --target-label examples/demo-capture/rag-quality --force
```

## Generated Harness

- Target: examples/demo-capture/rag-quality
- Brief: RAG app with prompts, evals, and retrieval checks
- Selected profile: llm-app
- Selection confidence: high
- Selection evidence: `Docs/Environment/PROFILE_SELECTION.md`
- Primary instruction surface: `AGENTS.md` (RAG Quality Harness Codex Harness)

## Verification

- Brief acceptance: pass
- Eval score: 100
- Offline smoke: pass
- Local harness check: pass
- Combined validation: pass

## Reviewer Walkthrough

1. Open `Docs/Environment/PROFILE_SELECTION.md` to inspect why the profile was selected.
2. Open `AGENTS.md` to inspect the generated Codex-facing instruction surface.
3. Run `python scripts/check-harness.py` inside this generated harness.
4. From the generator repo, run `python scripts/codex_harness.py validate <this-harness>`.

## Limits

- This is a deterministic public-safe demo, not external adoption proof.
- It proves the installed-style brief path can generate and validate an inspectable harness.
- It does not prove every future live model-mediated `/create` run will be ideal.
