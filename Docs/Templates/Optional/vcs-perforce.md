# Perforce Integration Rule (Template)

<!-- ANNOTATION: This rule defines Perforce safety boundaries. Generate when
     the user's project uses Perforce/Helix Core (common in game dev, large
     binary-heavy projects). Perforce has a fundamentally different model from
     Git: explicit checkout, server-authoritative, numbered changelists. -->

<!-- QUALITY: Must include the "never submit" rule. Must handle binary assets.
     Must categorize commands. Must not exceed 120 lines. -->

## Example: Perforce VCS Rule (`.codex/rules/vcs-perforce.md`)

```markdown
# Perforce integration

This project uses Perforce (Helix Core), not Git.

<!-- ANNOTATION: State the VCS upfront because Codex defaults to Git
     assumptions. This single line prevents many misrouted operations. -->

## Safe commands (run without asking)

<!-- ANNOTATION: These are all read-only or locally reversible operations.
     The key insight: in Perforce, "p4 edit" just opens a file for editing
     (marks it in the server), it does not commit anything. -->

All safe -- run immediately and report the result:
- `p4 opened` -- list files currently checked out
- `p4 edit <file>` -- open file for editing
- `p4 add <file>` -- mark new file for addition
- `p4 diff`, `p4 diff -du <file>` -- view local changes
- `p4 describe -s <CL>` -- describe a changelist
- `p4 changes -s submitted` -- list submitted changelists
- `p4 fstat <file>` -- file status and metadata
- `p4 sync` -- get latest from server
- `p4 reconcile` -- detect offline changes and open them
- `p4 change -o`, `p4 change -i` -- create/update changelist specs
- `p4 reopen -c <CL> <file>` -- move file between changelists
- `p4 revert <file>` -- revert a single file (locally reversible)

## Never run autonomously

<!-- ANNOTATION: p4 submit is the equivalent of git push -- it is
     permanent and visible to the entire team. This is the single
     most important safety rule for Perforce projects. -->

- **`p4 submit`** -- NEVER run this. Human-only operation.
  - Why: submit is permanent and immediately visible to all team members.
  - Always: prepare the changelist, then tell the user it is ready to submit.

Ask before running:
- `p4 revert` on large file sets (>10 files) or entire changelists
- `p4 obliterate` -- permanently destroys history (admin operation)

## Changelist hygiene

<!-- VARIATION: Some teams use one CL per feature, others use one CL per
     checkpoint. Adapt based on team conventions from intake. -->

- Keep changelists small: one feature, bugfix, or refactor per CL
- Keep unrelated files out of a CL
- Update the CL description to reflect the final state of changes
- Use `p4 reopen -c <CL> <file>` to move files between changelists

## Binary asset handling

<!-- ANNOTATION: This is critical for game dev and media projects.
     Binary files (.uasset, .umap, .psd, .fbx, etc.) cannot be
     meaningfully diffed or merged. Codex must never edit them. -->

Do NOT edit binary assets (`.uasset`, `.umap`, `.psd`, `.fbx`, `.blend`).
If a binary/editor-only change is required:
1. Write the exact editor steps the user should follow
2. STOP and wait for the user to make the change manually

<!-- VARIATION: For non-game projects, replace the binary extensions with
     whatever binary formats the project uses (.pdf, .xlsx, .docx, etc.) -->

## File handling

- If a file is read-only, it has not been opened for edit yet
- Run `p4 edit <file>` before modifying any tracked file
- Use `p4 reconcile` to detect files changed outside of Perforce
- Use `p4 add <file>` for new files not yet in the depot
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] "p4 submit" explicitly forbidden as autonomous action
     - [ ] WHY included for the submit prohibition
     - [ ] Binary asset types listed (adapted to project domain)
     - [ ] Binary edit protocol: write steps, then STOP
     - [ ] Common commands categorized
     - [ ] Changelist hygiene guidance included
     - [ ] Under 120 lines
-->

<!-- ANTI-PATTERN: Do not include Perforce workspace/client configuration
     details. Those belong in AGENTS.override.md (machine-specific, not
     shared). Do not include depot paths -- those are project-specific
     and should come from GENESIS.md. -->
