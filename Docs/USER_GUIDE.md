# Codex Harness Generator -- User Guide

This guide walks you through using the Codex Harness Generator to build a
customized AI assistant environment for your project. Whether you write code,
analyze data, draft legal briefs, or develop games, the Harness Generator interviews you
about your work and generates an assistant tailored to how you operate.

Reading time: about 15-20 minutes.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Fast Deterministic Path](#fast-deterministic-path)
- [Getting Started: Creating Your First Environment](#getting-started-creating-your-first-environment)
- [Starter Profiles](#starter-profiles)
- [The Deep Interview (No Profile Fits)](#the-deep-interview-no-profile-fits)
- [File Processing Features](#file-processing-features)
- [Reviewing an Existing Environment](#reviewing-an-existing-environment-validate-environment)
- [Updating the Harness Generator's Knowledge](#updating-the-creators-knowledge-update)
- [Tips and Common Scenarios](#tips-and-common-scenarios)
- [Your First Week](#your-first-week)
- [What Gets Generated](#what-gets-generated)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have the following:

**Required:**

- **Codex CLI** (version 1.0 or later). This is OpenAI's command-line
  tool for working with Codex. Install it from
  https://developers.openai.com/codex. You will also need an
  OpenAI API key or a Codex Max subscription.

- **A project directory.** This is the folder on your computer where your
  project lives (or will live). It can be an existing project with files
  already in it, or an empty folder for a new project. The Harness Generator generates
  its files into this directory.

- **Basic terminal familiarity.** You need to know how to open a terminal
  (Command Prompt, PowerShell, or Terminal app), navigate to a folder with
  `cd`, and type commands. That is all.

**Optional (for file processing features):**

- **Python** (version 3.10 or later). Needed if your work involves reading or
  processing Excel spreadsheets, Word documents, PDFs, or PowerPoint files.
  The Harness Generator uses a Python library called MarkItDown to convert these formats
  into text that the assistant can understand. Install Python from
  https://python.org if you do not already have it.

- **Pandoc.** Needed if your work produces formatted documents (Word files,
  presentations, PDFs) for clients, boards, or other external audiences. Pandoc
  converts the assistant's text output into professionally formatted files.
  Install with `winget install pandoc` on Windows or `brew install pandoc` on
  macOS.

You do not need to install Python or Pandoc right now. The Harness Generator will tell
you during setup if your project needs them.

---

## Fast Deterministic Path

If you want to try the generator without a full model-mediated `/create`
interview, use the deterministic CLI path first. It is the quickest way to see
what a Codex harness looks like on disk and to verify the local evaluator.

```bash
cd /path/to/Codex-Harness-Generator
python scripts/codex_harness.py profiles --details
python scripts/codex_harness.py recommend "RAG app with prompts, evals, and retrieval checks"
python scripts/codex_harness.py brief-acceptance /tmp/codex-rag-harness \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --project-name "RAG Quality Harness" \
  --force
python scripts/codex_harness.py eval /tmp/codex-rag-harness
python scripts/codex_harness.py smoke /tmp/codex-rag-harness
```

This path writes the same core Codex-facing files as the generated examples:
`AGENTS.md`, `.codex/config.toml`, `.codex/agents/`, `.agents/skills/`,
environment docs, `CREATION_CONTEXT.md`, `CREATE_ACCEPTANCE_REPORT.md`, and
`PROFILE_SELECTION.md`. The profile recommendation is deterministic and
explainable. Recommendation output includes a confidence label; if confidence
is low or the selected profile does not fit your project, use the full
`/create` flow below.

---

## Getting Started: Creating Your First Environment

This section walks through the full creation process step by step.

The full creation process typically takes 10-20 minutes. This includes the
interview, architecture design, five generation passes, and validation.

The pipeline uses several specialized assistants behind the scenes (an
architect, a generator run five times, and a validator). Each consumes API
credits. If you are on a metered API plan, expect the creation process to use
approximately 100,000-200,000 tokens.

### Step 1: Open the Harness Generator

Open a terminal and navigate to the Codex-Harness-Generator directory:

```
cd /path/to/Codex-Harness-Generator    # macOS/Linux
cd C:\path\to\Codex-Harness-Generator  # Windows
```

Then start Codex:

```
codex
```

You will see a prompt where you can type messages to the Harness Generator.

### Step 2: Start the creation process

Type `/create` and press Enter.

You can also just describe your project in plain language -- for example,
"I need a Codex environment for my accounting practice" -- and the Harness Generator
will recognize that you want to create a new environment. But `/create` is the
most direct way.

### Step 3: Provide your project directory

The Harness Generator asks for the path to your project directory. Type the full path --
for example:

```
/Users/YourName/Projects/MyProject       # macOS
/home/YourName/Projects/MyProject        # Linux
C:\Users\YourName\Projects\MyProject     # Windows
```

The Harness Generator verifies the directory exists and that it can write files there. If
the directory does not exist, it creates it for you. If the directory already
contains Codex files (a `AGENTS.md` or `.codex/` folder), the Harness Generator
notes this and handles any conflicts during generation.

You will see a confirmation message like:

> Target directory: confirmed writable
> Existing files: none found
> The creation pipeline will now begin.

### Step 4: Answer the experience question

The Harness Generator asks how familiar you are with AI assistants and command-line tools.
Your answer calibrates the complexity of your generated environment:

- **"Just getting started"** -- Fewer assistants, simpler documentation, and
  your getting-started guide includes terminal basics.
- **"Somewhat familiar"** -- Standard setup with clear documentation.
- **"Very comfortable"** -- Full-featured environment with technical
  documentation.

### Step 5: Choose a starting point (preset or custom)

The Harness Generator offers two ways to start:

- **Preset (fast).** Pick one of the four slim base profiles (Software
  Development, Knowledge Work, Data & Analysis, DevOps & Infrastructure) or one
  of the 16 bundled domain profiles in `Docs/DomainLibrary/` (for example game
  development, data science, legal research, financial modeling, grant writing,
  course design, product management). A preset is a pre-built
  starting point that the Harness Generator then customizes to your specifics. This is
  the quickest path. (See [Starter Profiles](#starter-profiles) below for
  details on each base profile.)
- **Custom (more tokens/time).** For a long-term, reusable harness, the Harness Generator
  can synthesize a fresh `DOMAIN_PROFILE.md` tailored to your domain during
  architecture. This costs more tokens and time but produces a profile you can
  reuse across future environments.

If you are not sure which domain you fall under, `Docs/DomainLibrary/DOMAIN_REFERENCE.md`
maps roughly 20 common domains to a recommended starting point.

Pick the one that best describes your work. If none of them fit, say "none of
these" -- the Harness Generator switches to a more detailed interview. (See
[The Deep Interview](#the-deep-interview-no-profile-fits).)

### Step 6: Customize your profile

After you select a profile, the Harness Generator asks 2-3 rounds of follow-up questions
to tailor it to your specific needs. These questions cover:

- What languages, frameworks, or tools you use
- Whether you have specific workflow steps or approval gates
- Whether you work alone or on a team
- Things the assistant should always do or never do
- Whether you work with data files (spreadsheets, CSV, databases)
- Whether your work involves sensitive or regulated data
- Whether you repeat the same process for different clients or projects
- What documents your work produces and who sees them
- Whether your organization has brand guidelines or templates

You do not need to answer every question in detail. Short answers work fine --
the Harness Generator adapts based on what you share.

### Step 7: Confirm external services

The Harness Generator asks about external services your project uses -- things like
GitHub, Jira, Notion, databases, or APIs. This determines whether the
environment should include integrations with those services.

If you do not use any, just say so.

### Step 8: Review and confirm the plan

The Harness Generator presents a summary of what it intends to build:

- Which assistants it will create and what each one handles
- What rules it will put in place
- What commands will be available
- How your project's memory and state management will work

Review this summary. If something looks wrong or missing, say so -- the Harness Generator
adjusts before proceeding. When it looks right, confirm and the Harness Generator begins
generating.

### Step 9: Watch the generation progress

The Harness Generator builds your environment in five passes, reporting progress after
each one:

1. "Creating foundation files... done (1/5)" -- The main instructions file,
   behavioral rules, permissions, and safety settings.
2. "Creating assistant definitions... done (2/5)" -- Specialized assistants
   for your domain (research, drafting, review, etc.).
3. "Creating commands... done (3/5)" -- Slash commands you can use
   (saving progress, checking health, etc.).
4. "Creating infrastructure... done (4/5)" -- Your project's memory structure,
   self-learning system, and state management.
5. "Creating documentation... done (5/5)" -- Your getting-started guide and
   cross-reference verification.

### Step 10: Validation

After generation, the Harness Generator runs an automatic validation that checks your new
environment against its quality checklist (the single source of truth is
`Docs/Templates/References/validation-guide.md`). It verifies that all files
reference each other correctly, permissions are properly configured, no
contradictory rules exist, and the environment is ready to use. The validator
also runs a build-time drift audit and boundary-crossing checks.

If the validator finds critical issues, the Harness Generator fixes them automatically
(up to two retries). Warnings are reported but do not block you from using the
environment.

### Step 11: Start using your environment

The Harness Generator presents a final summary showing:

- What was generated (file list)
- How to get started (step by step)
- A short smoke test you can run to verify everything works

To start using your new environment:

1. Open a terminal
2. Navigate to your project directory: `cd /path/to/YourProject`
3. Run: `codex`
4. Your customized assistant is ready. Try saying hello -- it will greet you
   and describe what it can help with.

---

## Starter Profiles

The Harness Generator offers four slim base profiles, described below. Each one comes
pre-configured with assistants, rules, commands, and permissions suited to its
domain. During setup, you customize whichever profile you choose.

In addition to these four base profiles, the Harness Generator bundles 16 ready-made
domain profiles in `Docs/DomainLibrary/` -- including API design, book
publishing, course design, customer support, data engineering, data science,
financial modeling, game development, grant writing, hiring pipeline, legal
research, LLM apps, market research, product management, security audit, and
social media. These are narrower starting points you can pick directly. If none fit, the Harness Generator can
synthesize a fully custom `DOMAIN_PROFILE.md` instead (see Step 5). The base
profile format is documented in `Docs/StarterProfiles/PROFILE_FORMAT.md`.

### Software Development

**For:** Developers building web apps, APIs, command-line tools, libraries, or
services in Python, JavaScript/TypeScript, Go, Rust, Java, or C#.

**What you get:**

- Six specialized assistants: a researcher (finds documentation and patterns),
  a planner (breaks features into steps), an implementer (writes code), a
  reviewer (checks code quality), an explorer (navigates your codebase), and a
  debugger (diagnoses and fixes bugs).
- Git integration with safe command handling (the assistant will not force-push
  or delete branches without asking).
- Pre-configured permissions for your programming language's tools (package
  managers, test runners, linters, formatters).
- The assistant acts proactively -- it does the work and reports what it did,
  rather than asking permission for every step.

**Best for:** Solo developers or small teams building software with standard
toolchains and Git-based workflows.

### Knowledge Work

**For:** Researchers, lawyers, financial analysts, technical writers, policy
analysts, and other professionals whose primary output is documents and
analysis rather than code.

**What you get:**

- Three assistants with plain-language names: a research assistant (finds and
  synthesizes information), a drafting assistant (writes and edits documents),
  and a review assistant (checks documents for accuracy and quality).
- Conservative behavior -- the assistant asks before searching the web on
  sensitive topics or overwriting existing documents.
- Executive and technical output styles so you can request the right format
  for your audience.
- File processing support for reading Word documents, PDFs, spreadsheets, and
  PowerPoint files, plus optional formatted document output.

**Best for:** Professionals who need help with research, drafting, and review
but do not write code as their primary work.

### Data & Analysis

**For:** Accountants, financial analysts, data scientists, business analysts,
researchers with datasets, healthcare administrators, real estate analysts, and
anyone who works primarily with structured data.

**What you get:**

- Four assistants: a research assistant (looks up standards, regulations,
  methodologies), a data analyst (reads spreadsheets, runs calculations,
  generates output files using Python), a report writer (drafts reports and
  memos from analysis results), and a quality checker (verifies calculations
  and audits reports).
- Python-powered data processing for reading Excel files, performing financial
  calculations, building forecasts, and generating output files.
- A data safety rule: the assistant never modifies your original data files.
  It always creates new output files with dated names.
- Financial, analytical, and executive output styles.
- A `/process-data` command that catalogs your data files on first use --
  it reads each file's structure, column names, data types, and row counts.

**Best for:** Professionals who work primarily with spreadsheets, CSV files, and
structured data -- financial modeling, variance analysis, data cleaning,
reporting -- but do not write software as their primary work.

### DevOps & Infrastructure

**For:** DevOps engineers, SRE teams, platform engineers, and infrastructure
specialists managing cloud platforms, CI/CD pipelines, container orchestration,
and system reliability.

**What you get:**

- Five specialized assistants: a researcher (finds cloud documentation,
  infrastructure patterns, and best practices), a planner (designs
  infrastructure changes with rollback plans), an implementer (writes IaC code
  and pipeline configs), a reviewer (checks for security and reliability
  issues), and an incident responder (helps diagnose and resolve production
  issues).
- Infrastructure safety gates -- the assistant never applies changes to
  production without explicit confirmation. Destructive operations (teardown,
  scale-to-zero, security group changes) require approval.
- IaC protection -- Terraform state files, Kubernetes secrets, and cloud
  credentials are never read or modified directly.
- Pre-configured permissions for infrastructure tools (terraform, kubectl,
  docker, aws/gcloud/az CLIs, ansible).
- Incident response workflow with structured diagnosis, mitigation tracking,
  and post-incident review.

**Best for:** Teams managing cloud infrastructure, CI/CD pipelines, container
platforms, or on-call rotations who want an assistant that understands
infrastructure safety and operational discipline.

---

## The Deep Interview (No Profile Fits)

If none of the base profiles or bundled domain profiles matches your project,
select "none of these." The Harness Generator switches to a five-stage deep interview
that gathers enough information to build a fully custom environment from
scratch.

The five stages are:

1. **Project overview.** What your project is, what it produces, your team
   size, and the main thing you want help with.
2. **Technical environment.** Languages, version control, build systems, and
   external services (skipped entirely for non-technical projects).
3. **Workflow.** Your typical task flow from start to finish, any approval
   steps, your biggest pain points, and whether you repeat the same process
   for different clients or cases.
4. **Roles and specializations.** What specialized assistants would help you,
   what the assistant should never do without asking, and whether your work
   involves sensitive data.
5. **Preferences.** Communication style, documentation preferences, and
   anything else the Harness Generator should know.

The interview is conversational. The Harness Generator asks questions in plain language
and adapts based on your answers. For simple projects, it condenses the
questions. For complex ones, it asks follow-ups.

This path takes longer than choosing a profile (typically 5-10 minutes of
questions instead of 2-3), but it produces a fully tailored environment that
matches your specific work.

---

## File Processing Features

If your work involves documents, spreadsheets, or presentations, the Harness Generator
can set up your environment to read and produce these file formats.

### Reading files (inbound)

The assistant uses a tool called MarkItDown to convert office documents into
text it can process. Supported formats include:

- Excel spreadsheets (.xlsx, .xls)
- Word documents (.docx)
- PowerPoint presentations (.pptx)
- PDF files (.pdf)
- CSV and JSON files
- HTML pages
- Images (extracts metadata and performs basic text recognition)

After conversion, the assistant can summarize, analyze, compare, or extract
information from any of these files.

### Producing formatted output (outbound)

If you need the assistant to produce professionally formatted documents --
Word files, PowerPoint decks, or PDFs -- the environment uses Pandoc to convert
the assistant's text output into formatted files. This is especially useful
when producing deliverables for clients, boards, or other external audiences.

### The Inbox/Outbox workflow

For environments with file processing, the Harness Generator sets up two special folders:

- **Inbox/** -- Drop files here for the assistant to process. You can say
  something like "Summarize the report in Inbox/" or "Analyze the spreadsheet
  in Inbox/data.xlsx."
- **Outbox/** -- The assistant places its generated output here. Find your
  finished reports, cleaned data files, or converted documents in this folder.

### Brand guidelines

If your organization has brand guidelines or document templates, you can use
them with the assistant:

1. After your environment is created, find the `Brand/` folder (if the Harness Generator
   determined you need it based on your answers).
2. Drop your brand guide (PDF, Word, etc.) into `Brand/Guidelines/`.
3. Drop your document templates (.docx, .pptx) into `Brand/Templates/`.
4. The assistant automatically reads these materials and applies your brand
   standards when producing formatted documents.

When you update your brand assets, the assistant detects the changes and
refreshes its knowledge automatically the next time it produces a document.

### Setup

If the Harness Generator determines your project needs file processing, your
getting-started guide will include the specific install commands. The typical
setup is:

```
pip install 'markitdown[all]'
```

This one command installs the file reader. If you also need formatted document
output, the guide will tell you to install Pandoc:

```
winget install pandoc
```

(On macOS, use `brew install pandoc` instead.)

---

## Reviewing an Existing Environment: /validate-environment

If you already have a Codex environment and want to check whether it is
set up correctly, the Harness Generator can audit it.

### Step 1: Start the Harness Generator

Open a terminal, navigate to the Codex-Harness-Generator directory, and run
`codex`.

### Step 2: Run the validator

Type `/validate-environment` and press Enter.

### Step 3: Provide the path

The Harness Generator asks for the path to the environment you want to check. Type the
full path to the project directory (the folder containing `AGENTS.md` or
`.codex/`).

### Step 4: Review the results

The validator runs its full checklist (see
`Docs/Templates/References/validation-guide.md`, the single source of truth)
covering four categories:

**Structural checks** -- Do all the pieces exist and fit together?
- Referenced files actually exist on disk
- Assistant definitions have the right format
- Command definitions have proper trigger phrases
- Permissions file is valid and includes safety rules

**Consistency checks** -- Do the pieces agree with each other?
- Assistants mentioned in routing rules actually exist
- Commands mentioned in the main instructions file actually exist
- No contradictory rules across different rule files
- No orphaned components that nothing references

**Quality checks** -- Are the pieces well-made?
- Files are appropriately sized (not too long or bloated)
- Rules explain WHY, not just WHAT
- No unnecessary role-setting language
- Command trigger phrases are specific enough to avoid false matches

**Completeness checks** -- Is anything missing?
- Getting-started guide exists and is complete
- Progress-saving command covers all necessary categories
- Memory index exists and matches the actual file structure

### Step 5: Interpret the results

The validator reports one of three overall verdicts:

- **PASS** -- Everything checks out. No issues found.
- **WARN** -- Some improvements are possible, but nothing is broken. The report
  lists each warning with an explanation.
- **FAIL** -- One or more critical issues need fixing. The report describes each
  failure, explains why it matters, and suggests how to fix it.

### Step 6: Fix issues

If the validator found problems, it offers to create a fix plan grouped by
effort level:

- **Quick fixes** (1-2 file edits) -- typos, missing references, small
  formatting issues.
- **Medium fixes** (new files needed) -- missing components, incomplete
  configurations.
- **Large fixes** (structural changes) -- contradictory rules, fundamental
  architecture issues.

You choose which fixes to apply. The validator does not make changes
automatically -- it only reports and suggests.

---

## Updating the Harness Generator's Knowledge: /update

The Harness Generator has its own knowledge base about best practices for building AI
assistant environments. You can update this knowledge in two ways.

### Adding your own knowledge

If you have documents about Codex best practices, environment design
tips, or lessons learned:

1. Place the documents in the `Docs/ProvideKnowledge/` folder inside the
   Codex-Harness-Generator directory.
2. Start Codex in the Codex-Harness-Generator directory.
3. Type `/update`, or simply say something like "process knowledge" or "I added
   some docs." This triggers `/update` in its local-only mode, which ingests
   `Docs/ProvideKnowledge/` without searching the web.
4. The Harness Generator reads each document, classifies it by topic, assesses its
   reliability, and incorporates validated findings into its knowledge base.
5. Processed files are moved to `Docs/ProvideKnowledge/Processed/` so they
   are not re-processed.

Future environments you create will benefit from the updated knowledge.

### Refreshing from official sources

Type `/update` to also have the Harness Generator search for the latest Codex
Code documentation and best practices from OpenAI. It checks for new
features, breaking changes, and updated recommendations, then incorporates
anything new into its knowledge base.

---

## Tips and Common Scenarios

### "I already have a AGENTS.md"

The the Harness Generator detects existing Codex files during setup and notes them. It
handles conflicts during the generation process -- existing files are not
silently overwritten. You will be informed of what was found.

### "I want to regenerate just part of my environment"

There is no single command that regenerates one file in isolation, but there
are several approaches depending on the scope of the change:

- **Small tweaks.** Edit the generated files directly. They are plain Markdown
  and JSON files designed to be readable and editable. This is the primary
  approach for adjusting rules, adding permissions, or rewording instructions.
- **Larger changes.** Re-run `/create` to go through the full process again
  with updated answers. If the process is interrupted, it offers a resume
  option so you do not lose progress.
- **Targeted fixes.** Run `/validate-environment` against your project. It
  identifies specific issues (broken references, missing files, contradictory
  rules) and suggests targeted fixes you can apply individually.
- **Tracking what was generated.** The generated `VERSION.md` file in your
  environment records what was generated and when, so you can see which files
  came from the Harness Generator versus which you edited by hand.

### "My project does not fit any category"

Select "none of these" when the profiles are presented. The Harness Generator switches
to a detailed five-stage interview that builds a completely custom environment
based on your answers. This works for any kind of project.

### "I need to process Excel, PDF, or Word files"

The Harness Generator asks about this during the intake questions. If you mention working
with data files or office documents, it configures the right tools
automatically. You do not need to set this up yourself -- just answer the
questions honestly and the Harness Generator handles the configuration.

### "I have brand guidelines"

After your environment is generated, look for the `Brand/` folder in your
project directory. Drop your brand guide documents into `Brand/Guidelines/`
and your document templates (.docx, .pptx) into `Brand/Templates/`. The
assistant reads them automatically and applies your brand standards to
formatted output.

Note: The `Brand/` folder is only created if you indicated during intake that
your work has brand requirements.

### "I want a simpler environment"

If the generated environment feels like too much, there are two paths to a
lighter setup:

- **Automatic.** During intake, answer "Just getting started" to the
  experience question. The Harness Generator generates a simpler environment
  automatically -- fewer agents, simpler routing rules, and lighter
  documentation.
- **Manual.** After generation, remove what you do not need. Delete agent
  files from `.codex/agents/`, skill folders from `.agents/skills/`, or
  rule files from `.codex/rules/`. Update references in `AGENTS.md` when
  you remove something.

The minimum viable environment is just three things: `AGENTS.md`,
`.codex/config.toml`, and one rule file. Everything else is optional and
can be added back later as your needs grow.

### "I want to contribute to the Harness Generator"

See the CONTRIBUTING.md file in the Codex-Harness-Generator directory. It
covers how to add new starter profiles, create or update templates, improve the
knowledge base, and test your changes.

---

## Your First Week

A practical checklist for getting comfortable with your new environment.

### Day 1: Verify the basics

1. Open a terminal, navigate to your project directory, and run `codex`.
2. Say hello. The assistant should greet you and describe what it can help with.
3. Run `/state-save` to save your session, then `/state-load` to restore it.
   Confirm the round-trip works.
4. Run `/health-check` to verify the environment is intact. Fix anything it
   flags.

### Days 2-3: Use it for real work

5. Bring a real task -- something you would normally do yourself -- and work
   through it with the assistant.
6. Try each slash command at least once so you know what is available.
7. Note any friction: commands that feel awkward, rules that get in the way,
   missing permissions that force unnecessary confirmation prompts.

### Days 4-5: Let the self-learning system work

8. Run `/update`. The self-learning system analyzes how the assistant has been
   working and proposes improvements based on friction it observed.
9. Review each suggestion. Approve the ones that make sense, dismiss the rest.
10. If you hit a recurring annoyance, check whether a rule or permission
    change would fix it and edit the file directly.

### End of week: Review and tune

11. Check `Docs/_working/retro/` for friction patterns the system logged.
12. Decide if any rules need tweaking. Common early adjustments:
    - Loosening autonomy rules (if the assistant asks too often)
    - Tightening autonomy rules (if it acts when you wanted it to ask)
    - Adding project-specific terminology or conventions
13. Run `/health-check` one more time to confirm everything is still consistent
    after your edits.

---

## What Gets Generated

When the Harness Generator finishes, your project directory will contain these components
(the exact set depends on your answers during intake):

### AGENTS.md

The main instructions file for your assistant. It defines what the assistant
does, how it routes your requests, what it can and cannot do, and its core
behavioral rules. This file is under 250 lines by design -- it is meant to be
readable.

### .codex/rules/

Behavioral rules that govern how the assistant operates. These cover topics
like:

- How to decide which assistant handles a request (routing)
- What the assistant can do on its own versus what requires your approval
- How to manage context when conversations get long
- How the assistant learns and improves over time
- How to handle errors gracefully
- Domain-specific rules (version control safety, data handling, build systems,
  testing gates, etc.)

### .codex/agents/

Specialized assistants for different parts of your work. Each one has a defined
role, reasoning effort, sandbox scope, and instructions for when to invoke it.
For example, a research assistant can be read-only, while an implementer can use
workspace-write scope when the task requires file edits.

### .agents/skills/

Commands you can type to trigger specific actions. Every generated environment
includes at least these four:

- `/state-save` -- Saves your current session progress so you can close the
  terminal and pick up later.
- `/state-load` -- Restores your session from a saved state.
- `/update` -- Analyzes how the assistant has been working and proposes
  improvements.
- `/health-check` -- Validates that your environment is intact and reports
  any issues.

Additional commands depend on your profile (for example, `/build` and
`/review` for development projects, or `/process-data` for data analysis
projects).

### .codex/config.toml

Permissions and tool access configuration. This file controls what the
assistant is allowed to do without asking -- for example, reading any file in
your project, running your test suite, or searching the web. It also defines
what the assistant is never allowed to do -- for example, deleting files, running
administrator commands, or reading secret credentials.

### Docs/ (or Memory/)

Your project's knowledge and state management system. This includes:

- **Memory/** -- Project knowledge organized by topic. The assistant loads an
  index file on startup and retrieves specific documents on demand, keeping
  conversations efficient.
- **State/** -- Session snapshots for saving and resuming your work.
- **Retro/** -- The self-learning system. The assistant tracks friction
  patterns (things that went wrong or could be improved) and periodically
  proposes improvements.
- **Environment/** -- Metadata about how your environment was generated,
  including the original intake answers and architecture decisions.

### GETTING_STARTED.md (inside Docs/)

A plain-language guide written specifically for your project. It explains what
the assistant can do, how to start a session, what commands are available, and
suggests a few things to try first. Share this with teammates who will use the
environment.

---

## Troubleshooting

### "The Harness Generator says it cannot write to my directory"

Check that the directory path is correct and that you have write permissions.
On Windows, try running your terminal as Administrator if the directory is in a
protected location. On macOS/Linux, check folder permissions with `ls -la` and
fix with `chmod 755 <directory>` or use `sudo` if needed. Better yet, use a
directory in your user folder where you have full permissions.

### "The intake feels too long"

You can give short answers. The Harness Generator adapts to however much detail you
provide. If you are not sure about a question, say "I'm not sure" or "skip
this" -- the Harness Generator uses sensible defaults for anything you do not specify.

### "I want to change something after generation"

Edit the generated files directly. They are plain Markdown and TOML files
designed to be readable. Alternatively, re-run `/create` to go through the
full process again with different answers.

Common files you might want to tweak:

- `AGENTS.md` -- Adjust rules, add constraints, change routing.
- `.codex/config.toml` -- Add or remove permissions.
- `.codex/rules/01-autonomy.md` -- Change what the assistant does
  automatically versus what it asks about.
- `Docs/index.md` -- Update your project wiki / knowledge index.

### "File processing is not working"

Check that the required tools are installed:

- For reading office documents: `pip install 'markitdown[all]'`
- For producing formatted output: verify Pandoc is installed with
  `pandoc --version`
- For Excel processing: `pip install openpyxl`

If you see permission errors, check `.codex/config.toml` to make sure the
relevant operations are represented in the permission policy.

### "The assistant keeps asking for permission to do things"

This usually means `.codex/config.toml` is missing the permissions the assistant
needs. Open the file and add the narrowest safe permission for the specific
operation that keeps prompting.

### "The environment seems too complex for my project"

The Harness Generator calibrates complexity based on your answers during intake. If you
selected an experience level of "just getting started" and your project is
simple, the environment should be lightweight. If it still feels like too much,
you can delete components you do not need -- remove agent files from
`.codex/agents/`, skill folders from `.agents/skills/`, or rules from
`.codex/rules/`. Just make sure to update references in `AGENTS.md` when you
remove something.

### "I want to validate my environment but I'm not in the Harness Generator directory"

You need to run `/validate-environment` from within the Codex-Harness-Generator
directory (not your project directory). Start Codex there, run the command,
and provide your project's path when asked.
