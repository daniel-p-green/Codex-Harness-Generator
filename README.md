# Codex Harness Generator

**v1.0.0** | Codex-equivalent beta | Built for Codex GPT-5.5 (`gpt-5.5`) | MIT

Codex Harness Generator helps you create and validate a project-specific Codex
harness: `AGENTS.md`, `.codex/config.toml`, `.codex/agents/`, `.agents/skills/`,
rules, memory scaffolding, setup docs, validation records, and a small
self-improvement loop.

A harness is the operating layer around a project. It tells Codex what the
project is, which files matter, which subagents and skills exist, what can be
changed safely, how to save state, and how to verify the setup over time.

[![Tutorial Video](https://img.youtube.com/vi/0R3JPNTEljU/0.jpg)](https://www.youtube.com/watch?v=0R3JPNTEljU)

## Current Status

This repo is the **Codex-native equivalent in structure and intent** of the
earlier harness-generator architecture. It has been ported to Codex concepts:
`AGENTS.md`, `.codex/config.toml`, TOML subagents, `.agents/skills/`, Codex
permission profiles, artifact-first docs, and a local eval gate.

It should still be treated as a **beta**, not a fully battle-tested public
replacement. What is proven today:

- The repo is structurally Codex-native and passes the local eval gate.
- Golden generated-harness fixtures pass contract, smoke, and mutation tests.
- `scripts/generate_minimal_harness.py` provides a deterministic acceptance path
  for the four base starter profiles and 16 bundled domain presets without
  waiting on a live model run.
- `examples/deterministic/` contains checked-in generated harness snapshots for
  all 20 first-class starting points, and the release gate evaluates and smokes
  them.
- `scripts/simulate_create_trigger.py` proves the deterministic `/create`
  preflight handoff by writing `Docs/Environment/CREATION_CONTEXT.md` for fresh,
  existing, hub, and resume scenarios.
- `scripts/run_create_acceptance.py` stitches the trigger and preset generator
  together in one target, preserving `CREATION_CONTEXT.md`, writing a complete
  harness, and adding `CREATE_ACCEPTANCE_REPORT.md`.
- `scripts/run_demo_capture.py` creates a short public-safe demo harness from a
  brief, writes `Docs/Environment/DEMO_CAPTURE.md`, and validates the result so
  reviewers can inspect profile selection, `AGENTS.md`, and local checks.
- `scripts/run_quickstart.py` and `codex-harness quickstart` turn the first-use
  path into one command: generate from a brief, validate, run the copied local
  eval, and write `Docs/Environment/QUICKSTART_REPORT.md`.
- `scripts/inspect_project.py` and `codex-harness inspect` scan local project
  metadata such as config filenames, top-level directories, and extensions to
  recommend deterministic starter profiles before generation.
- `codex-harness init --from-project` turns that metadata inspection into a
  generated harness and records `Docs/Environment/PROJECT_INSPECTION.md` inside
  the output.
- `examples/create-acceptance/` contains checked-in snapshots of that
  deterministic preset `/create` acceptance flow for every supported profile and
  bundled domain preset.
- `scripts/refresh_generated_surfaces.py` and `codex-harness refresh-examples`
  refresh checked-in generated fixtures and example families from the current
  generator, then run the example inventory contract check so public examples
  do not drift behind generated behavior.
- `examples/demo-capture/` contains a checked-in public-safe walkthrough of the
  brief-driven demo path.
- Generated harnesses are required to include architecture, assumptions, source
  mapping, manifests, and validation reports.
- Generated harnesses include `Docs/Environment/EVAL_PLAN.md`, a portable
  project-specific eval plan with success criteria, smoke checks, acceptance
  checks, reviewer checks, and regression checks.
- Generated harnesses include `Docs/Environment/IMPROVEMENT_LOG.md`, a tracked
  loop for converting repeated friction and user corrections into small,
  evidence-backed harness updates.
- Generated harnesses include `scripts/record-improvement.py`, a local helper
  for appending structured, redacted improvement-log entries.
- Generated harnesses include `scripts/summarize-improvements.py`, a local
  summary/check over the improvement backlog, including proposed and applied
  harness updates.
- Generated harnesses include `Docs/Environment/TASK_TRIALS.md` and
  `scripts/record-task-trial.py`, a copied-harness-local lane for recording
  task outcome, evidence, verification, privacy review, and limitations.
- Generated harnesses include `scripts/summarize-task-trials.py`, a local
  summary/check over recorded task-trial outcomes.
- Generated harnesses include `scripts/run-harness-evals.py` and
  `Docs/Environment/EVAL_REPORT.md`, a copied-harness-local eval report that
  runs the local smoke check, task-trial summary, and improvement-backlog
  summary without this generator repo.
- Generated harnesses include `scripts/export-public-usage-report.py`, a
  copied-harness-local exporter that turns the latest complete successful task
  trial plus local eval status into the same public-safe issue-body format that
  maintainers can review directly with `codex-harness usage-from-harness` or
  convert from a submitted issue with `codex-harness usage-from-issue`.
- Generated harnesses include `scripts/check-harness.py`, a local smoke check
  that can run without this generator repo and catches missing paths, stale
  manifest references, broken agent/skill config, and weak eval/improvement
  logs.
- `scripts/capture_live_create_example.py` provides a repeatable packaging path
  for sanitized live `/create` outputs.
- `examples/live-create/` contains sanitized live model-mediated `/create`
  captures for knowledge work, Python CLI, and data analysis, plus a curated
  public-safe high-risk security-audit task-trial fixture and legal-research
  task-trial fixture, financial-modeling task-trial fixture, hiring-pipeline
  task-trial fixture, and customer-support task-trial fixture.
- `scripts/run_live_example_task_trials.py` runs authenticated Codex task trials
  against temporary copies of those generated harnesses and verifies concrete
  output files.
- The generated-harness evaluator includes high-risk domain guardrail mutations
  for security audit, legal research, financial analysis, hiring, and customer
  support scenarios.
- `scripts/codex_harness.py` gives users one thin local entry point for
  profile listing, profile descriptions, quickstart, project inspection, generation,
  inspected generation, acceptance, eval, smoke, copied local eval reports,
  migration audit, evidence-packet, pilot preparation, issue-based usage
  conversion, gate, demo-capture, live-trial, source-freshness, and snapshot
  workflows.
- `pyproject.toml` exposes that wrapper as an installable `codex-harness`
  console command, and the release gate smokes the non-editable install path.
- `scripts/record_eval_snapshot.py` records eval-gate snapshots under
  `Docs/Environment/eval-history/` and updates `Docs/Environment/EVAL_TRENDS.md`.
- `scripts/check_source_freshness.py` verifies official OpenAI documentation
  citations are still reachable and writes `Docs/Environment/SOURCE_FRESHNESS.md`.
- `scripts/check_semantic_alignment.py` checks that key local guidance still
  names the core concepts present in official Codex docs and writes
  `Docs/Environment/SEMANTIC_ALIGNMENT.md`.
- `scripts/check_codex_equivalence.py` and `codex-harness equivalence` write
  `Docs/Environment/CODEX_EQUIVALENCE_MATRIX.md`, a tested capability map from
  the earlier harness-generator responsibilities to the Codex-native command,
  artifact, and proof surfaces.
- `scripts/check_upstream_drift.py` and `codex-harness upstream-drift` write
  `Docs/Environment/UPSTREAM_DRIFT.md`, a source-lineage audit showing whether
  the source upstream ref has upstream-only commits that need
  Codex-port review.
- `scripts/record_usage_case.py` provides a privacy-checked path for recording
  sanitized real-world or private-summary usage evidence under
  `Docs/Environment/usage-records/`, and `scripts/validate_usage_records.py`
  can enforce stricter non-synthetic, external/multi-project, domain-coverage,
  and installed-generation proof thresholds when making real-world usage claims.
- `scripts/usage_gaps.py` and `codex-harness usage-gaps` write
  `Docs/Environment/USAGE_GAPS.md`, a concrete list of the remaining beta-exit
  evidence gaps plus suggested external pilot targets from the supported Codex
  profile catalog and a coverage projection showing whether those candidates
  would satisfy beta-exit usage thresholds if completed and converted.
- `scripts/beta_exit_audit.py` and `codex-harness beta-exit-audit` write
  `Docs/Environment/BETA_EXIT_AUDIT.md`, a non-gating beta-exit readiness audit
  that names missing evidence, source-check state, pilot-board state, and the
  final commands to run before dropping the beta label.
- `scripts/export_pilot_campaign.py` and `codex-harness pilot-campaign` write
  `Docs/Environment/PILOT_CAMPAIGN.md`, a shareable external-pilot campaign
  plan derived from the current usage gaps, including a projection for the
  listed pilot slots.
- `scripts/proof_next.py` and `codex-harness proof-next` write
  `Docs/Environment/PROOF_NEXT.md`, a next-action packet that turns the current
  beta-exit gap into exact prepare, board, conversion, audit, and final proof
  commands without treating the packet as evidence.
- `scripts/pilot_board.py` and `codex-harness pilot-board` write
  `Docs/Environment/PILOT_BOARD.md`, a prepared-pilot funnel report that tracks
  prepared, invited, completed, converted, and dropped pilots without treating
  outreach state as usage proof. Use `codex-harness pilot-update <slug>` to
  move a pilot through that funnel and refresh the board without hand-editing
  JSON; converted pilots are cross-checked against the referenced usage record.
- `scripts/prepare_pilot.py` and `codex-harness prepare-pilot` combine
  brief-based quickstart generation with an external pilot pack and issue-body
  draft, so the next beta-exit pilot can be prepared with one command before a
  reporter runs a real task.
- `scripts/prepare_next_pilot.py` and `codex-harness prepare-next-pilot`
  select the next recommended pilot from current usage gaps and prepare that
  generated harness, pack, and issue draft without copy-pasting a long command;
  add `--pilot-record-dir` when the prepared pilot should appear on the pilot
  board.
- `scripts/prepare_pilot_batch.py` and `codex-harness prepare-pilot-batch`
  dry-run or prepare the full suggested pilot batch under one target root so
  maintainers can turn the beta-exit coverage projection into concrete pilot
  materials without running each slot by hand.
- `scripts/usage_from_harness.py` and `codex-harness usage-from-harness`
  convert a generated harness's local eval report and task trials into a
  privacy-checked usage record; add
  `--pilot-record-dir Docs/Environment/pilot-records` to convert the matching
  prepared pilot in the same run.
- Generated `Docs/GETTING_STARTED.md` files now include a first useful task
  loop, profile-specific verification menu, task-trial recording command, local
  eval command, and privacy-safe reporting boundary.
- `scripts/export_evidence_packet.py` and `codex-harness evidence-packet`
  write a public-safe Markdown packet from a copied harness's local eval report
  and task trials before maintainers decide whether a usage record is justified.
- `scripts/export_pilot_pack.py` and `codex-harness pilot-pack` write an
  external pilot guide and optional GitHub issue-body draft so outside testers
  know which commands to run, what evidence to record, and what not to share.
- `scripts/usage_from_issue.py` and `codex-harness usage-from-issue` convert a
  sanitized GitHub external-usage issue body into a privacy-checked usage
  record; add `--no-write --json` to preview before writing files, or
  `--pilot-record-dir Docs/Environment/pilot-records` to convert the matching
  prepared pilot after the record is written. New issue drafts include the
  pilot or usage-record slug so maintainers can omit `--slug` when the issue
  body is complete.
- `Docs/Environment/usage-records/` includes sanitized self-dogfood usage
  records from this public repo's Codex work. They are useful evidence, but not
  yet external or longitudinal adoption proof.
- `scripts/proof_status.py` writes `Docs/Environment/PROOF_STATUS.md`, a
  one-command readiness summary tying the proof matrix, installable CLI smoke,
  live task trials, and usage records together without overclaiming.

What still needs product proof:

- More real use of generated harnesses on real Codex tasks over time, especially
  external or multi-project usage, recorded as sanitized or private-summary
  evidence. External users can start with the GitHub **External usage report**
  issue template; see `Docs/Environment/EXTERNAL_USAGE_EVIDENCE.md`.
- More live examples for specialized domains as new public-safe briefs become
  available.

Until broader real-world usage records exist, treat the eval suite, golden
fixtures, deterministic examples, synthetic live examples, and self-dogfood
usage evidence as strong product proof, not a guarantee that every future
`/create` run will be ideal.

For a claim-by-claim evidence map, see
`Docs/Environment/PROOF_MATRIX.md`. For beta exit criteria and near-term
milestones, see `Docs/Environment/ROADMAP.md`.

## Why this exists

OpenAI's Codex customization has several layers: project instructions, config,
subagents, skills, permissions, MCP servers, memory, and docs. Teams can
hand-write those pieces, but the result often drifts: broken file references,
oversized instructions, generic routing, unclear permission boundaries, and
undocumented assumptions.

This repo turns that setup work into a repeatable Codex workflow. The generator
interviews you or starts from a preset, writes the harness in focused passes, and
runs validation so the output is reviewable on disk.

## When it is useful

- You create similar Codex setups across several projects, teams, or domains.
- You want repeatable local conventions instead of one-off prompt notes.
- You need specialized subagents, skills, permissions, and memory to stay aligned.
- You want a generated harness that leaves an audit trail: source map,
  assumptions, manifest, architecture, and validation report.

## When it is not useful

- A small one-off project only needs a short `AGENTS.md`.
- You only want a full-featured deterministic scaffold CLI. This project now has
  a small deterministic proof path, but the richer path is still Codex-driven.
- You need a compliance or policy engine. The harness can document and reinforce
  boundaries, but it is not a substitute for organization-level controls.
- You are not willing to run and maintain evals as Codex docs and APIs evolve.

## Quick Start

```bash
# 1. Download this repo
git clone https://github.com/daniel-p-green/Codex-Harness-Generator.git
cd Codex-Harness-Generator

# 2. Optional: install the local helper command
python -m pip install -e .
codex-harness --help
codex-harness doctor
codex-harness quickstart /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
codex-harness init /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
codex-harness validate /tmp/codex-rag-harness

# 3. Launch Codex in the directory
codex

# 4. Create a harness, then answer the prompts
/create
```

The create flow asks about your domain, tools, team shape, existing files, risk
tolerance, and how much autonomy Codex should have. It then writes a harness to
the path you choose.

## Fast Acceptance Test

Before trying the full model-mediated `/create` flow, generate a minimal valid
harness deterministically:

```bash
python scripts/codex_harness.py profiles
codex-harness profiles
codex-harness doctor
codex-harness inspect .
codex-harness quickstart /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
codex-harness init /tmp/codex-existing-project-harness \
  --from-project . \
  --project-name "Existing Project Harness" \
  --force
codex-harness adoption-plan . \
  --source-label "existing project" \
  --report /tmp/HARNESS_ADOPTION_PLAN.md \
  --blueprint-out /tmp/codex-existing-project-blueprint \
  --force-blueprint \
  --copy-script /tmp/copy-codex-harness-adds.sh
codex-harness init /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
codex-harness validate /tmp/codex-rag-harness
codex-harness local-eval /tmp/codex-rag-harness
python scripts/codex_harness.py profiles --details
python scripts/codex_harness.py recommend "RAG app with prompts, evals, and retrieval checks"
python scripts/codex_harness.py inspect .
python scripts/codex_harness.py init /tmp/codex-existing-project-harness \
  --from-project . \
  --project-name "Existing Project Harness" \
  --force
python scripts/codex_harness.py adoption-plan . \
  --source-label "existing project" \
  --report /tmp/HARNESS_ADOPTION_PLAN.md \
  --blueprint-out /tmp/codex-existing-project-blueprint \
  --force-blueprint \
  --copy-script /tmp/copy-codex-harness-adds.sh
python scripts/codex_harness.py profile security-audit
python scripts/codex_harness.py brief-acceptance /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
python scripts/codex_harness.py demo-capture /tmp/codex-demo-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
python scripts/codex_harness.py generate /tmp/codex-harness-example --force
python scripts/codex_harness.py validate /tmp/codex-harness-example
python scripts/codex_harness.py local-eval /tmp/codex-harness-example
python scripts/codex_harness.py eval /tmp/codex-harness-example
python scripts/codex_harness.py smoke /tmp/codex-harness-example
```

`adoption-plan` is non-destructive. It compares a generated harness blueprint to
an existing project and labels files as `add`, `conflict`, or `identical` so
project-local `AGENTS.md`, `.codex/config.toml`, and other existing guidance can
be merged by hand. When you pass `--blueprint-out` and `--copy-script`, it also
writes a persistent generated blueprint plus an executable script that copies
only `add` rows and refuses to overwrite existing project files. Conflict rows
still require manual review. The plan and copy script include post-adoption
checks for the generated self-check, copied local eval, and task-trial recorder.

To inspect an older harness before manually porting it to Codex-native files:

```bash
python scripts/codex_harness.py migration-audit /path/to/harness \
  --report /tmp/CODEX_MIGRATION_PLAN.md
```

The report lists legacy paths, missing Codex-native artifacts, legacy
tool/config wording, and a command sequence for generating a Codex blueprint
plus a non-destructive adoption plan. It also includes a cleanup checklist for
legacy paths to archive or remove after their useful content has been
translated.

The deterministic generator currently supports the four base starter profiles
and 16 bundled domain presets listed by:

```bash
python scripts/codex_harness.py profiles
```

This proves the repo can write valid Codex harnesses to disk across 20
first-class starting points and that the same evaluator used for fixtures
accepts them. The full `/create` flow remains the richer custom path.

Checked-in examples are available under `examples/deterministic/`. Refresh them
with:

```bash
python scripts/refresh_deterministic_examples.py
python scripts/codex_harness.py gate
```

To test the `/create` trigger handoff without launching a full live generation:

```bash
python scripts/simulate_create_trigger.py /tmp/codex-create-trigger-example \
  --project-type "Python CLI" \
  --notes "solo developer" \
  --json
```

This writes `Docs/Environment/CREATION_CONTEXT.md`, the artifact the orchestrator
uses before profile selection, architecture, generation, and validation.

To run the deterministic preset `/create` acceptance flow end to end:

```bash
python scripts/codex_harness.py acceptance /tmp/codex-create-acceptance \
  --profile software-development \
  --project-type "Python CLI" \
  --notes "release gate acceptance"
```

This writes the trigger context, generates the preset harness into the same
target, evaluates it, smoke-checks it, and records
`Docs/Environment/CREATE_ACCEPTANCE_REPORT.md`.

Checked-in create-acceptance examples are available under
`examples/create-acceptance/`. Refresh them with:

```bash
python scripts/refresh_create_acceptance_examples.py
python scripts/codex_harness.py gate
```

Checked-in brief-acceptance examples are available under
`examples/brief-acceptance/`. Refresh them with:

```bash
python scripts/refresh_brief_acceptance_examples.py
python scripts/codex_harness.py gate
```

To package a sanitized live `/create` output after it has passed eval and smoke:

```bash
python scripts/capture_live_create_example.py /tmp/codex-live-target \
  --capture-name synthetic-python-cli \
  --project-brief "Synthetic Python CLI utility for local file cleanup" \
  --project-type "Python CLI" \
  --notes "public-safe live-create capture" \
  --source-label "temporary synthetic target" \
  --force
```

The capture helper requires `Docs/Environment/CREATION_CONTEXT.md` by default so
live examples prove the `/create` handoff, not just a valid generated harness.

To prove checked-in live examples can steer Codex through representative tasks:

```bash
python scripts/codex_harness.py live-trials
```

This uses authenticated local Codex CLI access, copies each live example to a
temporary workspace, seeds synthetic inputs, runs `codex exec`, and writes
`examples/live-create/TASK_TRIALS.md`.

To record an eval trend snapshot:

```bash
python scripts/codex_harness.py snapshot
```

To check official OpenAI source freshness:

```bash
python scripts/codex_harness.py source-freshness
```

To check whether core local guidance still names the official Codex concepts it
depends on:

```bash
python scripts/codex_harness.py semantic-alignment
```

To record a sanitized usage case after a generated harness has been used on a
real or public-safe task:

```bash
python scripts/codex_harness.py usage-record \
  --slug example-real-task \
  --title "Example real task" \
  --domain "software development" \
  --harness-path "private-summary: client repo" \
  --task-summary "Public-safe summary of the task." \
  --outcome success \
  --evidence-type private-summary \
  --source-type external \
  --generation-path installed-quickstart \
  --evidence "Generated harness guided implementation and verification." \
  --evidence "Sanitized artifact checklist completed; raw evidence retained privately." \
  --verification "Tests passed; raw logs retained privately." \
  --verification "Expected task artifact was produced and reviewed." \
  --privacy-review "No secrets, personal data, proprietary source, or local paths included." \
  --limitation "Raw project files are private."
```

After recording task trials in a copied generated harness, refresh its local
eval report, export a review packet, and create a usage record from that local
evidence:

```bash
python scripts/codex_harness.py local-eval /tmp/codex-rag-harness
python scripts/codex_harness.py pilot-pack /tmp/codex-rag-harness \
  --domain "LLM app" \
  --slug rag-harness-trial \
  --title "RAG harness trial" \
  --harness-label "RAG harness private repo" \
  --source-type external \
  --generation-path installed-quickstart \
  --prefill-from-trials \
  --issue-out /tmp/EXTERNAL_USAGE_ISSUE_DRAFT.md
python scripts/codex_harness.py evidence-packet /tmp/codex-rag-harness \
  --harness-label "RAG harness private repo" \
  --out /tmp/HARNESS_EVIDENCE_PACKET.md
python scripts/codex_harness.py usage-from-harness /tmp/codex-rag-harness \
  --slug rag-harness-trial \
  --title "RAG harness trial" \
  --domain "LLM app" \
  --harness-label "RAG harness private repo" \
  --evidence-type private-summary \
  --source-type external \
  --generation-path installed-quickstart \
  --privacy-review "Private-summary evidence only; no secrets, personal data, private repository names, or raw logs." \
  --limitation "Single private task trial, not longitudinal proof" \
  --pilot-record-dir Docs/Environment/pilot-records \
  --pilot-board-report Docs/Environment/PILOT_BOARD.md \
  --no-write \
  --json
```

Use `--no-write --json` to preview copied-harness evidence before committing it.
When `--pilot-record-dir` points at a matching prepared pilot, copied-harness
conversion can infer title, domain, harness label, source type, and generation
path from the pilot record. Issue-body conversion can infer the slug from the
issue body and title plus fallback harness label, source type, and generation
path from the same pilot record. Provide those flags directly for standalone
conversions when the issue body or pilot record does not include them.
When an external usage report arrives through the GitHub issue template, save
the issue body and lint it before previewing the normalized record or writing
files:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --title "External RAG harness trial" \
  --lint-only \
  --json

python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --title "External RAG harness trial" \
  --no-write \
  --json
```

After reviewing the preview for concrete evidence, verification, privacy
boundaries, and limitations, rerun without `--no-write` to write the checked-in
record and refresh `Docs/Environment/USAGE_RECORDS.md`. If copied-harness or
issue-body evidence came from a prepared pilot with the same slug, add
`--pilot-record-dir Docs/Environment/pilot-records` to mark that pilot
`converted`, validate the usage-record reference, and refresh
`Docs/Environment/PILOT_BOARD.md` in the same run. The linked pilot path
prevalidates the pilot domain, source type, and generation path before writing
the usage record so mismatched evidence cannot leave a half-converted pilot.

Validate checked-in usage records before release:

```bash
python scripts/codex_harness.py usage-validate
```

Report what beta-exit usage evidence is still missing:

```bash
python scripts/codex_harness.py equivalence
python scripts/codex_harness.py usage-gaps
```

The report includes suggested pilot targets with starter `quickstart` or `init`
commands plus `pilot-pack` follow-up so maintainers can collect the next records
by profile, source type, and generation path instead of guessing. It also shows
whether the suggested candidates would satisfy beta-exit usage thresholds if
they become real converted evidence.

Write a shareable campaign packet from those gaps:

```bash
python scripts/codex_harness.py pilot-campaign
```

Write the exact next proof commands from those gaps:

```bash
python scripts/codex_harness.py proof-next
```

`proof-next` writes `Docs/Environment/PROOF_NEXT.md`. It packages the next
pilot target, candidate coverage projection, `prepare-next-pilot`,
`prepare-pilot-batch`, `pilot-board`, preview-first `usage-from-harness` and `usage-from-issue` conversion commands,
`beta-exit-audit`, and final `proof-status --beta-exit` commands while keeping
the claim boundary explicit: the packet is a plan, not usage proof. Use the
copied-harness route when the generated harness directory is available; use the
issue route when the reporter only shared the sanitized issue body.

To collect privacy-safe evidence from outside this repository, use the
**External usage report** GitHub issue template and
`Docs/Environment/EXTERNAL_USAGE_EVIDENCE.md`.

Require actual non-synthetic success evidence before making real-world usage
claims:

```bash
python scripts/codex_harness.py usage-validate \
  --min-records 2 \
  --require-non-synthetic \
  --require-success
```

Require beta-exit usage coverage before dropping the beta label:

```bash
python scripts/codex_harness.py usage-validate \
  --min-records 5 \
  --require-non-synthetic \
  --require-success \
  --min-external-or-multi-project 3 \
  --min-domains 4 \
  --min-installed-init-brief 2
```

The `--min-installed-init-brief` flag is retained for compatibility; it now
counts installed brief-based generation records from `codex-harness
prepare-next-pilot`, `codex-harness prepare-pilot`, `codex-harness quickstart`,
or `codex-harness init --brief`.

Summarize the checked-in product-proof package:

```bash
python scripts/codex_harness.py doctor
python scripts/codex_harness.py proof-status
python scripts/codex_harness.py proof-status --beta-exit
```

`doctor` is the fast first check for a local checkout. It verifies Python,
required public files, supported profiles, example inventory, usage evidence,
and the current proof-status report. Add `--include-install-smoke` before
publishing packaging or console-script changes.

The wrapper is intentionally thin. It delegates to the underlying scripts so
advanced users can still call `scripts/generate_minimal_harness.py`,
`scripts/run_create_acceptance.py`, `scripts/run_evals.py`, and the individual
evaluators directly.

## Commands

| Command | What it does |
|---|---|
| `/create` | Interviews you or uses a preset, designs the harness, generates files, and validates the output. |
| `/validate-environment` | Checks an existing harness for broken references, invalid config, missing metadata, weak skill triggers, and quality issues. |
| `/upgrade-environment` | Audits an existing harness and proposes improvements before making approved changes. |
| `/update` | Refreshes the generator's local knowledge base from web research or `Docs/ProvideKnowledge/` in local-only mode. |

## Script Entry Point

For local CLI use before or alongside Codex, start with:

```bash
python -m pip install -e .
codex-harness --help
```

If you do not want to install the helper command, call the wrapper directly:

```bash
python scripts/codex_harness.py --help
```

Common subcommands:

| Subcommand | Delegates to | What it proves |
|---|---|---|
| `quickstart <target>` | `run_quickstart.py` | Generates from a brief, validates the harness, runs the copied local eval, and writes `QUICKSTART_REPORT.md`. |
| `prepare-pilot <target>` | `prepare_pilot.py` | Generates and validates a pilot harness from a brief, then writes an external pilot pack and issue-body draft for the reporter. |
| `prepare-next-pilot [target]` | `prepare_next_pilot.py` | Selects a suggested pilot from current usage gaps and prepares its generated harness plus evidence kit. |
| `init <target>` | `generate_minimal_harness.py` or `run_brief_acceptance.py` | One-command starter path; add `--brief` to recommend a profile and record `PROFILE_SELECTION.md`. |
| `init <target> --from-project <path>` | `run_inspected_acceptance.py` | Inspects project metadata, generates through deterministic acceptance, and records `PROJECT_INSPECTION.md`. |
| `profiles` | `generate_minimal_harness.py --list-profiles` or `profile_catalog.py` | Shows supported deterministic starters; add `--details` or `--json` for a chooser-friendly catalog. |
| `profile <slug>` | `profile_catalog.py` | Describes one deterministic starter, including first tasks and domain guardrails. |
| `recommend <brief>` | `profile_catalog.py` | Recommends deterministic starters from a short project brief using explainable keyword matches, confidence labels, and low-confidence guidance. |
| `inspect <path>` | `inspect_project.py` | Scans project metadata and recommends deterministic starters before generation. |
| `adoption-plan <path>` | `plan_project_adoption.py` | Builds a non-destructive file-by-file plan and optional add-only copy script for adopting a generated harness into an existing project. |
| `generate <target>` | `generate_minimal_harness.py` | Writes a minimal valid Codex harness. |
| `acceptance <target>` | `run_create_acceptance.py` | Runs trigger handoff, generation, eval, smoke, and report writing. |
| `brief-acceptance <target>` | `run_brief_acceptance.py` | Recommends a profile from a brief, runs deterministic acceptance, and records `PROFILE_SELECTION.md`. |
| `eval <paths...>` | `eval_generated_harness.py` | Checks generated harness contract quality. |
| `smoke <paths...>` | `smoke_generated_harness.py` | Parses config, resolves agents and skills, optionally runs Codex live smoke. |
| `validate <paths...>` | `validate_generated_harness.py` | Runs eval, offline smoke, and the generated local self-check together. |
| `local-eval <path>` | generated `scripts/run-harness-evals.py` | Runs the copied harness's embedded eval report without depending on this generator repo. |
| `migration-audit <paths...>` | `migration_audit.py` | Audits legacy harness artifacts and writes an optional Codex migration plan report. |
| `gate` | `run_evals.py` | Runs the repo release gate. |
| `refresh-examples` | `refresh_generated_surfaces.py` | Refreshes checked-in generated fixtures and example families from the current generator, then runs the example inventory contract check. |
| `live-trials` | `run_live_example_task_trials.py` | Runs authenticated Codex tasks against checked-in live examples. |
| `source-freshness` | `check_source_freshness.py` | Confirms official OpenAI source URLs are reachable. |
| `semantic-alignment` | `check_semantic_alignment.py` | Checks local guidance against official Codex doc concepts. |
| `equivalence` | `check_codex_equivalence.py` | Checks and writes the Codex-native equivalence matrix. |
| `upstream-drift` | `check_upstream_drift.py` | Reports divergence from the source upstream ref without treating drift status as product proof. |
| `usage-record` | `record_usage_case.py` | Records sanitized generated-harness usage evidence. |
| `usage-from-harness` | `usage_from_harness.py` | Converts copied-harness task trials and eval reports into a privacy-checked usage record; add `--no-write` to preview first or `--pilot-record-dir` to prevalidate and convert a matching prepared pilot. |
| `evidence-packet <path>` | `export_evidence_packet.py` | Exports a public-safe Markdown evidence packet from copied-harness local eval and task trials. |
| `pilot-pack <path>` | `export_pilot_pack.py` | Writes an external pilot guide and optional GitHub issue-body draft for one privacy-safe generated-harness trial. |
| `pilot-campaign` | `export_pilot_campaign.py` | Writes a shareable external-pilot campaign plan and listed-pilot coverage projection from current usage evidence gaps. |
| `prepare-pilot-batch` | `prepare_pilot_batch.py` | Dry-runs or prepares the suggested beta-exit pilot batch under one target root, with optional pilot-board records. |
| `pilot-board` | `pilot_board.py` | Summarizes prepared pilot records and cross-checks converted pilots against usage records without counting outreach as proof. |
| `pilot-update <slug>` | `pilot_board.py` | Updates one prepared pilot's status, validates converted usage-record references, and refreshes the pilot board. |
| `beta-exit-audit` | `beta_exit_audit.py` | Writes a non-gating audit of beta-exit readiness and remaining evidence gaps. |
| `proof-next` | `proof_next.py` | Writes the next beta-exit proof actions and candidate coverage projection from current usage gaps without counting the plan as evidence. |
| `usage-from-issue` | `usage_from_issue.py` | Converts a sanitized external-usage issue body into a privacy-checked usage record; infers the slug from the issue body when present, and supports `--lint-only`, `--no-write`, or `--pilot-record-dir` for linked pilot conversion. |
| `usage-validate` | `validate_usage_records.py` | Validates checked-in usage evidence schema, privacy checks, and optional non-synthetic proof thresholds. |
| `usage-gaps` | `usage_gaps.py` | Reports remaining beta-exit usage evidence gaps and writes `Docs/Environment/USAGE_GAPS.md`. |
| `proof-status` | `proof_status.py` | Summarizes checked-in proof readiness, live task-trial coverage, and usage evidence; add `--beta-exit` to apply the roadmap exit thresholds. |
| `doctor` | `doctor.py` | Runs a fast local readiness check and prints the next useful commands. |
| `snapshot` | `record_eval_snapshot.py` | Records an eval trend snapshot. |

## Presets

The intake supports a fast preset path and a custom path. Presets live in:

- `Docs/StarterProfiles/` for base profiles: software development, knowledge
  work, data and analysis, DevOps and infrastructure.
- `Docs/DomainLibrary/` for bundled domains: API design, book publishing,
  course design, customer support, data engineering, data science, financial
  modeling, game development, grant writing, hiring pipeline, legal research,
  LLM app work, market research, product management, security audit, and social
  media.

Custom mode runs a deeper interview and writes a reusable domain profile for the
target environment.

## What Gets Generated

```text
your-project/
|-- AGENTS.md
|-- .codex/
|   |-- config.toml
|   |-- rules/
|   |-- agents/
|-- .agents/
|   |-- skills/
|-- Docs/
|   |-- GETTING_STARTED.md
|   |-- Environment/
|   |   |-- GENESIS.md
|   |   |-- ARCHITECTURE.md
|   |   |-- ASSUMPTIONS.md
|   |   |-- MANIFEST.md
|   |   |-- EVAL_PLAN.md
|   |   |-- EVAL_REPORT.md
|   |   |-- IMPROVEMENT_LOG.md
|   |   |-- TASK_TRIALS.md
|   |   |-- SOURCE_MAP.md
|   |   |-- VALIDATION_REPORT.md
|-- scripts/
|   |-- check-harness.py
|   |-- run-harness-evals.py
|   |-- record-improvement.py
|   |-- record-task-trial.py
|   |-- summarize-improvements.py
|   |-- summarize-task-trials.py
|   |-- export-public-usage-report.py
|-- Memory/
|-- State/
|-- Retro/
```

The exact file set depends on the project. The important contract is that the
generated harness should be explicit about why each component exists, what was
assumed, which sources informed it, and how to validate it.

## Architecture

The repo uses a Codex orchestrator plus five configured agents:

- `intake-interviewer`: gathers project context when presets do not fit.
- `environment-architect`: turns intake into a component manifest, routing plan,
  assumptions ledger, and architecture record.
- `component-generator`: writes the harness in focused passes.
- `environment-validator`: checks the generated environment against the
  validation guide and writes `VALIDATION_REPORT.md`.
- `upgrade-analyzer`: reviews an existing harness and proposes improvements.

The core design is artifact-first. Important intermediate decisions are written
to `Docs/Environment/` instead of living only in chat context.

## Quality Gates

Run the full local gate before publishing changes:

```bash
python scripts/run_evals.py
```

This runs:

- Static Codex port checks.
- Generated-harness fixture evaluation.
- Offline smoke checks for generated harnesses.
- Deterministic profile generation, evaluation, and smoke checks.
- Brief-based deterministic acceptance tests.
- Checked-in deterministic, create-acceptance, and brief-acceptance example
  inventory checks.
- Checked-in deterministic example evaluation and smoke checks.
- `/create` trigger contract tests for CREATION_CONTEXT.md handoff scenarios.
- Deterministic preset `/create` acceptance flow with final eval and smoke.
- Checked-in create-acceptance example evaluation and smoke checks.
- Checked-in brief-acceptance example evaluation and smoke checks.
- Checked-in live-create example evaluation and smoke checks when live captures
  exist.
- Live-create capture helper tests.
- Live-create task-trial helper tests. Authenticated maintainers can run the
  full task trials separately with `python scripts/run_live_example_task_trials.py`.
- Eval trend snapshot helper tests.
- Source freshness helper tests. Maintainers can run the live source check with
  `python scripts/check_source_freshness.py`.
- Contract and mutation tests.
- Python compile checks.

The evals prove structural and contract quality against golden fixtures and the
deterministic profile generator, including checked-in examples. They do not
prove that every live `/create` run will be perfect, so meaningful changes should
still be reviewed against generated artifacts.

The proof matrix in `Docs/Environment/PROOF_MATRIX.md` maps each major claim to
the artifact and command that verifies it.

For an authenticated local Codex CLI check against a generated harness, run:

```bash
python scripts/run_evals.py --codex-live
```

By default this adds one live smoke check against
`examples/create-acceptance/software-development`. Use
`--codex-live-profile all` to run live smoke against every checked-in
create-acceptance profile.

## Project Structure

```text
Codex-Harness-Generator/
|-- AGENTS.md
|-- .codex/
|   |-- config.toml
|   |-- agents/
|   |-- rules/
|-- .agents/
|   |-- skills/
|-- Docs/
|   |-- AgentGuidelines/
|   |-- AgentPlaybooks/
|   |-- DomainLibrary/
|   |-- StarterProfiles/
|   |-- Templates/
|   |-- Environment/
|-- scripts/
|-- tests/
```

## Value Assessment

The project is valuable for serious Codex users, workshop/demo contexts, and
teams that care about repeatable setup, reviewable local artifacts, and
validation discipline. Its strongest utility is compressing a lot of Codex
configuration knowledge into a guided workflow while leaving enough files on disk
for inspection and improvement.

It is not yet a mainstream public product. The main limitation is that generation
is model-mediated and the current evidence is mostly structural. The repo should
be judged by generated examples, output contracts, eval coverage, and maintenance
loop, not by an assumption that the first generated harness is always ideal.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add profiles, bundled domains,
templates, docs, and eval coverage.

## License

MIT. See [LICENSE](LICENSE).
