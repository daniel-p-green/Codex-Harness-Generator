# Component Manifest

Single source of truth for the Codex Harness Generator's own component
inventory. **Do not hardcode these counts elsewhere.** `README.md`,
`OVERVIEW.md`, `USER_GUIDE.md`, and the `INDEX.md` files reference this file
instead of repeating numbers.

Harness Generator version: see `Docs/Environment/VERSION.md`.

> Maintenance: when a component is added or removed, update the affected row
> here in the same commit. The numbers below describe the Harness Generator
> itself, not the environments it generates.

## Counts

| Component class | Count | Location |
|---|---|---|
| Agents | 5 | `.codex/agents/` |
| Skills | 4 | `.agents/skills/` |
| Rules | 4 | `.codex/rules/` |
| Knowledge topics | 18 | `Docs/AgentGuidelines/Topics/` (non-contiguous numbering; gaps are reserved) |
| Agent playbooks | 6 (+INDEX) | `Docs/AgentPlaybooks/` |
| Base starter profiles | 4 (+INDEX, PROFILE_FORMAT, DOMAIN_REFERENCE) | `Docs/StarterProfiles/` |
| Bundled domain presets | 16 (+INDEX) | `Docs/DomainLibrary/` |
| Environment records | 5 (+MANIFEST) | `Docs/Environment/` |
| Template files | 52 | `Docs/Templates/` (incl. README) |

## Agents (5)

| Name | Model | Role |
|---|---|---|
| intake-interviewer | medium-effort | Deep 5-stage interview when no profile fits (relay protocol) |
| environment-architect | high-effort | Designs ARCHITECTURE.md from GENESIS.md + knowledge base |
| component-generator | high-effort | Writes environment files, one of 5 passes per invocation |
| environment-validator | medium-effort | Runs the validation checklist; read-only w.r.t. the environment |
| upgrade-analyzer | high-effort | Audits an existing environment against best practices (review-grade reasoning) |

## Skills (4)

| Name | Audience | Role |
|---|---|---|
| create | user | Trigger the /create pipeline |
| validate-environment | user | Structural + quality validation of an environment |
| upgrade-environment | user | Best-practice audit + approved improvements |
| update | user | Refresh the Harness Generator's knowledge base (web research + ProvideKnowledge/ ingest; local-only mode skips web) |

## Rules (4)

`00-creator-core.md` (routing + handoff + context discipline),
`01-intake-protocol.md`, `02-generation-standards.md`, `03-quality-gates.md`.

## Template files by category (52)

| Category | Count | Path |
|---|---|---|
| Core | 16 | `Docs/Templates/Core/` |
| Optional | 12 | `Docs/Templates/Optional/` (incl. authorization-scope-rule, adverse-decision-rule) |
| Agents | 9 | `Docs/Templates/Agents/` |
| Skills | 6 | `Docs/Templates/Skills/` |
| References | 8 | `Docs/Templates/References/` (incl. ecosystem-permissions.md) |
| README | 1 | `Docs/Templates/README.md` |

## Knowledge topics (18)

Topics use non-contiguous numbering. Active numbers: 00, 01, 02, 03, 04, 05,
07, 08, 10, 11, 12, 13, 15, 16, 18, 20, 21, 23; the gaps (06, 09, 14, 17, 19,
22, 24, 25) are reserved. Indexed by `Docs/AgentGuidelines/INDEX.md`.

## Base starter profiles (4)

software-development, knowledge-work, data-analysis, devops-infrastructure (all
slim, ~110-170 lines, per `PROFILE_FORMAT.md`). Indexed by
`Docs/StarterProfiles/INDEX.md`.

## Bundled domain presets (16)

api-design, book-publishing, course-design, customer-support, data-engineering,
data-science, financial-modeling, game-development, grant-writing,
hiring-pipeline, legal-research, llm-app, market-research, product-management,
security-audit, social-media. Indexed by `Docs/DomainLibrary/INDEX.md`; routing
help in `StarterProfiles/DOMAIN_REFERENCE.md`.
