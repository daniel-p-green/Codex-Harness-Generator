# Build System Integration Rule (Template)

<!-- ANNOTATION: Generate this rule when the project has a build step
     (compiled languages, bundlers, CI pipelines). Skip for interpreted
     languages with no build step (plain Python scripts, shell scripts). -->

<!-- QUALITY: Must include the actual build command. Must define error
     parsing behavior. Must include retry policy. Under 120 lines. -->

## Example: Build System Rule (`.codex/rules/build-system.md`)

```markdown
# Build system

<!-- ANNOTATION: State the build command explicitly. Codex cannot guess
     project-specific build commands reliably. This is one of the most
     valuable things to put in rules (per OpenAI best practices). -->

## Build command

<!-- VARIATION: Adapt to the project's actual build system.
     - C++/UE: UnrealBuildTool or Editor build
     - Rust: cargo build
     - Go: go build ./...
     - TypeScript: npm run build / tsc
     - Java: mvn compile / gradle build
     - C#: dotnet build
     - Frontend: npm run build / vite build -->

Primary build command:
```bash
npm run build
```

Test command (run after successful build):
```bash
npm run test
```

<!-- EXAMPLE: For a C++ project:
     Primary: cmake --build build/ --config Release
     Test: ctest --test-dir build/ --output-on-failure -->

<!-- EXAMPLE: For a Rust project:
     Primary: cargo build
     Test: cargo test -->

## When to build

- After implementing a checkpoint or completing a code change
- Before declaring a task complete
- When the user asks to verify changes compile

Do NOT build:
- After every small edit (batch changes, then build once)
- When only documentation or config files changed

## Error handling

<!-- ANNOTATION: This section teaches Codex how to interpret build
     output. Without this, Codex may ignore warnings or retry
     endlessly on infrastructure errors. -->

When a build fails:
1. Read the FULL error output (do not truncate)
2. Identify the root cause (first error, not cascading errors)
3. Categorize the error:
   - **Syntax/type error**: Fix the code and rebuild
   - **Missing dependency**: Install it, then rebuild
   - **Configuration error**: Fix config, then rebuild
   - **Infrastructure error** (disk full, network, permissions): Report to user
4. Fix and rebuild (max 3 retries on the same error)
5. If the same error persists after 3 attempts, report to the user

<!-- ANTI-PATTERN: Do not retry indefinitely. Three retries is the limit.
     After that, the fix approach is wrong and needs human input. -->

## Pre-build checks

<!-- VARIATION: Adapt to the project's toolchain.
     - TypeScript: type checking (tsc --noEmit)
     - Python: mypy, ruff
     - Rust: cargo check (faster than full build)
     - Go: go vet -->

Before a full build, consider running faster checks:
- Lint: `npm run lint` (catches style issues without full compilation)
- Type check: `npx tsc --noEmit` (catches type errors quickly)

These are faster than a full build and catch common issues early.

## Build artifacts

<!-- ANNOTATION: Tell Codex where build output goes so it does not
     accidentally read or modify build artifacts. -->

Build output goes to: `dist/` (do not edit files in this directory)
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] Actual build command specified (not placeholder)
     - [ ] Error categorization includes at least 3 categories
     - [ ] Retry policy has a cap (max 3 recommended)
     - [ ] Pre-build checks listed if the ecosystem supports them
     - [ ] Build artifact directory identified
     - [ ] Under 120 lines
-->

<!-- ANTI-PATTERN: Do not include CI/CD pipeline configuration. That
     belongs in the project's CI config files, not in Codex's rules.
     Do not list every possible build flag -- only the ones the team
     actually uses. -->
