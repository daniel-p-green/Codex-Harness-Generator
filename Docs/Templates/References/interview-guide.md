# Interview Guide

Reference document for the intake-interviewer agent. Contains the 5-stage
interview funnel, GENESIS.md format template, and question design principles.

Loaded by the intake-interviewer agent in Step 1 of its procedure.

---

## 5-Stage Interview Funnel

### Stage 1: Project Overview

Goal: Understand domain, work type, scale, and team.

Questions:
- "What kind of project is this? What does it do or produce?"
- "Is this mostly code, documents, research, data, or a mix?"
- "How many people work on it? Just you, a small team, or a large organization?"
- "What is the main thing you want an AI assistant to help with?"
- "How familiar are you with AI assistants and command-line tools?
  (Just getting started / Somewhat familiar / Very comfortable)"
  This determines: agent count (fewer for novices), language complexity in
  generated docs, GETTING_STARTED.md depth, whether to include terminal basics.

This stage always runs. After processing answers, you must be able to state in
one sentence what the project is and what the user wants help with. If you
cannot, add one clarifying question before moving on.

Write findings to `## Project Overview` section of GENESIS.md.

### Stage 2: Technical Environment

Goal: Languages, VCS, build system, external services, plugin/tool integration.

Questions:
- "What programming languages or tools does the project use?"
- "Do you use version control? If so, which one (Git, Perforce, SVN, etc.)?"
- "Do you have a build system, test suite, or CI/CD pipeline?"
- "What external services does your project connect to (databases, APIs, cloud
  platforms, project management tools)?"
- "Do you use any additional Codex plugins or tool integrations that
  extend what the assistant can do? (These are sometimes called MCP servers --
  if you are not sure, the answer is probably no.)"
- "Do you work with data files like spreadsheets, CSV files, or databases? If
  so, what do you typically need to do with them -- read them, analyze them,
  transform them, or produce reports from them?"
  This determines: Python/data tool permissions, data-analyst agent, data
  processing routing entries.
- "Does your project include files like images, videos, audio, design files,
  or other files that cannot be edited as text?"
  This determines: VCS ignore rules patterns, binary protection hooks, "describe
  editor steps" routing entries.

SKIP CONDITION: If Stage 1 reveals a purely non-technical project (pure writing,
legal analysis with no code), skip this stage entirely. Record "Technical
environment: N/A -- non-technical project" in GENESIS.md.

Write findings to `## Technical Environment` section.

### Stage 3: Workflow

Goal: Work patterns, quality gates, pain points.

Questions:
- "Walk me through a typical task from start to finish. What steps do you
  usually take?"
- "Are there any approval steps or quality checks in your process?"
- "What are the most frustrating or time-consuming parts of your workflow?"
- "Do you repeat the same process for different clients, students, cases, or
  projects? If so, describe one such repeatable workflow from start to finish."
  This determines: template-management skills, per-entity folder structures,
  /new-engagement style skills.
- "What kinds of documents or files does your work produce -- for example,
  plain text, Word documents, presentations, PDFs, spreadsheets? For any
  formatted documents, do they go to external audiences where professional
  formatting matters?"
  This determines: document conversion/formatting tool selection (Pandoc for
  high-quality formatted output vs simpler pip-only tools for basic documents).
- "Does your organization have brand guidelines, a style guide, or design
  standards that your work output should follow? Do you have existing document
  or presentation templates that produced files should match?"
  This determines: Brand/ directory scaffolding, brand-rules.md auto-generation,
  template-aware output routing (Pandoc reference-doc integration).

This stage always runs. Adapt question phrasing based on whether the project is
technical or non-technical. At least one workflow pattern and one pain point must
be identified.

Write findings to `## Workflow` section.

### Stage 4: Roles and Specializations

Goal: What specialized assistants would be useful, what needs human approval.

Questions:
- "If you could have specialized AI assistants, what would each one do?"
- "Are there any actions the assistant should NEVER do without asking you first?"
- "Are there any actions the assistant should ALWAYS do automatically?"
- "How much do you want the assistant to explain its reasoning versus just
  doing the work?"
- "Does your work involve sensitive or regulated data -- such as client
  information, student records, patient data, or financial records? Are there
  any types of information the assistant should never store or display?"
  This determines: data classification rules, restricted memory paths, PII
  handling rules, deny patterns.
  Follow-up if yes: "Should sensitive data be blocked automatically
  (deterministic scanning) or handled by advisory guidelines only?"
  This determines: compliance enforcement hooks vs advisory-only.

For very simple projects (solo, single-purpose), condense to: "What should
the assistant always ask about before acting?"

Hard constraints (never-do-without-asking) must be explicitly recorded. If the
user cannot think of any, record: "No hard constraints specified -- default to
domain-appropriate safety level."

Write findings to `## Roles and Constraints` section.

### Stage 5: Preferences

Goal: Communication style, autonomy level, documentation needs, setup tolerance.

Questions:
- "How do you prefer the assistant to communicate -- brief and direct, or
  detailed and explanatory?"
- "Should the assistant write documentation as it works, or only when asked?"
- "Do you prefer a simpler setup you can start using right away, or are you
  comfortable spending time installing and configuring extra tools for more
  capability?"
  Record the general inclination. This is a soft signal -- actual trade-offs
  are presented during architecture review with per-recommendation cost/benefit.
- "Any other preferences or requirements I should know about?"

Can be condensed to a single question if earlier stages have already revealed
clear preferences.

Write findings to `## Preferences` section.

---

## Question Design Principles

- All questions MUST use plain language. Avoid technical jargon. Say "version
  control" not "VCS", say "build your code" not "CI/CD pipeline", say
  "assistant" not "agent". The user may not be a developer.
- Each relay round should ask 2-5 questions (not 1, not 10).
- Questions must not repeat information already gathered.
- Maximum 5 relay rounds. If you still need answers after 5 rounds, proceed
  with what you have and note assumptions in Intake Notes.

---

## GENESIS.md Format

Write the file incrementally, filling in sections as each stage completes:

```markdown
# Environment Genesis

Created: YYYY-MM-DD
Intake Path: Deep Interview
Base Profile: Custom
INTAKE_STATUS: IN_PROGRESS | COMPLETE

## Project Overview
[What the project is, what it does, team size, primary need]

## Technical Environment
[Languages, VCS, build system, test framework, CI/CD]
[Or "N/A -- non-technical project"]

## Workflow
[Typical task flow, quality gates, pain points, automation desires]

## Roles and Constraints
[Desired specializations, hard constraints, autonomy preferences]

## Team Role Diversity
[Solo / Team-same-role / Team-multi-role]

## External Services
[Service list with access levels, or "None specified"]

## Codebase Scale and RAG Strategy
[Codebase size estimate, retrieval approach, or "N/A -- fresh project"]

## Reference Documents
[Document types, formats, volume, parsing tool, or "None"]

## Task Complexity and Tracking
[Single-session vs multi-session, dependencies, parallel work, VCS type]

## AI Tool Budget and Multi-Model Usage
[Budget tier, other AI tools, routing recommendations, or "Codex only"]

## Token Efficiency Priority
[cost-conscious / balanced / quality-first]

## Setup Tolerance
[lean simple / no strong preference / lean full-featured]
[Any specific tools the user already uses or explicitly wants/rejects]
[Note: actual complexity decisions made per-recommendation during architecture review]

## Sensitive Data Handling
[Data types, regulatory frameworks, enforcement preference]

## AI Ecosystem Extensions
[Capability gaps and chosen tools, or "None -- native capabilities sufficient"]

## Preferences
[Communication style, documentation preferences, other]

## Modifications from Base Profile
N/A -- custom intake

## Intake Notes
[Assumptions made, gaps in information, follow-up suggestions]
```

---

## Re-invocation Protocol

When re-invoked after answers are provided:

1. Read GENESIS.md at the genesis_path.
2. Find the `## Pending Questions` section.
3. Process each Q&A pair, extracting information into the appropriate sections.
4. Determine which stage you are in and what information is still missing.
5. Either:
   a. Write new questions for the next stage (set `STATUS: AWAITING_ANSWERS`), OR
   b. If all stages complete, set `INTAKE_STATUS: COMPLETE` at top and remove
      the Pending Questions section.

---

## Edge Cases

**Contradictory answers**: Note the contradiction, write a clarifying question
in the next Pending Questions batch, and record the resolution in Intake Notes.

**User provides a document or spec**: Read it, extract answers to the interview
questions, write what you found to GENESIS.md, then ask only for the gaps.

**Unclear domain**: Focus on workflow (Stage 3). How work gets done matters more
than domain labels. Map workflow patterns to the closest starter profile for
structural guidance. Note in Intake Notes: "Non-standard domain. Architecture
based on workflow similarity to [closest profile]."

---

## Domain Classification Logic

When mapping an unfamiliar project to structural patterns:

1. Identify primary output type: code, documents, data, infrastructure, mixed
2. Identify work cadence: continuous, project-based, sprint-based, ad-hoc
3. Identify quality gates: automated (tests, builds), manual (reviews, approvals),
   regulatory (compliance checks), or none
4. Map to closest starter profile based on strongest signal:
   - Produces code -> software-development (game/engine work -> the game-development bundled domain)
   - Produces documents/research -> knowledge-work
   - Produces data/reports -> data-analysis
   - Manages infrastructure -> devops-infrastructure
5. Record mapping rationale in Intake Notes
