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
- `scripts/inspect_project.py` and `codex-harness inspect` scan local project
  metadata such as config filenames, top-level directories, and extensions to
  recommend deterministic starter profiles before generation.
- `codex-harness init --from-project` turns that metadata inspection into a
  generated harness and records `Docs/Environment/PROJECT_INSPECTION.md` inside
  the output.
- `examples/create-acceptance/` contains checked-in snapshots of that
  deterministic preset `/create` acceptance flow for every supported profile and
  bundled domain preset.
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
  profile listing, profile descriptions, project inspection, generation,
  inspected generation, acceptance, eval, smoke, copied local eval reports,
  migration audit, evidence-packet, gate, demo-capture, live-trial,
  source-freshness, and snapshot workflows.
- `pyproject.toml` exposes that wrapper as an installable `codex-harness`
  console command, and the release gate smokes the non-editable install path.
- `scripts/record_eval_snapshot.py` records eval-gate snapshots under
  `Docs/Environment/eval-history/` and updates `Docs/Environment/EVAL_TRENDS.md`.
- `scripts/check_source_freshness.py` verifies official OpenAI documentation
  citations are still reachable and writes `Docs/Environment/SOURCE_FRESHNESS.md`.
- `scripts/check_semantic_alignment.py` checks that key local guidance still
  names the core concepts present in official Codex docs and writes
  `Docs/Environment/SEMANTIC_ALIGNMENT.md`.
- `scripts/record_usage_case.py` provides a privacy-checked path for recording
  sanitized real-world or private-summary usage evidence under
  `Docs/Environment/usage-records/`, and `scripts/validate_usage_records.py`
  can enforce stricter non-synthetic proof thresholds when making real-world
  usage claims.
- `scripts/usage_from_harness.py` and `codex-harness usage-from-harness`
  convert a generated harness's local eval report and task trials into a
  privacy-checked usage record.
- `scripts/export_evidence_packet.py` and `codex-harness evidence-packet`
  write a public-safe Markdown packet from a copied harness's local eval report
  and task trials before maintainers decide whether a usage record is justified.
- `scripts/usage_from_issue.py` and `codex-harness usage-from-issue` convert a
  sanitized GitHub external-usage issue body into a privacy-checked usage
  record.
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
still require manual review.

To inspect an older harness before manually porting it to Codex-native files:

```bash
python scripts/codex_harness.py migration-audit /path/to/harness
```

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
python scripts/codex_harness.py evidence-packet /tmp/codex-rag-harness \
  --harness-label "RAG harness private repo" \
  --out /tmp/HARNESS_EVIDENCE_PACKET.md
python scripts/codex_harness.py usage-from-harness /tmp/codex-rag-harness \
  --slug rag-harness-trial \
  --title "RAG harness trial" \
  --domain "LLM app" \
  --harness-label "RAG harness private repo" \
  --evidence-type private-summary \
  --privacy-review "Private-summary evidence only; no secrets, personal data, private repository names, or raw logs." \
  --limitation "Single private task trial, not longitudinal proof" \
  --json
```

When an external usage report arrives through the GitHub issue template, save
the issue body and convert it directly:

```bash
python scripts/codex_harness.py usage-from-issue /tmp/external-usage-issue.md \
  --slug external-rag-trial \
  --title "External RAG harness trial" \
  --json
```

Validate checked-in usage records before release:

```bash
python scripts/codex_harness.py usage-validate
```

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

Summarize the checked-in product-proof package:

```bash
python scripts/codex_harness.py doctor
python scripts/codex_harness.py proof-status
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
| `migration-audit <paths...>` | `migration_audit.py` | Audits legacy harness artifacts and lists the Codex-native migration work. |
| `gate` | `run_evals.py` | Runs the repo release gate. |
| `live-trials` | `run_live_example_task_trials.py` | Runs authenticated Codex tasks against checked-in live examples. |
| `source-freshness` | `check_source_freshness.py` | Confirms official OpenAI source URLs are reachable. |
| `semantic-alignment` | `check_semantic_alignment.py` | Checks local guidance against official Codex doc concepts. |
| `usage-record` | `record_usage_case.py` | Records sanitized generated-harness usage evidence. |
| `usage-from-harness` | `usage_from_harness.py` | Converts copied-harness task trials and eval reports into a privacy-checked usage record. |
| `evidence-packet <path>` | `export_evidence_packet.py` | Exports a public-safe Markdown evidence packet from copied-harness local eval and task trials. |
| `usage-from-issue` | `usage_from_issue.py` | Converts a sanitized external-usage issue body into a privacy-checked usage record. |
| `usage-validate` | `validate_usage_records.py` | Validates checked-in usage evidence schema, privacy checks, and optional non-synthetic proof thresholds. |
| `proof-status` | `proof_status.py` | Summarizes checked-in proof readiness, live task-trial coverage, and usage evidence. |
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
