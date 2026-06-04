# Codex Harness Generator

**v1.0.0** | Built for Codex GPT-5.5 (`gpt-5.5`) | MIT

Codex Harness Generator helps you create and validate a project-specific Codex
harness: `AGENTS.md`, `.codex/config.toml`, `.codex/agents/`, `.agents/skills/`,
rules, memory scaffolding, setup docs, validation records, and a small
self-improvement loop.

A harness is the operating layer around a project. It tells Codex what the
project is, which files matter, which subagents and skills exist, what can be
changed safely, how to save state, and how to verify the setup over time.

[![Tutorial Video](https://img.youtube.com/vi/0R3JPNTEljU/0.jpg)](https://www.youtube.com/watch?v=0R3JPNTEljU)

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
- You want a deterministic scaffold CLI. This project is primarily a Codex-driven
  generation workflow with deterministic eval scripts around it.
- You need a compliance or policy engine. The harness can document and reinforce
  boundaries, but it is not a substitute for organization-level controls.
- You are not willing to run and maintain evals as Codex docs and APIs evolve.

## Quick Start

```bash
# 1. Download this repo
git clone https://github.com/daniel-p-green/Codex-Harness-Generator.git
cd Codex-Harness-Generator

# 2. Launch Codex in the directory
codex

# 3. Create a harness, then answer the prompts
/create
```

The create flow asks about your domain, tools, team shape, existing files, risk
tolerance, and how much autonomy Codex should have. It then writes a harness to
the path you choose.

## Commands

| Command | What it does |
|---|---|
| `/create` | Interviews you or uses a preset, designs the harness, generates files, and validates the output. |
| `/validate-environment` | Checks an existing harness for broken references, invalid config, missing metadata, weak skill triggers, and quality issues. |
| `/upgrade-environment` | Audits an existing harness and proposes improvements before making approved changes. |
| `/update` | Refreshes the generator's local knowledge base from web research or `Docs/ProvideKnowledge/` in local-only mode. |

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
    |-- GETTING_STARTED.md
    |-- Environment/
    |   |-- GENESIS.md
    |   |-- ARCHITECTURE.md
    |   |-- ASSUMPTIONS.md
    |   |-- MANIFEST.md
    |   |-- SOURCE_MAP.md
    |   |-- VALIDATION_REPORT.md
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
- Contract and mutation tests.
- Python compile checks.

The evals prove structural and contract quality against golden fixtures. They do
not prove that every live `/create` run will be perfect, so meaningful changes
should still be reviewed against generated artifacts.

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

The project is valuable when the user cares about repeatable Codex setup,
reviewable local artifacts, and validation discipline. Its strongest utility is
compressing a lot of Codex configuration knowledge into a guided workflow while
leaving enough files on disk for inspection and improvement.

The main limitation is that generation is model-mediated. The repo should be
judged by its output contracts, eval coverage, and maintenance loop, not by an
assumption that the first generated harness is always ideal.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add profiles, bundled domains,
templates, docs, and eval coverage.

## License

MIT. See [LICENSE](LICENSE).
