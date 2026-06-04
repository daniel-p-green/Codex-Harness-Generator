# Quality gates

Validation happens at three points: before generation, during file writes, and
after generation. Each gate prevents a specific class of failure.

The full post-generation checklist is NOT enumerated in this rule. It lives in
`Docs/Templates/References/validation-guide.md` -- the single source of truth
(core, conditional, and hub checks). This rule states the gate
*contract*; the validator agent and the validation guide carry the detail.
Do not re-list the checks here; keep the validation guide the single source of truth.

## Gate 1: Pre-generation checks

Before writing any files to the target directory:

1. **Directory writability**: create and delete a temp file; stop and report if it fails.
2. **Existing files**: if `.codex/` or `AGENTS.md` exists, warn and offer backup / overwrite / cancel.
3. **Disk space**: verify reasonable free space on the target drive.

## Gate 2: File preview gate

Before writing: present the full file tree, show component counts (N rules, N
agents, N skills), and ask "Ready to generate these files?" Proceed only on
confirmation.

## Gate 3: Post-generation validation

The environment-validator runs every applicable check from the validation guide
and writes `VALIDATION_REPORT.md`. Checks are tiered by severity:

| Tier | Meaning | Effect |
|---|---|---|
| Blocking | Structural breakage; the environment will not work | FAIL gates release |
| Critical | Logic/consistency defect; works but misbehaves | FAIL gates release |
| Advisory | Quality/UX improvement | WARN; does not gate |
| Conditional | Applies only when its GENESIS/ARCHITECTURE trigger is present | Run when triggered |

On FAIL: the orchestrator delegates targeted fixes to component-generator, then
re-runs the validator. Maximum 2 fix-and-revalidate cycles. The validator is
read-only; it never fixes issues itself.

Boundary-crossing checks catch what existence checks miss: 16b
cross-validates the ARCHITECTURE.md Component Manifest against files actually
written (planned-but-not-written, or written-but-unplanned); 16c verifies the
environment MANIFEST.md entries actually exist on disk; 20b confirms the GENESIS
domain vocabulary actually appears in the generated AGENTS.md (intake absorbed,
not generic).

## Skill description quality bar

Every generated skill description must: be 80-1024 characters, use third person
("Captures state..." not "I capture..."), include 3+ trigger phrases, include
2-3 near-miss negative triggers (phrases where a sibling skill or a built-in
could confusably fire), and follow [What] + [When/triggers] + [Capabilities].
Verified by check 3 and the skill triggering tests.

## 3-tier grading methodology

| Tier | Method | Catches |
|---|---|---|
| Code-based (structural) | Script checks: file existence, JSON validity, size limits | Missing files, malformed config, bloat |
| LLM-based (semantic) | Validator reads content for contradictions, gaps, jargon drift | Inconsistent rules, incomplete routing, dead references |
| Human (functional) | User runs the smoke test | Wrong behavior, confusing UX, missing permissions |

Tiers 1 and 2 run automatically (the validator). Tier 3 is the smoke test
presented to the user. The functional test scenarios, the smoke-test template,
and the edge-case checklist (empty state, path/encoding, permission boundaries,
scale appropriateness, content freshness) live in
`Docs/AgentPlaybooks/EnvironmentValidation.md`.
