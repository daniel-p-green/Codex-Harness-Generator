# Git Integration Rule (Template)

<!-- ANNOTATION: This rule defines safe vs dangerous Git operations and
     establishes commit/PR workflows. Only generate this when the user's
     project uses Git (identified during intake). -->

<!-- QUALITY: Must categorize every common git command as safe or dangerous.
     Must include commit message guidance. Must include PR workflow if
     the user collaborates with others. Must not exceed 120 lines. -->

## Example: Git VCS Rule (`.claude/rules/vcs-git.md`)

```markdown
# Git integration

<!-- ANNOTATION: Lead with the safety classification. This is the most
     important section because it prevents destructive operations. -->

## Safe commands (run without asking)

<!-- VARIATION: All projects get the same safe list. This rarely changes. -->

These commands are read-only or locally reversible. Run them immediately:
- `git status`, `git diff`, `git log`, `git show`
- `git add <files>`, `git commit`
- `git branch`, `git checkout`, `git switch`
- `git stash`, `git stash pop`, `git stash list`
- `git pull`, `git fetch`
- `git merge` (local branches only)
- `git cherry-pick`
- `git rebase` (local, non-interactive)

<!-- ANTI-PATTERN: Do not list every possible git command. Focus on the
     commands Claude actually uses. Listing obscure commands wastes tokens. -->

## Dangerous commands (ask first)

<!-- ANNOTATION: These are hard-to-reverse or visible to others.
     Include the WHY so Claude understands the risk, not just the rule. -->

Never run without explicit user request:
- `git push --force` / `git push --force-with-lease` -- rewrites remote history
- `git reset --hard` -- destroys uncommitted work
- `git clean -f` / `git clean -fd` -- permanently deletes untracked files
- `git branch -D` -- deletes branch without merge check
- `git checkout .` / `git restore .` -- discards all local changes

Ask before running:
- `git push` -- makes changes visible to others
- `git rebase` on shared branches -- rewrites shared history
- `git merge` from remote branches -- may introduce conflicts

<!-- VARIATION: For solo projects, `git push` can be moved to safe commands.
     For teams with CI/CD, keep it in the "ask" category. -->

## Commit workflow

<!-- ANNOTATION: This section teaches Claude how to make good commits.
     Adapt the message format to the team's conventions (identified in intake). -->

When asked to commit:
1. Run `git status` to see all changes
2. Run `git diff --staged` to review what will be committed
3. Stage specific files (prefer `git add <file>` over `git add -A`)
4. Never commit `.env`, credentials, or secrets
5. Write a concise commit message:
   - First line: imperative mood, under 72 chars, describes the WHY
   - Blank line, then details if needed
6. Run `git status` after commit to verify

<!-- EXAMPLE: Alternative commit message format for Conventional Commits:
     "feat: add user authentication endpoint"
     "fix: prevent null pointer in payment processing"
     "refactor: extract validation logic into shared module" -->

<!-- ANTI-PATTERN: Do not include "Co-Authored-By" lines in the template.
     That is specific to the Harness Generator's own workflow, not generated environments. -->

## PR workflow

<!-- VARIATION: Only include this section if the user works with a team
     or uses GitHub/GitLab. Skip for solo projects. -->

When asked to create a pull request:
1. Check current branch is not main/master
2. Push branch to remote (`git push -u origin <branch>`)
3. Use `gh pr create` (GitHub) or equivalent
4. Include:
   - Short title (under 70 chars)
   - Summary of changes
   - Test plan
5. Do not force-push to main/master

## Branch conventions

<!-- VARIATION: Adapt to the team's branching model. Common patterns:
     - feature/<name>, bugfix/<name>, hotfix/<name>
     - <initials>/<ticket>-<description>
     - No convention (solo projects) -->

Follow the project's branching conventions. If none are established:
- `feature/<description>` for new features
- `fix/<description>` for bug fixes
- Keep branch names lowercase with hyphens
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] All common git commands categorized (safe/ask/never)
     - [ ] WHY included for dangerous commands
     - [ ] Commit workflow includes staging and verification steps
     - [ ] No secrets committed (explicit rule)
     - [ ] PR workflow present if user has team/collaboration
     - [ ] Under 120 lines
     - [ ] No role-setting ("Act as a git expert")
-->
