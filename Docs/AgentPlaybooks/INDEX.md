# Agent Playbooks Index

Executable process guides loaded into agent context on demand.
Unlike AgentGuidelines/Topics/ (reference knowledge as individual topic files), playbooks are
step-by-step procedures that agents follow during specific operations.

Last Updated: 2026-05-31

## Playbooks

| File | Loaded By | Purpose |
|------|-----------|---------|
| OrchestratorWorkflow.md | orchestrator | Detailed /create and /upgrade-environment pipeline choreography (hub detection, architecture-confirmation sub-steps, shape conversions, progress reporting). AGENTS.md holds the high-level step list. |
| IntakeChecklist.md | orchestrator, intake-interviewer | Step-by-step intake protocol: profile-first + deep interview paths, work-area shape (incl. "not sure" branch), preset-vs-custom flow, question relay protocol, GENESIS.md format, validation criteria, edge cases |
| EnvironmentValidation.md | environment-validator | Functional test scenarios, smoke-test template, and edge-case checklist. The check list itself is the SoT in validation-guide.md (referenced, not duplicated). |
| ComponentQuality.md | component-generator, environment-validator | Quality standards per component type, file size limits, include/exclude rubrics, anti-overengineering checks |
| UpgradeChecklist.md | upgrade-analyzer | 28-item best-practice audit protocol (6 parts including Environment Shape P6), user pain point mapping, recommendation prioritization, conflict detection |
| HubPipelineTests.md | developer (manual) | 8 end-to-end walkthrough scenarios for verifying hub creation, add-area, convert-to-hub, collapse-to-single, declare-hub, budget overflow, cross-area routing, and resume-after-interrupt |

## Usage

Playbooks are NOT loaded into the orchestrator's main context (too large).
They are passed to agents via the Codex subagent tools prompt or read by agents at the
start of their execution.

- Orchestrator loads OrchestratorWorkflow.md when running a /create or /upgrade pipeline.
- Orchestrator loads IntakeChecklist.md only during /create intake phase.
- component-generator loads ComponentQuality.md at the start of each generation pass.
- environment-validator loads EnvironmentValidation.md at the start of validation.
- environment-validator also loads ComponentQuality.md for quality criteria reference.
- upgrade-analyzer loads UpgradeChecklist.md at the start of upgrade analysis.
