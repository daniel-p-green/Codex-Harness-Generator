# Process-Inbox Skill (Template)

<!-- ANNOTATION: The process-inbox skill handles batch processing of files
     dropped into the Inbox/ directory. It converts non-plain-text files
     via MarkItDown, summarizes contents, and processes per user instructions.
     Used by both data-analysis and knowledge-work profiles. This is the
     primary "file ingestion" skill for non-developer environments. -->

<!-- QUALITY: Must show progressive disclosure structure (SKILL.md + scripts/).
     Must include proper description with trigger phrases. Must demonstrate
     the scan -> convert -> summarize -> process -> output pipeline. Must
     handle brand checking. SKILL.md under 500 lines. -->

## Progressive Disclosure Structure

```
process-inbox/
  SKILL.md                    # Core instructions (< 500 lines)
  scripts/
    convert-file.sh           # MarkItDown wrapper script (optional)
  references/
    supported-formats.md      # Supported conversion formats (optional)
```

<!-- ANNOTATION: The scripts/ directory wraps MarkItDown invocation with
     error handling and format detection. This avoids regenerating the
     conversion logic each time. Falls back to inline commands if missing. -->

## Example: Process-Inbox Skill (`.agents/skills/process-inbox/SKILL.md`)

````markdown
---
name: process-inbox
description: >
  Process files from the Inbox/ directory. Use when the user says "process
  inbox", "check inbox", "process the files in inbox", "what's in my inbox",
  "handle these files", "read the inbox", or drops files and asks for
  processing. Converts non-plain-text files to Markdown, summarizes contents,
  and processes per user instructions. Output goes to Outbox/. Do NOT use for
  data-specific analysis (route to /process-data or analyst agent) or for
  single-file quick reads (use Read tool directly).
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
     - context: fork (isolated context -- inbox files can be numerous/large)
     - scoped workspace writes allowed for producing output files
     - Bash allowed for MarkItDown conversion and file operations
     - description: 6 trigger phrases and 2 negative triggers
     VARIATION: For data-analysis profile, this skill may chain to
     /process-data for discovered data files. For knowledge-work profile,
     this is the primary file ingestion path. -->

## Critical: Source File Safety

<!-- ANNOTATION: Restating safety rules from 06-data-handling.md because
     skills run in forked context. Inbox/ files are never modified. -->

Do NOT modify, move, or delete files in `Inbox/`. All output goes to `Outbox/`
or user-specified locations. Source files in Inbox/ remain untouched.

## Processing Pipeline

<!-- ANNOTATION: The pipeline follows scan -> convert -> summarize -> ask -> process -> output.
     The "ask" step is important: after summarizing, the user chooses what to do.
     This avoids wasted processing on files the user does not care about. -->

### Step 1: Scan Inbox

List all files in `Inbox/`:

```bash
ls -la Inbox/ 2>/dev/null || echo "Inbox/ directory not found"
```

For each file, record: filename, size, type (by extension), last modified.

If Inbox/ is empty or does not exist, report and stop.

### Step 2: Convert to Markdown

For each non-plain-text file, convert using MarkItDown:

```bash
# Using markitdown CLI (pip install markitdown[all])
markitdown "Inbox/filename.xlsx" > "Data/converted/filename.md"

# Or using markitdown MCP server if available (preferred)
```

| File type | Conversion method | Notes |
|---|---|---|
| .xlsx, .xls | MarkItDown | Preserves table structure as Markdown tables |
| .pdf | MarkItDown | Extracts text; quality varies by PDF type |
| .docx | MarkItDown | Preserves headings, lists, tables |
| .pptx | MarkItDown | Extracts slide content and speaker notes |
| .csv, .tsv | Read directly | No conversion needed; read first 50 rows |
| .json | Read directly | No conversion needed; parse and summarize |
| .md, .txt | Read directly | No conversion needed |
| .html | MarkItDown | Strips tags, preserves content structure |
| .jpg, .png | MarkItDown | OCR/description if supported |

Store converted files in `Data/converted/` (intermediate, cleaned up later).

<!-- ANNOTATION: The conversion step is the most error-prone. Some PDFs
     are scanned images (MarkItDown may produce poor results). Some Excel
     files have complex formatting that does not convert cleanly. The skill
     should report conversion quality and let the user decide. -->

If MarkItDown is not available:
- Check if markitdown MCP server is configured
- Try `pip install markitdown[all]` (if Python is allowed)
- Fall back to reading raw text content where possible
- Report files that could not be converted

### Step 3: Summarize contents

For each file (original plain text or converted Markdown), produce a summary:

```markdown
### <filename>
- **Type**: <file format>
- **Size**: <file size>
- **Content summary**: <2-3 sentence description of what the file contains>
- **Key sections/topics**: <bullet list of main sections or topics>
- **Actionable items**: <any tasks, requests, or action items found>
- **Conversion quality**: Good / Partial / Poor (for converted files)
```

Present all summaries to the user and ask: "What would you like done with
these files?"

### Step 4: Process per instructions

After the user specifies what they want, process each file accordingly.
Common processing requests:

| User intent | Action |
|---|---|
| "Summarize" | Produce detailed summaries in Outbox/ |
| "Extract data" | Pull structured data into CSV/table format |
| "Combine" | Merge multiple files into a single document |
| "Analyze" | Route to analyst agent or /process-data skill |
| "Draft a response" | Route to drafter agent with file contents as input |
| "Review" | Route to reviewer agent |
| "Just organize" | Move converted versions to Outbox/ with inventory |

### Step 5: Brand check (conditional)

<!-- ANNOTATION: Brand checking is conditional on the Brand/ directory
     existing. This supports knowledge-work and data-analysis profiles
     that produce branded output. If no Brand/ directory, skip entirely. -->

If `Brand/` directory exists AND the output will be user-facing (report,
memo, presentation):

1. Check if `Brand/brand-rules.md` exists
2. If it exists, check the "Last Updated" date
3. If stale (brand assets modified after last update), recommend running
   brand rules refresh before producing branded output
4. Apply brand rules to any formatted output (tone, terminology, formatting)

If `Brand/` does not exist, skip this step entirely.

### Step 6: Output to Outbox

Write processed results to `Outbox/` with dated filenames:

```
Outbox/YYYY-MM-DD_<descriptive-name>.<ext>
```

For multi-file processing, also write an index:

```markdown
# Inbox Processing Summary - YYYY-MM-DD

## Files Processed
| # | Source file | Action taken | Output file |
|---|---|---|---|
| 1 | Inbox/report.pdf | Summarized | Outbox/2026-02-15_report_summary.md |
| 2 | Inbox/data.xlsx | Extracted to CSV | Outbox/2026-02-15_data_extract.csv |

## Notes
- <any issues encountered>
- <files that could not be processed>
```

## Cleanup

<!-- ANNOTATION: Intermediate converted files in Data/converted/ should be
     cleaned up after processing. But ask the user first in case they want
     to keep them for reference. -->

After processing is complete:
- Offer to clean up intermediate files in `Data/converted/`
- Do NOT move or delete files from `Inbox/` (user manages their own inbox)
- Update `Docs/Areas/data-inventory.md` if data files were discovered

## Output Format

```markdown
## Inbox Processing Complete

**Files found**: <count>
**Files processed**: <count>
**Files skipped**: <count> (with reasons)

### Results
<per-file summary of what was done>

### Output Files
<list of files written to Outbox/>

### Issues
<any conversion problems, unreadable files, or sensitive data detected>

### Artifacts
- Outbox/<dated files> (processed output)
- Data/converted/ (intermediate files, recommend cleanup)
- Docs/Areas/data-inventory.md (updated if applicable)
```
````

## Example Script: `scripts/convert-file.sh`

<!-- ANNOTATION: This script wraps MarkItDown with error handling and
     output directory management. The skill uses it for batch conversion.
     Falls back to inline commands if the script is missing. -->

```bash
#!/bin/bash
# Convert a single file from Inbox/ to Markdown using MarkItDown
# Usage: convert-file.sh <input-path> <output-dir>

INPUT="$1"
OUTDIR="${2:-Data/converted}"
FILENAME=$(basename "$INPUT")
BASENAME="${FILENAME%.*}"

mkdir -p "$OUTDIR"

echo "Converting: $INPUT"

if command -v markitdown &>/dev/null; then
    markitdown "$INPUT" > "$OUTDIR/${BASENAME}.md" 2>/dev/null
    EXIT_CODE=$?
elif command -v python3 &>/dev/null; then
    python3 -c "from markitdown import MarkItDown; m=MarkItDown(); print(m.convert('$INPUT').text_content)" > "$OUTDIR/${BASENAME}.md" 2>/dev/null
    EXIT_CODE=$?
else
    echo "ERROR: markitdown not available. Install with: pip install markitdown[all]"
    exit 1
fi

if [ $EXIT_CODE -eq 0 ] && [ -s "$OUTDIR/${BASENAME}.md" ]; then
    echo "SUCCESS: $OUTDIR/${BASENAME}.md"
else
    echo "FAILED: Could not convert $INPUT (exit code: $EXIT_CODE)"
    exit 1
fi
```

<!-- QUALITY: Validation checklist for the generator:
     - [ ] SKILL.md under 500 lines
     - [ ] Description includes 3+ trigger phrases
     - [ ] Description includes negative triggers
     - [ ] context: fork specified
     - [ ] Source file safety rule restated (never modify Inbox/)
     - [ ] Pipeline: scan -> convert -> summarize -> ask -> process -> output
     - [ ] File type conversion table with supported formats
     - [ ] MarkItDown usage documented with fallback
     - [ ] Brand check step (conditional on Brand/ existence)
     - [ ] Output to Outbox/ with dated filenames
     - [ ] Multi-file index produced for batch processing
     - [ ] Cleanup conventions for intermediate files
     - [ ] Output format includes issues and artifacts
     - [ ] scripts/ directory used for conversion wrapper
     - [ ] No README.md inside the skill folder
-->

<!-- ANTI-PATTERN: Do not process files without first showing the user
     what was found. The "ask" step after summarizing prevents wasted work
     on files the user does not care about or did not intend to process. -->

<!-- ANTI-PATTERN: Do not delete or move files from Inbox/ after processing.
     The user manages their own inbox. Processed files are COPIED to Outbox/,
     not moved. -->

<!-- ANTI-PATTERN: Do not fail silently when MarkItDown cannot convert a
     file. Report the failure, note which files were skipped, and continue
     processing the remaining files. Partial results are better than no results. -->
