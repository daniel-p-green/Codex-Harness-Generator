# Agent Guidelines Index

Reference documents for Claude Code environment design and generation.
This is the ONLY file loaded by default. Agents load specific topic files on demand.

Last Updated: 2026-05-31

## Documents

| File | Description |
|------|-------------|
| Topics/*.md | 18 topic files. Numbering is non-contiguous: gaps (6, 9, 14, 17, 19, 22, 24, 25) are unused. |
| ../Templates/References/tool-registry.md | Centralized registry of all third-party tools with per-tool metadata, matching rules, verification dates, and deprecation tracking |
| ../Templates/References/architecture-guide.md | Architecture section templates, patterns (A-I), output format, and quality gates for the environment-architect agent |
| ../Templates/References/component-generator-guide.md | Detailed pass descriptions, template references, and generation patterns for the component-generator agent |

## Topic Map

Model-Scope markers inside topics: `[ALL]` applies to every supported model;
`[4.7+]` applies to Opus 4.7 and 4.8; `[4.6 ONLY]` is retained legacy guidance.

| # | File | Topic | Key Takeaway |
|---|------|-------|-------------|
| 0 | 00-appendix.md | Appendix | Cross-cutting references, glossary, source index |
| 1 | 01-rules.md | Rules | CLAUDE.md < 250 lines; intent behind every rule; .claude/rules/ for modularity |
| 2 | 02-agents.md | Agents | 5-element delegation; always set maxTurns; model selection (opus/sonnet/haiku) |
| 3 | 03-skills.md | Skills | Progressive disclosure; 3+ triggers; pipeline skills (3.11); CLI wrapping (3.12) |
| 4 | 04-teams.md | Teams, Parallelism & Patterns | Subagents default, teams ~15x; parallel file ops + worktrees; the 6 team-architecture patterns (Pipeline, Fan-out/Fan-in, Expert Pool, Producer-Reviewer, Supervisor, Hierarchical Delegation) |
| 5 | 05-memory.md | Memory, Context & State | Tiered memory (INDEX.md only default); compaction ~95% + pressure detection; 6-category state taxonomy + save/load symmetry; PKM/memory plugins |
| 7 | 07-self-learning.md | Self-Learning | Evaluation-driven cycle; seed 3-5 patterns; track trigger accuracy |
| 8 | 08-routing.md | Routing | XML classification; domain-specific entries; fallback chains |
| 10 | 10-integration.md | Integration & MCP | Pre-approve safe VCS; verification commands #1 priority; MCP transports, .mcp.json scope, qualified names, Tool Search (10.11) |
| 11 | 11-permissions.md | Permissions | deny->ask->allow; dual isolation; enterprise managed settings |
| 12 | 12-user-experience.md | User Experience | First-run onboarding; plain language; GETTING_STARTED.md in every env |
| 13 | 13-opus-specifics.md | Opus Model & Prompt Eng | 4.8 flagship (claude-opus-4-8, default); literal instructions; xhigh effort; no temperature/top_p/top_k; adaptive thinking only; XML tags + few-shot prompting |
| 15 | 15-testing-validation.md | Testing, Validation & QA | 3-tier grading; investigate-first; QA boundary-crossing (existence vs connection); near-miss trigger tests + with/without A/B skill eval |
| 16 | 16-hook-system.md | Hooks | 20+ events; exit code 2; PreToolUse allow/deny/defer; compliance hooks (16.9); May 2026 I/O additions (16.11) |
| 18 | 18-cost-awareness.md | Cost & Tokens | Subagents ~4x, teams ~15x; effort levels; --max-budget-usd; Fast Mode; RTK; .claudeignore; CLAUDE.md budget |
| 20 | 20-plugins.md | Plugins | Marketplace install; anthropics/skills repo; intake signal matching |
| 21 | 21-rag-strategies.md | RAG & Documents | Agentic/hybrid/hierarchical retrieval by codebase size; staleness watermarks; PaddleOCR/MinerU/Docling document pipeline |
| 23 | 23-multi-modal.md | Multi-Modal | Budget tiers; AI capability gap detection (23.3); guided selection (23.4) |

## Learning Path (suggested reading order)

- **Foundation**: 01-rules, 02-agents, 03-skills, 08-routing, 11-permissions, 12-user-experience
- **Architecture**: 04-teams, 05-memory, 07-self-learning, 10-integration, 16-hooks, 20-plugins
- **Advanced**: 13-opus-specifics, 15-testing-validation, 18-cost-awareness, 21-rag-strategies, 23-multi-modal, 00-appendix

## Agent Loading Guide

Which topic files each agent should load (load ONLY what's needed):

### Environment Architect
Load all 18 topics + tool-registry.md + architecture-guide.md.
The architect needs comprehensive knowledge to design the environment.

### Component Generator
Load by pass:
- **Pass 1 (Foundation)**: 01-rules, 05-memory, 08-routing, 11-permissions, 13-opus-specifics, 16-hooks, 18-cost-awareness
- **Pass 2 (Agents)**: 02-agents, 13-opus-specifics, 18-cost-awareness
- **Pass 3 (Skills)**: 03-skills, 20-plugins
- **Pass 4 (Infrastructure)**: 05-memory, 07-self-learning, 21-rag-strategies, 15-testing-validation
- **Pass 5 (Documentation)**: 10-integration, 12-user-experience, 21-rag-strategies, 23-multi-modal, 18-cost-awareness, tool-registry.md

### Environment Validator
Load: 01-rules, 02-agents, 03-skills, 08-routing, 11-permissions, 15-testing-validation, 16-hooks, 18-cost-awareness, 20-plugins.
Cross-reference against quality gates in 02-generation-standards rule and validation-guide.md.

### Intake Interviewer
Load: 08-routing, 11-permissions, 12-user-experience, 23-multi-modal.
Reference tool-registry.md for AI ecosystem extension probes.

### Upgrade Analyzer
Load all 18 topics (needs comprehensive knowledge like architect).
Also load tool-registry.md for tool currency checks.

### /update Skill
Load tool-registry.md for Step 3b (tool verification).
Load specific topic files only when updating that topic.
