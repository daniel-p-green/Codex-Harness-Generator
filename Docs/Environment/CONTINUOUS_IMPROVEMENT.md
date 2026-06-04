# Continuous Improvement Loop

This project should improve by turning every escaped harness issue into a repeatable eval.

## Eval Pyramid

1. **Static port eval**: `scripts/eval_codex_port.py`
   - Checks this generator repo for Codex schema drift, stale platform terms, broken config references, weak permissions, and missing official-source coverage.
2. **Generated harness fixture eval**: `scripts/eval_generated_harness.py`
   - Scores representative generated harnesses across correctness, Codex compatibility, safety/privacy, user clarity, maintainability, and source alignment.
3. **Generated harness smoke**: `scripts/smoke_generated_harness.py`
   - Proves Codex-facing files can be read, parsed, and resolved. CI runs the offline mode; local maintainers can add `--codex-live` for an authenticated Codex CLI instruction-loading check through `codex exec`.
4. **Mutation tests**: `tests/test_generated_harness_contract.py`
   - Starts from valid generated fixtures, breaks one contract at a time, and verifies the evaluator catches the defect.
5. **Full gate**: `scripts/run_evals.py`
   - Runs the static eval, generated fixture eval, generated smoke, mutation/unit tests, and compile checks.

## Required Gates

Before release or public claims:

```bash
python scripts/run_evals.py
```

Use `Docs/Environment/PROOF_MATRIX.md` to check which claim each gate supports
and what remains outside the proven scope.

The GitHub Actions workflow `.github/workflows/evals.yml` runs the same gate on pull requests, pushes to `main`, manual dispatch, and a weekly schedule.

The GitHub Actions workflow `.github/workflows/usage-evidence-lint.yml` runs a
lint-only public usage-evidence check on `[usage]`, `External usage pilot:`, and
`usage-evidence` issues/comments. It upserts one marker-managed readiness
comment with missing fields and evidence counts; it does not write usage records
or count as adoption proof.

For a local live smoke check against the Codex CLI, run:

```bash
python scripts/run_evals.py --codex-live
```

Use this only on machines with authenticated Codex CLI access. The live mode is
non-interactive and should not start the Codex TUI. By default it adds one live
smoke check against `examples/create-acceptance/software-development`; use
`--codex-live-profile all` for the full checked-in create-acceptance matrix.

For public product-proof examples, capture only sanitized live `/create` outputs:

```bash
python scripts/capture_live_create_example.py /tmp/codex-live-target \
  --capture-name synthetic-python-cli \
  --project-brief "Synthetic Python CLI utility for local file cleanup" \
  --project-type "Python CLI" \
  --notes "public-safe live-create capture" \
  --source-label "temporary synthetic target" \
  --run-codex \
  --force
```

Review the generated `Docs/Environment/LIVE_CREATE_CAPTURE.md` before committing
the capture under `examples/live-create/`. The capture helper requires
`Docs/Environment/CREATION_CONTEXT.md` by default; use
`--allow-missing-creation-context` only for explicitly labeled non-`/create`
experiments that should not be treated as product proof.

For authenticated usefulness checks against checked-in live examples:

```bash
python scripts/run_live_example_task_trials.py
```

This copies each live example to a temporary workspace, seeds synthetic inputs,
runs `codex exec`, verifies concrete output files, and writes
`examples/live-create/TASK_TRIALS.md`.

For eval trend tracking:

```bash
python scripts/record_eval_snapshot.py
```

This writes a compact JSON snapshot under `Docs/Environment/eval-history/` and
updates `Docs/Environment/EVAL_TRENDS.md`.

For official OpenAI source freshness:

```bash
python scripts/check_source_freshness.py
```

This verifies cited `developers.openai.com` URLs are reachable and updates
`Docs/Environment/SOURCE_FRESHNESS.md` plus its JSON payload. Treat failures as
a semantic review trigger before changing generator behavior.

## Fixture Coverage

The current golden fixtures cover:

- `software-dev-basic`
- `knowledge-work-basic`
- `security-audit-basic`
- `nontechnical-user-basic`
- `multi-area-hub`

Add a new fixture when a user-visible workflow has meaningfully different risks, permissions, routing, or user-level assumptions.

## Escaped-Issue Protocol

When a generated harness bug escapes:

1. Reproduce the issue in the smallest generated harness fixture.
2. Add a mutation test that fails for the escaped bug.
3. Patch the evaluator or generator guidance so the mutation fails before release.
4. Patch affected templates, profiles, or docs.
5. Run `python scripts/run_evals.py`.
6. Add the lesson to the relevant docs or guideline file only after the eval proves it.

## Score Policy

Generated fixtures must have:

- `status = pass`
- score >= 90
- zero failures

Warnings are allowed only when deliberately documenting a known quality debt. Otherwise, fix the fixture, evaluator, or template until the warning is gone.

## Scheduled Review

Weekly CI should be treated as a drift detector. If it fails without code changes, inspect:

- OpenAI Codex docs drift
- Python/runtime drift
- stale generated fixture assumptions
- overly narrow official-source coverage

Do not loosen a failing eval until there is a written reason and a replacement check that preserves the product promise.
