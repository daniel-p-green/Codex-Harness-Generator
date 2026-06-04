# Testing Gates Rule (Template)

<!-- ANNOTATION: Generate this rule when the project requires testing
     verification before changes are considered complete. This covers
     both automated tests (unit, integration) and manual testing
     (playtesting, visual review). The manual testing gate is especially
     important for game dev and UI-heavy projects. -->

<!-- QUALITY: Must define PASS/FAIL criteria. Must include test commands
     if automated tests exist. Must include manual test protocol if
     applicable. Under 120 lines. -->

## Example: Testing Gates Rule (`.codex/rules/testing-gates.md`)

```markdown
# Testing gates

Changes are not complete until they pass testing. This rule defines
what "passing" means and how to run tests.

<!-- ANNOTATION: State the principle upfront. This frames all the
     specific rules that follow. -->

## Automated tests

<!-- VARIATION: Include this section only when the project has automated
     tests. Skip entirely for projects without a test suite. -->

<!-- VARIATION: Adapt the command to the project's test runner:
     - Python: pytest / python -m pytest
     - JavaScript: npm test / jest / vitest
     - Rust: cargo test
     - Go: go test ./...
     - C#: dotnet test
     - Java: mvn test / gradle test -->

Run tests after implementing changes:
```bash
npm test
```

### Interpreting results
- **All pass**: Proceed to next step
- **Failures in changed code**: Fix before proceeding
- **Failures in unrelated code**: Note the pre-existing failures, proceed
  with your changes if they did not introduce the failures
- **Flaky tests** (pass/fail inconsistently): Run twice. If it passes on
  rerun, note it as flaky and proceed

### Test-first workflow
When fixing a bug:
1. Write or identify a test that reproduces the bug
2. Verify the test fails
3. Implement the fix
4. Verify the test passes
5. Run the full test suite

<!-- ANTI-PATTERN: Do not require running the entire test suite after every
     small edit. Run relevant tests during development, full suite before
     declaring a task complete. -->

## Manual testing gate

<!-- ANNOTATION: This is the critical gate for projects where automated
     tests cannot verify the change (UI, gameplay, visual output). The
     STOP-and-wait pattern is essential -- Codex must not continue past
     this point without user confirmation. -->

<!-- VARIATION: Include this section for game dev, UI-heavy projects,
     and any project where visual/interactive verification is required.
     Skip for backend-only or library projects with good test coverage. -->

After a successful build, output a test request:
1. What changed (3-5 bullets)
2. Files modified (paths)
3. Test steps (numbered, explicit, 3-10 steps)
4. Expected results for each step

Then STOP. Do not make further changes until the user reports results.

### Playtest result format

The user will respond with:
```
PLAYTEST RESULTS: <checkpoint>
- Result: PASS / FAIL / PARTIAL
- Notes: <observations>
- Repro steps (if FAIL): <numbered steps>
- Logs/screenshots: <paths or text>
```

### After receiving results
- **PASS**: Record the result, proceed to next step
- **PARTIAL**: Record what passed and failed, fix failures
- **FAIL**: Record the failure, diagnose the root cause, propose a fix

<!-- EXAMPLE: For a game dev project, the manual testing section would
     reference PIE (Play In Editor) testing, specific game mechanics to
     verify, and expected visual/audio feedback. -->

<!-- EXAMPLE: For a web frontend project, the manual testing section would
     reference browser testing, responsive layout checks, and specific
     user interactions to verify. -->

## Test documentation

Record test results in the task file:
- Which tests were run (automated and/or manual)
- PASS/FAIL/PARTIAL status
- Any issues found and whether they were fixed
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] Automated test command specified (if project has tests)
     - [ ] PASS/FAIL/PARTIAL criteria defined
     - [ ] Manual testing gate includes STOP instruction (if applicable)
     - [ ] Test result format documented
     - [ ] Recording results in task file mentioned
     - [ ] Under 120 lines
-->

<!-- ANTI-PATTERN: Do not combine build and test into a single rule file.
     They serve different purposes and not all projects need both. Keep
     them as separate optional rules that can be independently included. -->
