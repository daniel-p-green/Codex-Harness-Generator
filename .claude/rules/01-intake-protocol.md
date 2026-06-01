# Intake protocol

The intake determines what environment to generate. Two paths: profile-first
(common, fast) and deep interview (fallback, thorough). This rule is the
contract; the detailed question checklists, the "not sure" work-area branch, the
preset-vs-custom flow, the 5-stage funnel + relay protocol, the GENESIS.md
format, and edge cases live in `Docs/AgentPlaybooks/IntakeChecklist.md`. Load
that playbook when running an interview.

## Vocabulary (user-facing)

Say **"work area"** not "project" when asking about scope -- "project" is
ambiguous (subject vs. unit-of-work). Say **"shared basics"** not "parent
CLAUDE.md" or "inherited rules." "Hub" is an internal term -- never surface it
to users.

## AskUserQuestion conventions

The AskUserQuestion tool always provides a built-in freeform "Other" option.
Never include a redundant "something else", "none of these", or "other" choice
in the options list -- users can always type freeform details via the built-in
Other field.

## Profile-first path (orchestrator handles directly)

Primary path. Most users match a starter profile or a bundled domain with
modifications.

0. **Experience level** (preamble): beginner / intermediate / advanced. Calibrates
   agent count, doc complexity, and GETTING_STARTED.md depth.
0b. **Work-area shape**: one focused area / separate work areas / not sure (say
   "work area", never "hub"). Always reassure it is reversible (~1 minute). For
   "not sure", run the two-question branch in IntakeChecklist.md Step 0b. Multiple
   areas -> collect one-line descriptions, then loop steps 1-6 per area (shared
   basics collected once -> HUB_GENESIS.md).
0c. **Preset vs custom**: start from a tested preset (a base profile or bundled
   domain -- fast, fewer tokens; best for one-off / short-term harnesses) or
   custom generation (a tailored, reusable DOMAIN_PROFILE.md the architect
   synthesizes -- more tokens + time; best for long-term harnesses or novel
   domains). Record `GENERATION_MODE` in GENESIS.md. See IntakeChecklist.md Step 0c.
1. **Present options**: the 4 base profiles plus any relevant bundled domain from
   `Docs/DomainLibrary/`, one sentence each. (AskUserQuestion adds "Other"
   automatically -- do not add "none of these".) For hubs, present per area;
   different areas may pick different profiles/domains.
2. **User selects** -> load the chosen profile/domain from disk and present a
   plain-language summary of what the environment will include.
3. **Customize** (2-3 rounds): work through the probe checklist in
   IntakeChecklist.md Step 3 (Gather modifications) -- languages/tools, gates,
   team/roles, always/never, data + sensitivity, repeatable processes,
   output/brand, codebase scale, reference docs, multi-session, multi-modal, local
   model, AI budget, cost priority, setup tolerance.
4. **External services + integrations**: see IntakeChecklist.md Step 4 (External
   services and MCP integrations).
5. **Confirm**: present the intake summary; one confirmation round ("Does this
   look right? Anything to add or change?").
6. **Write GENESIS.md** (`INTAKE_STATUS: COMPLETE`; format in IntakeChecklist.md).
   Hubs: write HUB_GENESIS.md with shared basics (experience level, vocabulary,
   autonomy, team shape, shared tools, AI ecosystem extensions, work-area registry
   with one-line descriptions) plus one `<area-slug>/Docs/Environment/GENESIS.md`
   per area; set `HUB_STATUS: COMPLETE`.

## Deep interview path (delegate to intake-interviewer)

Triggered when the user says "none of these" or the project clearly fits no
profile. The intake-interviewer runs a 5-stage funnel (overview / technical /
workflow / roles / preferences; non-technical users skip the technical stage) and
communicates through the question relay protocol. Full funnel + relay steps:
IntakeChecklist.md.

## When to proceed to architecture

The intake is sufficient when you can design a routing table (you know what kinds
of requests the user will make), identify which agents are needed (and which are
not), and list the constraints and preferences. If any of these are unclear after
customization, ask one more targeted question -- do not over-interview.

## Target directory

Ask for the target directory early (the /create skill handles this). Verify it
exists and is writable before starting the interview, to avoid wasted effort on
an invalid path.
