# Profile Format (slim)

Both base starter profiles (`Docs/StarterProfiles/`) and bundled domains
(`Docs/DomainLibrary/`) follow this format. Target **~150-220 lines**. A profile
is a *starting point the architect adapts* -- it points at templates rather than
inlining their content.

## Why slim

Profiles must NOT inline agent definitions, rule bodies, skill specs, or full
permission JSON -- those already live as generator-read templates
(`Docs/Templates/Agents|Core|Optional|Skills/`) and the shared
`Docs/Templates/References/ecosystem-permissions.md`. Inlining them is dead
duplication the generator never reads. Keep only what is *domain-specific* and
not derivable from a template: the routing table, friction seeds, customization
points, and component *selection* (which templates, which model).

## Required sections

1. **Profile Metadata** -- name, target audience, primary tools/languages,
   complexity level (Lite/Standard/Extended), memory tier, action default
   (proactive/conservative), VCS.
2. **Component Roster** -- three compact tables listing names + one-line role +
   (agents) model + template pointer. Do NOT paste YAML or instructions.
   - Agents: `| name | model | role | template |`
   - Rules: `| name | purpose | template |`
   - Skills: `| name | purpose | template |` (always include the core skills:
     state-save, state-load, update, health-check)
3. **Domain Routing Table** -- the real value. 10-16 rows: `| # | user intent |
   route | context/notes | fallback |`, using this domain's vocabulary. Plus a
   complexity-scaling note (simple/standard/complex).
4. **Ecosystem Permissions** -- name the Base + Universal Deny sets and the
   specific ecosystems needed (e.g., "Python + Git -- see ecosystem-permissions.md").
   Inline ONLY domain-specific permissions not in that reference.
5. **Self-Learning Seed Entries** -- 4-6 pre-seeded `[PATTERN]` friction entries
   specific to this domain (bootstrapping threshold 1 during the first 30 days).
6. **Hook Suggestions** -- names + one-line purpose + template pointer
   (`Docs/Templates/Optional/hooks-template.md`). No full JSON unless the hook is
   domain-unique.
7. **Cost / Model Notes** -- recommended model tiering and token-priority
   defaults (cost-conscious / balanced / quality-first) for this domain.
8. **Customization Points** -- the 3-6 things the architect most often varies for
   this domain, as a checklist for intake follow-ups.

## Optional sections (only if domain-relevant)

Team template (when work splits into non-overlapping areas), MCP suggestions
(name the service + verified server from tool-registry), special patterns (A-I)
the domain triggers. Keep each to a few lines + a pointer.

## Team-architecture pattern

State which of the six patterns (topic 04) the roster naturally follows
(Pipeline / Fan-out-Fan-in / Expert Pool / Producer-Reviewer / Supervisor /
Hierarchical Delegation) and whether any phase justifies Agent Teams over the
subagent default. One or two sentences.
