# Starter Profiles Index

Starter profiles are pre-built environment configurations for common domains.
They are the primary path for ~80% of users -- select a profile, customize 2-3
things, and get a working environment in minutes.

Each profile includes: a component roster (agents/rules/skills as names +
template pointers), a domain routing table, ecosystem permissions (referenced),
self-learning seeds, memory tier, and cost guidance.

Profiles are **slim** (~110-170 lines) -- they point at templates rather than
inlining them. Format spec: `PROFILE_FORMAT.md`. For domains beyond these four,
see the 16 **bundled domains** in `Docs/DomainLibrary/` (`INDEX.md`) plus the
`DOMAIN_REFERENCE.md` routing map; for a domain none of those fit, use custom
generation (the architect synthesizes a reusable DOMAIN_PROFILE.md).

---

## Available Profiles

### 1. Software Development (`software-development.md`)

**Target audience**: Developers working on web apps, APIs, CLIs, libraries, or
services in any mainstream language (Python, Node/TypeScript, Go, Rust, Java, C#).

**Complexity**: Standard (6 agents, 7 rules, 6 skills)

**Key differentiators**:
- Language-aware ecosystem permissions (Python, Node, Go, Rust, Java, C#)
- Git integration with safe/dangerous command classification
- PostToolUse hooks for automatic test running
- Team template for large features (frontend + backend + tests)
- Proactive action default (act first, report after)

**Best for**: Solo developers or small teams building software with standard
toolchains and Git-based workflows.

---

### 2. Knowledge Work (`knowledge-work.md`)

**Target audience**: Researchers, lawyers, financial analysts, technical writers,
policy analysts, and other professionals whose primary output is documents and
analysis rather than code.

**Complexity**: Lite (3 agents, 6 rules, 5 skills)

**Key differentiators**:
- Plain-language agent names ("Research assistant", not "researcher")
- Conservative action default (ask before external actions)
- No VCS integration (document-centric workflow)
- Executive and technical output style templates
- Minimal ecosystem permissions (broad document read/write, limited Bash)

**Best for**: Professionals who need Claude to help with research, drafting,
and review but do not write code as their primary work.

---

### 3. Data & Analysis (`data-analysis.md`)

**Target audience**: Accountants, financial analysts, data scientists, business
analysts, researchers working with datasets, healthcare administrators tracking
metrics, real estate analysts, and anyone whose primary work involves processing
and analyzing structured data.

**Complexity**: Standard (4 agents, 7 rules, 6 skills)

**Key differentiators**:
- Python-enabled analyst agent for reading Excel files, performing calculations,
  and generating output files (unlike Knowledge Work which denies Python)
- Data file processing with structure detection and inventory cataloging
- Financial and analytical output format templates (financial statements,
  analytical reports, executive summaries)
- `/process-data` skill for data onboarding (catalogs file structure, types, row counts)
- "Never modify originals" data safety rule with dated output files
- Conservative action default (ask before overwriting data, confirm expensive computations)

**Best for**: Professionals who work primarily with spreadsheets, CSV files, and
structured data -- financial modeling, variance analysis, data cleaning, reporting --
but do not write software as their primary work.

---

### 4. DevOps & Infrastructure (`devops-infrastructure.md`)

**Target audience**: DevOps engineers, SRE teams, platform engineers, and cloud
infrastructure teams working with IaC (Terraform, Pulumi, CloudFormation), CI/CD
pipelines, Kubernetes, Docker, monitoring/alerting, and cloud platforms.

**Complexity**: Extended (5 agents, 8 rules, 6 skills)

**Key differentiators**:
- Infrastructure safety gates (plan before apply, dry-run before deploy)
- Blast radius analysis for every infrastructure mutation
- Incident responder agent for triage, diagnosis, and remediation
- PreToolUse hooks blocking destructive infrastructure commands (terraform destroy, kubectl delete)
- Multi-cloud ecosystem permissions (AWS, GCP, Azure CLIs with read-safe defaults)
- Runbook library and post-incident review workflow
- Proactive for read-only operations; gated for infrastructure mutations

**Best for**: Teams managing cloud infrastructure, CI/CD pipelines, and container
orchestration who need safe, auditable infrastructure changes with rollback strategies.

---

## How Profiles Are Used

1. The Harness Generator presents these profiles during intake
2. User selects the closest match (or "none of these" for deep interview)
3. User customizes 2-3 aspects (language, VCS, team size, etc.)
4. The environment-architect uses the profile as a starting point
5. The component-generator adapts profile content to the user's specifics

Profiles are NOT copied verbatim. They provide:
- Agent roster with model/turn/tool specifications
- Routing table entries (adapted to user's domain specifics)
- Ecosystem permission patterns (merged with base permissions)
- Self-learning seed entries (pre-populated friction patterns)
- Hook and MCP suggestions (offered during customization)

---

## Adding New Profiles or Bundled Domains

Follow the slim format spec: `PROFILE_FORMAT.md`. In short, a profile is a
*starting point the architect adapts* -- it lists component **names + template
pointers** (never inlined agent YAML, rule bodies, or full permission JSON;
those live in `Docs/Templates/` and `Docs/Templates/References/ecosystem-permissions.md`),
plus the domain-specific parts that are NOT derivable from a template: the
routing table (10-16 rows), self-learning seeds (4-6), customization points, and
the team-architecture pattern. Target ~150-220 lines. Bundled domains go under
`Docs/DomainLibrary/` and are listed in its `INDEX.md`. See `CONTRIBUTING.md` for
the contribution workflow.
