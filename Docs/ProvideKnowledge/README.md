# ProvideKnowledge

Drop files here to contribute knowledge to the Claude Harness Generator.

The Harness Generator's `/update` command scans this folder, validates the content,
incorporates useful findings into the knowledge base, and moves processed
items to the Processed/ subfolder. Use `/update` in its local-only mode
(say "process knowledge" or "I added some docs to ProvideKnowledge") to
ingest these files without running web research.

---

## What to Contribute

Anything that helps the Harness Generator generate better environments:

- **Best practices** you have discovered through using Claude Code
- **Configuration patterns** that worked well (or failed) for your project
- **Prompt engineering findings** (what phrasing works, what does not)
- **Skill descriptions** that trigger reliably (or ones that do not)
- **Agent patterns** that improved your workflow
- **Memory structures** that scaled well
- **Settings.json configurations** for specific ecosystems
- **Hook configurations** that caught real problems
- **Starter profile suggestions** for domains not yet covered
- **Bug reports** about generated environments that did not work correctly

---

## How to Contribute

### Option 1: Drop a File

Create a Markdown file in this directory with your findings. Use any
filename you like (it will be renamed during processing).

Recommended structure:

```markdown
# [Topic]

## Context
[What project/domain this applies to]
[What version of Claude Code you were using]

## Finding
[What you discovered, as specifically as possible]

## Evidence
[How you know this works -- test results, before/after, metrics]

## Suggested Action
[How the Harness Generator should use this information]
```

### Option 2: Drop a Configuration File

If you have a working settings.json, CLAUDE.md, rule file, or skill
definition that you think is well-crafted, drop a copy here. Include
a short note explaining what project it was made for and why it works well.

### Option 3: Drop a Link

Create a text file containing a URL to a blog post, documentation page,
or discussion thread with relevant information. Include a one-line
description of what the link contains.

```
https://example.com/article-about-claude-code-tips
Claude Code tips for Python projects -- covers virtual env handling and pytest integration
```

---

## What Happens After You Contribute

1. Run `/update` (it ingests pending ProvideKnowledge/ docs first, then
   web-researches; local-only mode skips the web research)
2. The Harness Generator reads each unprocessed file
3. It classifies the content (best practice, ecosystem config, bug report, etc.)
4. It cross-validates against existing knowledge (avoids duplicates, checks conflicts)
5. Validated findings are incorporated into:
   - `Docs/AgentGuidelines/Topics/` (general practices, as individual topic files)
   - `Docs/StarterProfiles/` (ecosystem-specific patterns)
   - `Docs/Templates/` (if the finding improves a template)
6. The original file is moved to `Processed/` with a processing note

You can check `Processed/` to see what was done with your contribution.

---

## Quality Guidelines

Contributions are most useful when they include:

- **Specificity**: "Adding `Bash(pytest *)` to settings.json allow list
  prevents permission prompts during test runs" is better than "make sure
  permissions are set up right."

- **Evidence**: "I tested this with 3 projects and it worked each time"
  is better than "I think this might work."

- **Context**: "This applies to Python projects using Poetry for dependency
  management" is better than "this is a good pattern."

- **Actionability**: "The Harness Generator should add X to Y when Z" is better
  than "something about X could be improved."

Low-quality contributions (vague opinions, untested ideas, generic advice)
will be noted but may not be incorporated.

---

## Folder Structure

```
ProvideKnowledge/
  README.md           <- You are here
  Processed/          <- Items that have been reviewed and incorporated
  [your-files-here]   <- Drop new contributions here
```

---

## Processing Status

Files in this directory are unprocessed. After `/update` runs:
- Successfully incorporated files move to `Processed/` with a note
- Files that were not actionable also move to `Processed/` with explanation
- Nothing is deleted -- you can always review what happened

---

## Questions or Issues

If you contributed knowledge that was not incorporated and you think it
should have been, check the processing note in `Processed/`. If you
disagree with the decision, re-submit with additional evidence or context.
