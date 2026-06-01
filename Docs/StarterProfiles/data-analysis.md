# Starter Profile: Data & Analysis

Follows `Docs/StarterProfiles/PROFILE_FORMAT.md` (slim). A starting point the
architect adapts -- it points at templates, it does not inline them.

## Profile Metadata

- **Target audience**: accountants, financial/business analysts, data scientists,
  BI analysts, healthcare-metrics and real-estate analysts, researchers working
  with datasets, actuarial and compliance-reporting work
- **Primary tools**: Python (pandas, openpyxl, numpy), MarkItDown; optional R, SQL
- **Complexity**: Standard | **Memory tier**: Standard | **Action default**: conservative (ask before overwriting data files or running expensive computations) | **VCS**: None by default

## Component Roster

Agents (definitions: `Docs/Templates/Agents/<name>.md`; adapt, do not copy verbatim):

| name | model | role | template |
|---|---|---|---|
| researcher | opus | Look up standards/regulations/methodology (GAAP, IRS, FASB, stats) before analysis; cite sources | researcher.md |
| analyst | sonnet | Read/transform/compute over data files via Python; produce dated output files | analyst.md |
| drafter | sonnet | Write reports, memos, executive summaries from analysis results | drafter.md |
| reviewer | opus | Verify calculations, validate methodology, audit reports (read-only) | reviewer.md |

Rules (templates in `Docs/Templates/Core|Optional/`): orchestrator/routing,
autonomy (conservative), context-management, self-learning, error-handling (with
diagnostic discipline for malformed data, encoding, type/date ambiguity),
memory-management, and `data-handling-rule.md` (never modify originals; dated
output copies; preserve lineage; track freshness).

Skills (templates in `Docs/Templates/Skills|Core/`): core `/state-save`,
`/state-load`, `/update`, `/health-check`; domain `/process-data` (data inventory
onramp) and `/process-inbox` (Inbox/ -> MarkItDown -> Outbox/). `/state-save` omits
the VCS category; `/health-check` also verifies pandas/openpyxl present and output/
exists. Output-style references (financial / analytical / executive) come from
`Docs/Templates/Optional/output-styles-template.md` into `Docs/Areas/output-styles.md`.

## Domain Routing Table

| # | User Intent | Route | Context / Notes | Fallback |
|---|-------------|-------|-----------------|----------|
| 1 | Analyze this spreadsheet / CSV | analyst (read, summarize structure, key metrics) | Run /process-data first if data inventory empty | answer directly (format Q, not content) |
| 2 | Build a financial forecast / projection | analyst (model) -> drafter (narrative) | Specify assumptions, horizon, growth rates | researcher (if methodology guidance needed) |
| 3 | Compare actuals vs budget / vs last year | analyst (variance analysis) | Specify absolute vs %, flag threshold | drafter (if narrative report also needed) |
| 4 | Calculate financial metric (IRR, NPV, cap rate) | analyst | Include cash flows, discount rate, periods | researcher (if formula/standard unclear) |
| 5 | Clean this data / fix formatting issues | analyst (detect issues, write cleaned output) | Never modify originals; new file | answer directly (if explaining manual cleanup) |
| 6 | Summarize this dataset | analyst (stats, distributions) -> drafter (summary) | Specify dimensions, audience | answer directly (if small and visible) |
| 7 | Create a report on [topic] | analyst (process data) -> drafter (write report) | Specify audience, length, format, questions | researcher (if background research first) |
| 8 | Check these numbers / verify calculations | reviewer | Provide source data + calculations to verify | analyst (if recalculation needed) |
| 9 | Explain this data / what does this mean | answer directly or analyst (if computation needed) | Adapt to user's technical level | researcher (if domain knowledge needed) |
| 10 | Research GAAP rule / tax reg / methodology | researcher | Specify jurisdiction, period, standards | answer directly (well-known fact) |
| 11 | Draft a memo / exec summary from this analysis | drafter | Include audience, length, key points | analyst first (if data not yet processed) |
| 12 | Find trends / patterns in this data | analyst (time series, stats) | Specify period, dimensions, significance | drafter (if narrative trend report needed) |
| 13 | Convert file format / restructure this data | analyst (read source, write new format) | Specify target format and structure | answer directly (if explaining manual conversion) |
| 14 | Reconcile these two data sources | analyst (matching, discrepancy ID) | Specify match keys, tolerance | reviewer (verify reconciliation completeness) |
| 15 | Build a dashboard / tracking spreadsheet | analyst (create structured output file) | Specify metrics, layout, update cadence | drafter (if accompanying docs needed) |
| 16 | What's missing from this analysis | reviewer (completeness check) | Provide analysis and its stated scope | researcher (if gaps need domain knowledge) |
| 17 | Process the file in Inbox/ | analyst via /process-inbox (MarkItDown -> process -> Outbox/) | Converts Excel/PDF/Word to Markdown | answer directly (if already CSV/plain text) |
| 18 | Create a formatted report from this data | analyst -> drafter; Pandoc -> .docx/.pdf if installed | Markdown default; Pandoc for formatted docs | drafter (Markdown-only if no Pandoc) |
| 19 | Update brand rules / re-read brand guide | analyst reads Brand/ via MarkItDown, updates brand-rules.md | Only if Brand/ directory exists | answer directly (if no Brand/) |

Complexity scaling: Simple (direct answer, <3 calls: factual Q, format
explanation, small lookup) | Standard (1-2 agents: single-file analysis,
calculation, report draft) | Complex (2-3 agents serial: multi-source analysis,
forecast models, full report with verification).

## Ecosystem Permissions

Base + Universal Deny + the "Data / Python-analysis" ecosystem (Python ALLOWED
here -- the key difference from Knowledge Work) -- all in
`Docs/Templates/References/ecosystem-permissions.md`. Add output paths the analyst
writes (`Write/Edit(./output/**)`, `./Outbox/**`, `./Data/**`) to avoid prompts.
Treat raw-data dirs as read-mostly. Domain-specific allows not in the reference:

- Data CLIs: `Bash(csvtool *)`, `Bash(jq *)`, `Bash(markitdown *)`, `Bash(pandoc *)`
- Extended (only if intake names the tool): R (`Rscript *`, `R *`), SQL
  (`sqlite3 *`, `psql *`), read-only cloud storage (`aws s3 cp/ls/sync *`;
  deny `aws s3 rm/mv *`)

Generate `settings.local.json` for machine-specific Python install or DB
connection paths.

## Self-Learning Seed Entries

Pre-seed `Docs/_working/retro/YYYY-MM.md` (bootstrapping threshold 1 for 30 days;
categories CALC_ERROR, DATA_FORMAT, METHODOLOGY_GAP, OUTPUT_MISMATCH):

```
- [PATTERN] (pre-seeded) Data format assumptions -- analyst writes Python that
  assumes CSV encoding/delimiter without checking (Latin-1 parsed as UTF-8, or
  semicolon-delimited parsed as comma). Mitigation: always detect encoding
  (chardet) and delimiter (csv.Sniffer) before processing.
- [PATTERN] (pre-seeded) Original data modified -- analyst overwrites a source file
  by writing output to the same path. Mitigation: never modify originals; create
  dated copies in output/. Analyst instructions + data-handling rule enforce this.
- [PATTERN] (pre-seeded) Large file context exhaustion -- analyst Reads an entire
  large CSV into context. Mitigation: read first 50 rows for structure discovery,
  then process with pandas; never load more than 100 rows into context.
- [PATTERN] (pre-seeded) Calculation methodology not documented -- analyst produces
  numbers without explaining derivation, so the user cannot verify/reproduce.
  Mitigation: include methodology notes (formula, assumptions, source) with every
  calculation; write scripts to Docs/_working/sessions/ for reproducibility.
- [PATTERN] (pre-seeded) Excel formula dependencies lost -- openpyxl resolves
  formulas to cached values and the logic is lost; computed cells get treated as
  static. Mitigation: note which cells had formulas (data_only=False pass),
  document the calculation logic separately, flag possibly-stale cached values.
```

## Hook Suggestions

- **PreCompact auto-save** (recommended -- data sessions run long): appends current
  data sources, methodology-in-progress, and output inventory to session state.
- See `Docs/Templates/Optional/hooks-template.md`. Stop-hook self-review is
  optional here (no code-producing default).

## Cost / Model Notes

Opus for researcher/reviewer (standards lookup, calculation verification); Sonnet
for analyst/drafter (established-pattern execution). Defaults: balanced (Opus on
reasoning roles, Sonnet on execution; compaction 95%; CLAUDE.md ~200 lines).
Cost-conscious override: all-Sonnet (Opus only for reviewer verifying against
regulatory standards), consider merging drafter into analyst, compaction 85%,
CLAUDE.md ~150, full RTK in GETTING_STARTED (filters verbose pandas/numpy output
and tracebacks), `.claudeignore` large data files (`*.csv`, `*.parquet`, `*.h5`,
`data/raw/`) and Python artifacts (`__pycache__/`, `*.pyc`, `.ipynb_checkpoints/`).
Analyst Python iteration is the main token sink (~5-15 Bash calls/analysis);
/process-data first run is expensive with many files. Subagents ~4x vs direct;
teams not recommended (serial process->analyze->draft->review is natural). Monitor
with `/cost`.

## MCP Suggestions

Offer during intake only if the user names the service (verified servers per
tool-registry): **MarkItDown** (`markitdown-mcp` -- file conversion without manual
Python calls), **PostgreSQL**, **Google Sheets**, **Notion**, **Snowflake/BigQuery**.
Default path needs no MCP -- pip `markitdown[all]` + openpyxl cover ingestion.

## Customization Points

- Branded output? -> add `Brand/` (Templates/Guidelines/brand-rules.md) + drafter
  brand awareness; many analysts only need Excel/CSV and skip it
- Formatted external reports? -> recommend Pandoc (Markdown -> DOCX/PDF/PPTX)
- Extra languages/stores? -> R, SQL (sqlite3/psql), cloud read-only -> ecosystem allows
- Regulated/compliance data? -> tighten autonomy, optional sensitive-data rule/hooks
- Token priority (cost-conscious / balanced / quality-first) -> drives model tiering,
  compaction, agent count
- Inbox/Outbox workflow volume -> /process-inbox cadence and MCP vs pip choice

## Team-architecture pattern

Pipeline (process data -> analyze -> draft -> review) with a Producer-Reviewer pair
(analyst/drafter produce, reviewer verifies). Subagents are the default and the
right tool -- the workflow is inherently serial, so Agent Teams are not recommended
for typical data work.
