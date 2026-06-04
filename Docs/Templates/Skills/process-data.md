# Process-Data Skill (Template)

<!-- ANNOTATION: The process-data skill is the data onboarding "on-ramp."
     It discovers, validates, and summarizes data files so the user and
     agents have a shared understanding of what data is available.
     Used by the data-analysis profile. Produces a data inventory as
     its primary artifact. -->

<!-- QUALITY: Must show progressive disclosure structure (SKILL.md + scripts/).
     Must include proper description with trigger phrases. Must demonstrate
     the discover -> validate -> summarize pipeline. Must show safety-first
     data handling. SKILL.md under 500 lines. -->

## Progressive Disclosure Structure

```
process-data/
  SKILL.md                    # Core instructions (< 500 lines)
  scripts/
    detect-schema.py          # Schema detection script (optional)
  references/
    supported-formats.md      # Supported file formats and detection (optional)
```

<!-- ANNOTATION: The scripts/ directory is optional for this skill because
     the detection logic may be inline Python. However, a reusable schema
     detection script saves tokens on repeated invocations. -->

## Example: Process-Data Skill (`.agents/skills/process-data/SKILL.md`)

````markdown
---
name: process-data
description: >
  Discover, validate, and summarize data files for analysis. Use when the user
  says "process this data", "analyze this file", "load this dataset", "what's
  in this file", "onboard this data", "read this spreadsheet", or drops files
  into Inbox/. Also use at the start of any data project to inventory available
  data. Do NOT use for performing actual analysis (route to analyst agent) or
  for generating reports (route to drafter agent).
context: fork
tool access policy:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
metadata:
  version: 1.0.0
---

<!-- ANNOTATION: Frontmatter design decisions:
     - context: fork (isolated context -- data files can be large)
     - scoped workspace writes allowed because this skill produces the data inventory
     - Bash allowed for Python-based file detection and schema analysis
     - description: 6 trigger phrases and 2 negative triggers
     VARIATION: For knowledge-work profile, this skill might not exist
     (replaced by /process-inbox which handles document files). -->

## Critical: Never Modify Source Files

<!-- ANNOTATION: This is the most important constraint, repeated from
     06-data-handling.md. Skills should restate critical safety rules
     because they run in forked context without the full rule set. -->

Do NOT modify, overwrite, or delete any source data files. All output goes
to `Docs/Areas/data-inventory.md` or `output/`.

## Processing Pipeline

<!-- ANNOTATION: The pipeline follows discover -> validate -> summarize.
     Each step produces progressively more detail. The user gets a
     quick summary they can act on immediately. -->

### Step 1: Discover files

Scan the target location for data files:

```bash
# Find data files in the specified directory (default: current directory + Inbox/)
find . -maxdepth 3 -type f \( \
  -name "*.csv" -o -name "*.xlsx" -o -name "*.xls" \
  -o -name "*.json" -o -name "*.tsv" -o -name "*.parquet" \
  -o -name "*.xml" -o -name "*.txt" \) \
  -not -path "./output/*" -not -path "./Docs/*" -not -path "./.codex/*" \
  | sort
```

For each file found, record: path, size, last modified date.

<!-- VARIATION: For projects with specific data directories, replace the
     find command with a targeted scan of known locations. -->

### Step 2: Detect file type and structure

For each discovered file:

| File type | Detection method | Structure to extract |
|---|---|---|
| CSV/TSV | Read first 5 lines, detect delimiter and encoding | Column names, row count, sample values |
| Excel (.xlsx) | Use openpyxl or pandas to list sheets | Sheet names, column names per sheet, row counts |
| JSON | Read and parse structure | Top-level keys, array lengths, nested structure |
| Parquet | Use pandas to read metadata | Column names, types, row count |
| Other text | Read first 20 lines | General structure description |

<!-- ANNOTATION: Reading first-N-lines avoids loading large files into context.
     Python (pandas) is used for formats that cannot be read as plain text.
     This is where the Bash tool earns its keep. -->

For CSV/TSV files, always detect encoding first:

```python
import chardet
with open(filepath, 'rb') as f:
    result = chardet.detect(f.read(10000))
encoding = result['encoding']
```

### Step 3: Validate structure

For each file, run basic validation:

- Can the file be opened and parsed without errors?
- Are column names present and reasonable (not Row1, Row2...)?
- Are data types consistent within columns?
- What percentage of values are null/empty per column?
- Are there obvious date format ambiguities (01/02/2026)?
- Are there potential sensitive fields? (See 07-sensitive-data.md if present)

Report any issues found. Do NOT attempt to fix them -- report for user decision.

### Step 4: Produce summary

For each file, produce a structured summary:

```markdown
### <filename>
- **Path**: <full path>
- **Format**: CSV / Excel / JSON
- **Size**: <file size>
- **Last modified**: <date>
- **Encoding**: <detected encoding>
- **Rows**: <count> (excluding header)
- **Columns**: <count>
- **Column details**:
  | Column | Type | Non-null | Sample values |
  |---|---|---|---|
  | revenue | float | 98% | 1234.56, 7890.12, ... |
  | date | date | 100% | 2026-01-15, 2026-02-01, ... |
- **Data quality issues**: <list any issues found>
- **Sensitive fields**: <list if detected, or "None detected">
```

### Step 5: Write data inventory

Write the complete inventory to `Docs/Areas/data-inventory.md`.
Update `Docs/index.md` to include the inventory entry if not present.

If a data inventory already exists, update it rather than overwriting.
Note which entries are new and which were updated.

## Output Format

```markdown
## Data Processing Summary

**Files discovered**: <count>
**Files processed**: <count>
**Issues found**: <count>

### File Inventory
<per-file summaries from Step 4>

### Data Quality Summary
- Files with encoding issues: <list>
- Files with missing values: <list with percentages>
- Files with date ambiguity: <list>
- Files with potential sensitive data: <list>

### Recommended Next Steps
- <what analysis the user might want to run>
- <any data cleaning needed before analysis>
- <any files that could not be processed and why>

### Artifacts Written
- Docs/Areas/data-inventory.md (created/updated)
- Docs/index.md (updated if needed)
```
````

## Example Script: `scripts/detect-schema.py`

<!-- ANNOTATION: This script handles the heavy lifting of schema detection.
     Running it as a script avoids regenerating the detection logic each
     time. The skill falls back to inline Python if the script is missing. -->

```python
#!/usr/bin/env python3
"""Detect schema and basic statistics for a data file."""
import sys
import json
import pandas as pd
import chardet

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(10000))
    return result['encoding'] or 'utf-8'

def analyze_file(filepath):
    ext = filepath.rsplit('.', 1)[-1].lower()
    result = {'path': filepath, 'format': ext}

    if ext in ('csv', 'tsv'):
        enc = detect_encoding(filepath)
        sep = '\t' if ext == 'tsv' else ','
        df = pd.read_csv(filepath, encoding=enc, sep=sep, nrows=100)
        result['encoding'] = enc
    elif ext in ('xlsx', 'xls'):
        df = pd.read_excel(filepath, nrows=100)
    elif ext == 'json':
        df = pd.read_json(filepath, lines=True, nrows=100)
    else:
        result['error'] = f'Unsupported format: {ext}'
        return result

    result['rows'] = len(df)
    result['columns'] = list(df.columns)
    result['dtypes'] = {col: str(dt) for col, dt in df.dtypes.items()}
    result['null_pct'] = {col: round(df[col].isnull().mean() * 100, 1)
                          for col in df.columns}
    return result

if __name__ == '__main__':
    print(json.dumps(analyze_file(sys.argv[1]), indent=2))
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 3+ trigger phrases
     - [ ] Description includes negative triggers
     - [ ] context: fork specified
     - [ ] Never-modify-originals safety rule restated
     - [ ] Pipeline: discover -> validate -> summarize
     - [ ] File type detection table with supported formats
     - [ ] Encoding detection step for text files
     - [ ] Validation checks enumerated (5+ checks)
     - [ ] Structured per-file summary format
     - [ ] Data inventory written to Docs/Areas/
     - [ ] INDEX.md updated
     - [ ] Output format includes recommended next steps
     - [ ] scripts/ directory used for schema detection
     - [ ] No README.md inside the skill folder
-->

<!-- ANTI-PATTERN: Do not load entire data files into context via the Read
     tool. Use Python (pandas) to read structure and statistics, then report
     the summary. A 50,000-row CSV in context will exhaust it immediately. -->

<!-- ANTI-PATTERN: Do not skip the validation step. Processing unvalidated
     data produces wrong results and the user loses trust. Always validate
     and report issues before offering to analyze. -->

<!-- ANTI-PATTERN: Do not produce the data inventory only as chat output.
     Write it to disk (Docs/Areas/data-inventory.md) so it persists
     across sessions. The chat output is a summary pointing to the artifact. -->
