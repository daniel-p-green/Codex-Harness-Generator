# Live Create Examples

This directory is reserved for sanitized examples from live, model-mediated
`/create` runs. These examples should only be checked in after the generated
target passes both:

```bash
python scripts/eval_generated_harness.py <target>
python scripts/smoke_generated_harness.py <target>
```

Each captured example must include `Docs/Environment/CREATION_CONTEXT.md`; that
file is the trigger handoff artifact that distinguishes a `/create` pipeline
capture from a generic generated harness.

See `INDEX.md` for the checked-in capture matrix.

Use `scripts/run_live_example_task_trials.py` to run authenticated task trials
against temporary copies of these examples and write `TASK_TRIALS.md`.

Use the capture helper to package a generated target:

```bash
python scripts/capture_live_create_example.py /tmp/codex-live-target \
  --capture-name synthetic-python-cli \
  --project-brief "Synthetic Python CLI utility for local file cleanup" \
  --project-type "Python CLI" \
  --notes "public-safe live-create capture" \
  --source-label "temporary synthetic target" \
  --force
```

To launch an authenticated Codex CLI run first, add `--run-codex`:

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

Do not check in real credentials, customer data, proprietary source, local
machine paths, raw model transcripts, transient `_working` state, or `.env*`
files. The capture helper strips common unsafe files and writes
`Docs/Environment/LIVE_CREATE_CAPTURE.md`, but the maintainer still owns the
final privacy review.
