# Template: Data Handling Rule (06-data-handling.md)

<!-- TEMPLATE ANNOTATION
  This template defines data safety conventions for environments that process
  user data files (CSV, Excel, JSON, etc.). It is used by the data-analysis
  profile and any Pattern A environment where users work with structured data.

  QUALITY CRITERIA:
  - Under 120 lines in generated output
  - Never-modify-originals rule stated explicitly
  - Dated copy convention with naming format
  - Data lineage tracking (source -> transformation -> output)
  - Sensitive field handling (PII/PHI awareness)
  - Validation-before-processing steps
  - Cleanup conventions for intermediate files
  - Output directory structure

  WHY THIS EXISTS:
  Data loss from overwriting originals is irreversible. Data processing without
  lineage tracking produces unreproducible results. Sensitive data handled
  carelessly creates legal and ethical risk. This rule prevents all three.
-->

<!-- ============================================================
  REFERENCE IMPLEMENTATION
  Domain: Financial analysis / data science
============================================================ -->

# Data handling

<!-- CORE PRINCIPLE
  WHY: The single most important data safety rule. Every other convention
  flows from this. If agents never modify originals, data loss is impossible.
-->
Original data files are immutable. Never modify, overwrite, or delete source data.

## Source data protection

<!-- SOURCE PROTECTION
  WHY: Making this an absolute rule removes ambiguity. Agents do not need to
  judge whether a modification is safe -- it is never safe on originals.
-->
- NEVER write to, edit, or overwrite any file in `Inbox/` or user-specified source locations
- NEVER use the same filename as a source file for output
- If a source file is read-only, do NOT attempt to change permissions
- If a processing error corrupts output, the source is always available to reprocess

## Dated copies for audit trails

<!-- DATED COPIES
  WHY: Undated output files get overwritten on re-runs. Dated filenames
  create a natural audit trail and prevent accidental overwrites.
-->
All output files use dated naming:

```
output/YYYY-MM-DD_<descriptive-name>.<ext>
```

Examples:
- `output/2026-02-15_variance_analysis.csv`
- `output/2026-02-15_cleaned_transactions.xlsx`
- `output/2026-02-15_quarterly_report.md`

When re-running an analysis on the same day, append a sequence number:
- `output/2026-02-15_variance_analysis_v2.csv`

Never overwrite existing dated output files. Create a new version instead.

## Data lineage tracking

<!-- DATA LINEAGE
  WHY: Without lineage, nobody can verify how results were derived. "Where
  did this number come from?" must always be answerable.
-->
Every output file must be traceable to its source. Track lineage by including
a header comment or companion metadata file:

For CSV/text outputs, include a header block:
```
# Source: Inbox/Q4_transactions.csv
# Generated: 2026-02-15
# Transformations: filtered by date >= 2026-01-01, aggregated by category
# Row count: 142 (source: 1,847 rows)
# Script: Docs/_working/sessions/2026-02-15_analysis/transform.py
```

For reports and documents, include a "Data Sources" section listing:
- Source file path and name
- Date range of data used
- Transformations applied (filters, aggregations, calculations)
- Row/record counts (before and after processing)
- Any exclusions and why

## Validation before processing

<!-- VALIDATION
  WHY: Processing garbage data produces garbage results. Validation catches
  problems before they propagate through an analysis pipeline.
-->
Before processing any data file, validate:

| Check | What to look for | Action on failure |
|---|---|---|
| File readability | Can the file be opened and parsed? | Report error, stop processing |
| Encoding detection | UTF-8, Latin-1, Windows-1252? | Detect with chardet, convert if needed |
| Delimiter detection | Comma, semicolon, tab, pipe? | Detect with csv.Sniffer or inspection |
| Schema consistency | Expected columns present? Types correct? | Report missing/extra columns, stop |
| Null/empty values | Missing data in critical fields? | Report count and percentage, warn user |
| Outlier detection | Values outside expected ranges? | Flag but do not remove without user approval |
| Duplicate detection | Duplicate rows or keys? | Report count, ask user how to handle |
| Date format | MM/DD vs DD/MM ambiguity? | Ask user to confirm if ambiguous |

Report validation results before proceeding. Do not silently skip bad records.

## Sensitive field handling

<!-- SENSITIVE DATA
  WHY: Data files may contain PII, PHI, or other sensitive information.
  Even in a local environment, sensitive data should not leak into logs,
  memory files, or context summaries.
-->
Watch for fields that may contain sensitive data:

- Names, email addresses, phone numbers, SSNs, account numbers
- Medical records, diagnoses, prescription information
- Salary, compensation, financial account details
- Addresses, dates of birth, government IDs

When sensitive fields are detected:
- Warn the user: "This file appears to contain [type] data in columns [X, Y]"
- Do NOT include sample values from sensitive columns in summaries or reports
- Use aggregate statistics instead of individual records in output
- If the user requests operations on sensitive fields, proceed but note it
  in the session log
- See `07-sensitive-data.md` for classification and handling rules (if present)

## Intermediate file conventions

<!-- INTERMEDIATE FILES
  WHY: Data processing often creates intermediate files (cleaned data,
  joined datasets, pivot tables). Without conventions these pile up.
-->
Intermediate processing files go in `Data/` (not `output/`):

```
Data/YYYY-MM-DD_<step-description>.<ext>
```

- Intermediate files are working artifacts, not final deliverables
- Clean up intermediate files when the analysis is complete
- If an intermediate file might be reused, promote it to `output/` with
  proper lineage documentation
- `/health-check` flags intermediate files older than 7 days

## Output directory structure

<!-- OUTPUT STRUCTURE
  WHY: Consistent output organization makes results findable.
-->
```
output/              # Final deliverables (dated, never overwritten)
Data/                # Intermediate/working files (cleaned up after use)
Inbox/               # Source data (never modified)
Outbox/              # Processed results for handoff (reports, exports)
```

## Row count reconciliation

<!-- ROW COUNTS
  WHY: A common data processing bug is silently dropping rows. Tracking
  counts at each step catches this immediately.
-->
At every transformation step, report:
- Input row count
- Output row count
- Rows added, removed, or modified (and why)
- Running reconciliation: "Started with 1,847 rows, ended with 142 rows
  (1,705 filtered by date criteria)"

If the output row count is unexpected, warn before proceeding.

<!-- ============================================================
  REFERENCE IMPLEMENTATION ENDS
============================================================ -->

<!-- VARIATION NOTES

  DATA ANALYSIS (this example):
  - Heavy emphasis on lineage and row count tracking
  - Python-based validation (pandas, chardet, csv.Sniffer)
  - Intermediate files in Data/ directory

  KNOWLEDGE WORK:
  - Less structured data, more document-centric
  - Lineage tracking focuses on source documents rather than row counts
  - Sensitive data: client names, case details, privileged information
  - Output: Outbox/ for handoff documents

  GAME DEVELOPMENT:
  - Data tables (CSV/JSON) for game balance and configuration
  - Version control (Perforce) handles audit trail
  - Validation: schema checks against expected game data structures
  - No sensitive data typically, but check for API keys in config files

  CONSERVATIVE DOMAINS (legal, healthcare, finance):
  - Stricter sensitive data handling (see sensitive-data-rule.md)
  - Longer retention for audit trails (regulatory requirements)
  - Validation includes compliance checks against regulatory schemas
  - Never auto-delete intermediate files without user confirmation
-->

<!-- ANTI-PATTERNS

  1. MODIFYING ORIGINAL FILES
     Problem: Source data overwritten, analysis cannot be reproduced.
     Fix: "Original data files are immutable." Absolute rule, no exceptions.

  2. UNDATED OUTPUT FILES
     Problem: Re-running analysis overwrites previous results.
     Fix: Dated naming convention with version numbers for same-day re-runs.

  3. NO DATA LINEAGE
     Problem: "Where did this number come from?" is unanswerable.
     Fix: Every output traces back to source files and transformations.

  4. SILENT ROW DROPPING
     Problem: Processing silently filters/drops rows, results are wrong.
     Fix: Row count reconciliation at every transformation step.

  5. SENSITIVE DATA IN SUMMARIES
     Problem: PII from data files appears in session notes or reports.
     Fix: Detect sensitive fields and use aggregates, not individual values.

  6. INTERMEDIATE FILES ACCUMULATE
     Problem: Data/ directory fills with orphaned temp files.
     Fix: Cleanup conventions and /health-check flagging.
-->

<!-- QUALITY CRITERIA FOR VALIDATION

  [ ] Under 120 lines in generated output
  [ ] Never-modify-originals rule stated as absolute
  [ ] Dated copy naming convention with format example
  [ ] Data lineage tracking with header block example
  [ ] Validation-before-processing table (6+ checks)
  [ ] Sensitive field handling with detection patterns
  [ ] Intermediate file conventions with cleanup rules
  [ ] Output directory structure specified
  [ ] Row count reconciliation requirement
  [ ] References to related rules (sensitive-data, health-check)
  [ ] ASCII-only
-->
