# Environment Validation Playbook

Loaded by the environment-validator agent. Contains the full validation
checklist, skill triggering tests, functional test scenarios, and smoke
test template.

The validator agent runs this checklist against a generated environment
and produces a validation report.

---

## Validation Report Format

Write the report to `<target>/Docs/Environment/VALIDATION_REPORT.md`:

```markdown
# Validation Report

Generated: YYYY-MM-DD HH:MM
Environment: <target path>
Overall: PASS | WARN | FAIL

## Summary
- Checks passed: NN (core + applicable conditional + hub)
- Warnings: NN
- Failures: NN

## Results
[Per-check results]

## Skill Triggering Tests
[Results per skill]

## Functional Tests
[Results per skill]

## Recommendations
[Ordered list of fixes needed]
```

---

## Validation checklist

The full check list is the single source of truth in
`Docs/Templates/References/validation-guide.md` (55 checks: 22 core + 27
conditional + 6 hub, with verdict logic and report format). Do not re-list the
checks here. Run them per that guide. For each skill, generate domain-appropriate
triggering test sets -- 3 obvious + 2 paraphrased + 2-3 near-miss negative
triggers (phrases where a sibling skill or built-in could confusably fire) --
per checks 3 and 22.

This playbook holds only what the guide does not: functional test scenarios, the
user smoke-test template, and the edge-case checklist.

---

## Functional Test Scenarios

For each core skill, define at least one functional test scenario. These
cannot be run automatically -- they are presented to the user as smoke test
instructions.

### /state-save Functional Test

**Setup**: Have some working context (at least one file read, one task discussed).
**Action**: Run /state-save.
**Expected**:
- `Docs/_working/state/SESSION_SNAPSHOT.json` is created with valid JSON
- `Docs/_working/state/SESSION_CONTEXT.md` is created with human-readable narrative
- JSON contains keys for all 6 taxonomy categories
- No errors or permission prompts during execution

**Verify**: Read both files. JSON should parse cleanly. Markdown should
describe the current session state accurately.

### /state-load Functional Test

**Setup**: Have a SESSION_SNAPSHOT.json from a previous /state-save.
**Action**: Run /state-load (ideally after /clear or in a new session).
**Expected**:
- Assistant reads both state files
- Presents a context restoration briefing
- Notes any drift (files changed since snapshot)
- Does not modify any files (read-only)

**Verify**: Assistant should be able to describe what was happening in the
previous session without re-reading all the original files.

### /update Functional Test

**Setup**: Environment has been used for at least a few interactions.
Have at least one entry in Docs/_working/retro/ (can be manually created for testing).
**Action**: Run /update.
**Expected**:
- Reads retro log and identifies patterns
- Presents analysis with evidence
- Proposes specific changes (if patterns found)
- Does NOT implement changes without approval
- Writes proposals to Docs/_working/retro/Proposals/

**Verify**: Proposals are specific and reference actual friction entries.
No files are modified outside Docs/_working/retro/Proposals/ during analysis phase.

### /health-check Functional Test

**Setup**: A complete generated environment.
**Action**: Run /health-check.
**Expected**:
- Runs deterministic checks (file existence, JSON validity, naming)
- Runs semantic checks (staleness, contradictions, routing)
- Produces a brief report with PASS/WARN/FAIL per check
- Report is accurate (no false failures on a freshly generated environment)

**Verify**: A freshly generated environment that passed the validator should
also pass health-check with zero FAILs and minimal WARNs.

### /build Functional Test (if generated)

**Setup**: A project with a build system configured.
**Action**: Run /build.
**Expected**:
- Executes the correct build command for the project
- Reports build result (success/failure)
- On failure, shows relevant error output

**Verify**: Build result matches running the same command manually.

### /review Functional Test (if generated)

**Setup**: Have some recent code changes (at least one modified file).
**Action**: Run /review.
**Expected**:
- Identifies changed files
- Reviews each file against project conventions
- Produces structured feedback (issues categorized by severity)
- Does not modify any files

**Verify**: Review findings are relevant to actual changes, not generic.

---

## Smoke Test Template

Present this to the user after environment generation as their verification
checklist.

```markdown
## Smoke Test Your New Environment

Run these tests to verify your environment works correctly.
Each test takes about 1 minute.

### Test 1: First Run Greeting
1. Open a new terminal in your project directory
2. Run `codex` (or your Codex invocation)
3. Send any greeting message ("hello", "hi", "what can you do?")

Expected: The assistant greets you, describes what it can do, and
suggests trying a specific command. It should detect this is a new
environment.

### Test 2: State Save and Load
1. Ask the assistant to do something simple (read a file, answer a question)
2. Run /state-save
3. Verify Docs/_working/state/ contains SESSION_SNAPSHOT.json and SESSION_CONTEXT.md
4. Run /clear (or start a new session)
5. Run /state-load
6. The assistant should know what you were doing before

Expected: State is captured and restored accurately. No permission errors.

### Test 3: Health Check
1. Run /health-check

Expected: All checks pass (PASS or WARN acceptable for a new environment).
No FAIL results.

### Test 4: Domain Task
1. Ask the assistant to help with a real task from your project
2. Observe: Does it use the right approach? Does it delegate to the
   right agent? Does it use the correct tools?

Expected: The assistant routes your request appropriately and produces
useful output without excessive permission prompts.

### Test 5: Try to Break It
1. Ask for something outside the assistant's scope
2. Ask for something ambiguous

Expected: The assistant either asks a clarifying question (for ambiguous)
or explains its limitations (for out-of-scope). It should not crash,
hallucinate capabilities, or modify files it should not touch.

### Troubleshooting
If any test fails:
- Run /health-check to identify structural issues
- Check Docs/Environment/VALIDATION_REPORT.md for known issues
- Check .codex/config.toml for missing permissions
- Report the issue to help improve the Harness Generator
```

---

## Edge Case Validation Checklist

Additional checks for situations that commonly cause problems:

### Path Handling
- [ ] All file paths in generated content use forward slashes (cross-platform)
- [ ] No absolute paths in generated content (all relative to project root)
- [ ] No path references contain spaces without proper handling guidance

### Encoding
- [ ] All generated files are ASCII-only (no unicode characters, no emoji)
- [ ] No BOM (byte order mark) in generated files

### Empty State
- [ ] Environment works on first run (no pre-existing state required)
- [ ] /state-load handles missing state files gracefully (first run)
- [ ] /health-check handles missing _working/retro/ entries gracefully
- [ ] Wiki index.md (Docs/index.md) has NEW_ENVIRONMENT status marker

### Permission Boundaries
- [ ] .codex/config.toml allow rules cover all operations agents need to perform
- [ ] .codex/config.toml deny rules do not block normal operation
- [ ] Agents with sandbox_mode do not reference those tools in their instructions

### Scale Appropriateness
- [ ] Memory tier matches project scale from GENESIS.md
- [ ] Number of agents is justified (not over-engineered for simple projects)
- [ ] Number of rules is justified (5-8 range)
- [ ] Complexity of routing table matches project complexity

### Content Freshness
- [ ] VERSION.md contains generation date and Harness Generator version
- [ ] All "Last Updated" fields have the generation date
- [ ] No placeholder dates (YYYY-MM-DD in final output)
