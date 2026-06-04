---
name: update
description: Updates the Harness Generator's own knowledge base (Docs/AgentGuidelines/Topics/, AgentPlaybooks/, tool-registry) -- ingests pending ProvideKnowledge/ docs, then web-researches OpenAI docs and changelogs, incorporates validated findings with source attribution, and prunes superseded or deprecated entries (90-day tool-registry cadence). Supports a local-only mode that ingests ProvideKnowledge/ without web search. Use when the user says "update knowledge", "refresh best practices", "check for updates", "update the Harness Generator", "process knowledge", "I added some docs to ProvideKnowledge", "incorporate this research", "process my notes", or "/update". Do NOT use to upgrade a user's generated environment (use /upgrade-environment) or to validate one (use /validate-environment).
---

## Critical

This updates the CREATOR'S OWN knowledge base (Docs/AgentGuidelines/ and Docs/AgentPlaybooks/), not a user's generated environment. Never modify files outside the Harness Generator project.

## What this skill does

1. Ingest any pending user-contributed knowledge from ProvideKnowledge/ (scan, classify, validate, incorporate, move to Processed/)
2. Check topic files in Docs/AgentGuidelines/Topics/ for staleness
3. Research latest Codex documentation from the web
4. Incorporate validated findings into the appropriate topic files
5. Review existing content for entries superseded by new findings
6. Prune deprecated or contradicted content
7. Report what changed (added, updated, removed)

This is the full update pipeline. **Local-only mode** -- triggered by phrasings
like "process knowledge", "I added some docs", "incorporate this research", or
"/update --local" -- ingests `Docs/ProvideKnowledge/` without web research: run
Steps 1, 4, 6, 7 only and skip the web-research steps (2, 3, 3b) and web-driven
pruning (5b).

## Steps

### Step 1: Process ProvideKnowledge items

Scan `Docs/ProvideKnowledge/` for unprocessed files (ignore `Processed/` subdirectory and `README.md`).

For each unprocessed item:
1. Read the full content
2. Classify by topic: rules, agents, skills, teams, memory, context, routing, permissions, hooks, MCP, prompt engineering, or other
3. Assess source reliability:
   - Tier 1: OpenAI official documentation
   - Tier 2: Validated community practices (multiple sources, evidence-backed)
   - Tier 3: Anecdotal or single-source
4. Cross-reference against existing topic files in `Docs/AgentGuidelines/Topics/` (use INDEX.md for routing)
5. If validated and new: add to the appropriate topic file with source attribution and tier
6. If contradicts existing content: flag for review, include both entries with dates
7. Move processed file to `Docs/ProvideKnowledge/Processed/` with date prefix (e.g., `2026-02-14_original-filename.md`)

### Step 2: Check topic files for staleness

Read `Docs/AgentGuidelines/INDEX.md` to get the topic file list and their last-updated dates.

If any topic file has not been updated in 30+ days (or has no date), proceed to Step 3. Otherwise, skip to Step 5 unless ProvideKnowledge items were found.

### Step 3: Research latest documentation

Search for recent Codex updates from these sources:
- OpenAI documentation site (developers.openai.com)
- Codex changelog and release notes
- New skill, agent, or hook patterns
- Changes to AGENTS.md format, .codex/config.toml schema, or permission syntax

Focus on:
- New features that affect environment design (new tool types, new frontmatter fields, new hook events)
- Breaking changes (deprecated features, changed behavior)
- New best practices from OpenAI (prompt engineering, agent patterns)

### Step 3b: Verify tool registry

Read `Docs/Templates/References/tool-registry.md`. For each tool where Last
Verified is 90+ days old:

1. Web search: "[tool name] latest version [current year]"
2. Web search: "[tool name] deprecated OR discontinued OR alternative"
3. Check if install command still works (verify package exists)
4. If the tool is still active: update Last Verified date in registry
5. If deprecated or superseded: change status to Deprecated, add Supersedes
   note, and queue the replacement as a new finding for Step 4
6. If a better alternative was discovered: add it as a new registry entry
   with status Experimental, queue for Step 4 incorporation

Also check for new tools in categories where the registry has few options:
- Search: "Codex [category] plugin [current year]"
- Only add tools meeting the evaluation criteria in section 5.10 of
  Topics/05-memory.md (local-first, free, open-source, compatible)

Update the registry's Last Updated date after all changes.

### Step 4: Incorporate findings

For each finding from Steps 1 and 3:

1. Use INDEX.md to determine the relevant topic file in Docs/AgentGuidelines/Topics/
2. Check if the information is already present in that topic file
3. If new and validated:
   - Add to the appropriate topic file
   - Include: source URL or document name, tier classification, date found
   - Format consistently with existing entries
4. If contradicts existing content:
   - Do NOT silently replace
   - Add a "Conflict" note with both the old and new information
   - Include dates for both entries
   - Flag for human review in the report

Update the "Last Updated" date in each modified topic file and in INDEX.md.

### Step 5: Review and prune existing content

After incorporating new findings, review the affected topic files for content that
should be updated or removed. This step prevents the knowledge base from
accumulating stale advice that competes with current guidance.

**5a. Superseded entries**: For each new finding added in Step 4, check if it
replaces or updates an existing entry in the same section. If the new entry
covers the same topic with newer information:
- Remove the old entry entirely (do not keep both)
- Note the removal in the report: "Removed: [old entry summary] -- superseded by [new entry summary]"
- If uncertain whether the old entry is fully superseded, keep both and add
  a CONFLICT marker for human review

**5b. Deprecated features**: Search for references to features, APIs, or
patterns that the web research (Step 3) identified as deprecated or removed.
Common signals:
- Codex changelog entries with "removed" or "deprecated"
- Documentation pages that no longer exist (404) or redirect
- Model versions that are no longer available
- Syntax or settings that have been replaced

For each deprecated reference:
- If a replacement exists: update the entry in place
- If no replacement: remove the entry and note in the report
- If uncertain: add a REVIEW marker with the deprecation signal found

**5c. CONFLICT and UNVERIFIED markers**: Check for existing CONFLICT or
UNVERIFIED markers that can now be resolved:
- If new findings clarify the conflict, resolve it (keep the validated side)
- If an UNVERIFIED entry from a previous run is now confirmed by Tier 1
  sources, remove the UNVERIFIED marker
- If an UNVERIFIED entry is contradicted by new Tier 1 findings, remove it

**5d. Propagate changes**: When entries are removed or updated in topic files,
check if downstream files reference them:
- `Docs/AgentPlaybooks/*.md` -- update or remove references
- `.codex/rules/02-generation-standards.md` -- verify standards still match
- `.codex/rules/03-quality-gates.md` -- verify checks still match
- `Docs/StarterProfiles/*.md` -- update profile recommendations if affected
- `Docs/Templates/References/tool-registry.md` -- sync tool status changes
- `.codex/agents/environment-architect.toml` -- update matching rules if tools changed

Only modify downstream files when the change is clear-cut (removed feature,
renamed concept). Flag ambiguous downstream impacts for human review.

Use the Cross-Reference Map in tool-registry.md to identify all files that
need updating when a tool's status changes.

### Step 6: Update indexes

If subsections were added or removed in topic files, or if new topic files were created:
- Update `Docs/AgentGuidelines/INDEX.md` to reflect changes

If playbook content was affected:
- Update `Docs/AgentPlaybooks/INDEX.md`

### Step 7: Report

Output a summary:
- **ProvideKnowledge items processed**: count and topics
- **Sources checked**: list of documentation sources searched
- **New entries added**: count and topics
- **Entries updated**: count and what changed (superseded, corrected)
- **Entries removed**: count and reason for each (deprecated, superseded, resolved conflict)
- **Conflicts flagged**: count and brief description of each (new + unresolved existing)
- **Downstream files updated**: list of files modified outside the topic files
- **Items needing human review**: CONFLICT/REVIEW markers still unresolved
- **Tool registry**: tools verified, status changes, new tools added
- **No changes needed**: if everything is already up to date, say so
