# Contributing to Codex Harness Generator

Thank you for your interest in improving the Harness Generator. This guide covers the main ways to contribute.

## Ways to Contribute

### 1. Add a Starter Profile

There are two profile collections, both following the SLIM format:

- **Base starter profiles** live in `Docs/StarterProfiles/` (software-development,
  knowledge-work, data-analysis, devops-infrastructure).
- **Bundled domain profiles** live in `Docs/DomainLibrary/` (16 ready-made
  domains such as game-development, data-science, data-engineering,
  legal-research, and product-management).

Profiles are SLIM by design: a profile is a *starting point the architect
adapts*, not a self-contained environment dump. It points at generator-read
templates rather than inlining their content. Read
`Docs/StarterProfiles/PROFILE_FORMAT.md` first -- it is the authoritative format
spec for both collections, and it explains why inlining agent definitions, rule
bodies, skill specs, or full permission-profile TOML is dead duplication the
generator never reads.

**To add a profile:**

1. Copy an existing profile (e.g., `software-development.md`) as your starting
   point, or a bundled domain from `Docs/DomainLibrary/` if it is closer.
2. Rename it to match your domain (e.g., `data-engineering.md`) and place it in
   the right collection (a broad base profile in `Docs/StarterProfiles/`, a
   ready-made specific domain in `Docs/DomainLibrary/`).
3. Fill in the required sections per `PROFILE_FORMAT.md`. Keep only what is
   domain-specific and not derivable from a template:
   - Profile metadata (name, target audience, complexity, memory tier, action default, VCS)
   - Component roster -- compact tables listing names + one-line role + (agents) model + template pointer. Do NOT paste YAML or instructions.
   - **Domain routing table** (10-16 domain-specific rows with notes + fallback chains) -- the real value of the profile
   - Ecosystem permissions -- name the Base + Universal Deny sets and the ecosystems needed (point to `Docs/Templates/References/ecosystem-permissions.md`); inline only domain-specific permissions not in that reference
   - Self-learning seed entries (4-6, marked `[PATTERN]`)
   - Hook suggestions (names + one-line purpose + template pointer)
   - Cost / model notes
   - Customization points
4. Add your profile to the matching index (`Docs/StarterProfiles/INDEX.md` or
   `Docs/DomainLibrary/INDEX.md`).
5. Test by generating an environment from your profile (see Testing below).

**Quality bar:** The routing table is the most important part. Generic entries like "bug -> debugger" are not acceptable. Every entry must include domain-specific context, e.g., "Pipeline failure -> debugger (check DAG logs + task dependencies) -> explorer -> debugger".

### 2. Create or Update Templates

Templates live in `Docs/Templates/` and serve as annotated reference implementations. They are NOT fill-in-the-blank forms -- the component-generator reads them as guidance.

**Template structure:**

Every template must include:
1. A complete working example of the component
2. HTML comment annotations explaining what each section does and WHY
3. Variation notes for different domains
4. Anti-patterns to avoid
5. Quality criteria for validation

**Annotation format:**
```html
<!-- ANNOTATION: [Section purpose]
     WHY: [Intent behind this section]
     ADAPT: [How to modify for different domains] -->
```

**To add a template:**
1. Write the template following the structure above
2. Place it in the appropriate directory (Core/, Optional/, Agents/, or Skills/)
3. If it's a new component type, update `Docs/Templates/README.md`

### 3. Improve the Knowledge Base

The knowledge base lives in topic files in `Docs/AgentGuidelines/Topics/`. It's organized into 18 topic files (numbering is non-contiguous), indexed by `Docs/AgentGuidelines/INDEX.md`.

**To add a recommendation:**

Each recommendation follows this format:
```markdown
### X.Y Topic Name

**Established**: YYYY-MM-DD (or "baseline")
**Source**: [Document name] (Tier N)

**Recommendation**: [Specific, actionable guidance]

**Anti-pattern**: [What to avoid and why]
```

Source tiers:
- Tier 1: OpenAI official documentation
- Tier 2: Validated community practice (multiple independent sources)
- Tier 3: Anecdotal (single source, unverified)

### 4. Contribute Research

Drop files into `Docs/ProvideKnowledge/` and run `/update` (its local-only mode
ingests pending docs without web research -- trigger it with phrasings like
"process knowledge" or "I added some docs to ProvideKnowledge"). The Harness Generator will:
1. Read and classify your contribution
2. Cross-validate against existing knowledge
3. Incorporate validated findings into the topic files
4. Move processed files to `Processed/`

Good contributions include:
- OpenAI documentation updates
- Codex changelog analysis
- Proven workflow patterns with evidence
- Industry-specific agent configurations that worked well

### 5. Report Issues

File issues with the GitHub issue templates for:

- Generated environments that don't work correctly
- Missing or incorrect best practices
- Intake questions that confuse users
- Validation checks that produce false positives/negatives
- External usage evidence

Include: what you expected, what happened, which profile you used, and the generated VALIDATION_REPORT.md if available.

## Testing Your Changes

### Quick Test

Run the deterministic gate first. It is fast, CI-safe, and does not require a
live model-mediated `/create` run:

```bash
cd Codex-Harness-Generator
python scripts/codex_harness.py doctor
python scripts/codex_harness.py profiles --details
python scripts/codex_harness.py recommend "RAG app with prompts, evals, and retrieval checks"
python scripts/codex_harness.py brief-acceptance /tmp/codex-brief-check \
  --brief "RAG app with prompts, evals, and retrieval checks" \
  --force
python scripts/codex_harness.py gate
```

If you changed generated example content, refresh the relevant checked-in
snapshots before running the gate:

```bash
python scripts/refresh_deterministic_examples.py
python scripts/refresh_create_acceptance_examples.py
python scripts/refresh_brief_acceptance_examples.py
python scripts/check_example_inventory.py
python scripts/codex_harness.py gate
```

For the richer live path, you can still run Codex in this repository, trigger
`/create`, select your profile, use a temporary target directory, and then run
`/validate-environment`. Treat that as additional live evidence, not a
substitute for the deterministic gate.

### What to Check

1. **Structural**: All files exist, cross-references resolve, .codex/config.toml is valid
2. **Quality**: AGENTS.md < 250 lines, rules < 120 lines, agents < 80 lines
3. **Routing**: Table has 10-16 domain-specific entries with fallback chains
4. **Skills**: Descriptions have 3+ trigger phrases and negative triggers
5. **Permissions**: .codex/config.toml covers all operations agents/skills will attempt
6. **First run**: The generated environment's first-run greeting works

### Proof And Evidence Checks

Before making public claims about readiness or usage, run:

```bash
python scripts/proof_status.py
python scripts/validate_usage_records.py \
  --min-records 2 \
  --require-non-synthetic \
  --require-success
```

The proof status report is conservative. It summarizes checked-in examples,
the installable CLI smoke, live task trials, and sanitized usage evidence; it
does not prove broad external adoption or that every future live `/create` run
will be ideal.

For external evidence, ask reporters to use the GitHub **External usage report**
issue template. Maintainers can convert privacy-safe reports into checked-in
records using `Docs/Environment/EXTERNAL_USAGE_EVIDENCE.md`.

### Validation Checklist

The environment-validator agent runs the full validation checklist automatically (see `Docs/Templates/References/validation-guide.md`, the single source of truth -- 22 core + 27 conditional + 6 hub checks, plus a Phase-0 drift audit and boundary-crossing checks). All checks should PASS. WARN is acceptable for non-critical items. FAIL must be fixed before merging.

## Roadmap

See `Docs/Environment/ROADMAP.md` for beta exit criteria, near-term product
proof work, and issue-intake guidance.

## Code of Conduct

Be respectful, constructive, and focused on improving the tool for everyone. We welcome contributors of all experience levels.

## Questions?

Open an issue or start a discussion. For questions about Codex itself, see the [OpenAI documentation](https://developers.openai.com/codex).
