# File Processing Tool Catalog

**Purpose:** Reference for component-generator when building file processing capabilities. Contains the definitive information about each tool -- what it does, how to install it, when to use it, and how to configure it in a Codex environment.

**Last Updated:** 2026-02-16

---

## Decision Matrix

Map user needs to tool selections. Read left-to-right: identify the need, then select the tools.

| User Need | Inbound Tool | Outbound Tool | Install Method | MCP Option |
|---|---|---|---|---|
| Read any file format | MarkItDown | -- | `pip install 'markitdown[all]'` | markitdown-mcp |
| Produce formatted .docx for clients | MarkItDown | Pandoc | `winget install pandoc` | pandoc-md2pptx MCP |
| Produce presentations (.pptx) | MarkItDown | Pandoc | `winget install pandoc` | pandoc-md2pptx MCP |
| Produce PDF reports | MarkItDown | Pandoc (+engine) | `winget install pandoc` | -- |
| Produce basic internal .docx | MarkItDown | python-docx | `pip install python-docx` | -- |
| Read/write Excel files | MarkItDown | openpyxl | `pip install openpyxl` | -- |
| Read/write Excel (Windows/PS) | MarkItDown | ImportExcel | `Install-Module ImportExcel -Scope CurrentUser` | -- |
| Heavy PDF table extraction | MarkItDown | pdfplumber | `pip install pdfplumber` | -- |
| Media processing | MarkItDown | ffmpeg | exe download | -- |

---

## Tool Details

### 1. MarkItDown (Microsoft)

- **Role:** Universal INBOUND converter (everything -> Markdown)
- **Install:** `pip install 'markitdown[all]'` (no exe, no admin)
- **Selective install:** `pip install 'markitdown[pdf,docx,xlsx]'` -- pick only needed extras
- **Extras available:** audio-transcription, az-doc-intel, docx, outlook, pdf, pptx, xls, xlsx, youtube-transcription
- **Supported formats:** PDF, DOCX, XLSX, PPTX, images (EXIF+OCR), audio (transcription), HTML, CSV, JSON, XML, ZIP

**MCP Server setup:**

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "uvx",
      "args": ["markitdown-mcp"]
    }
  }
}
```

This gives Codex a native `convert_to_markdown` tool -- the most seamless integration path.

**CLI usage:**

```bash
markitdown path/to/file.xlsx > output.md
```

**Python usage:**

```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("file.xlsx")
print(result.text_content)
```

- **When to use:** ALWAYS for file-processing environments. This is the universal inbound converter.
- **When NOT to use:** Never skip this for environments that process non-text files.
- **Note:** Codex's native Read tool already handles PDFs (up to 20 pages) and images. MarkItDown adds Excel, Word, PowerPoint, audio, and richer PDF extraction.

---

### 2. Pandoc

- **Role:** Universal OUTBOUND converter (Markdown -> formatted .docx/.pptx/.pdf)
- **Install:** `winget install pandoc` or `choco install pandoc` (exe install required)

**Key capabilities:**

```bash
# Markdown to Word with custom template
pandoc report.md -o report.docx --reference-doc=template.docx

# Markdown to PowerPoint with custom template
pandoc slides.md -t pptx -o deck.pptx --reference-doc=template.pptx

# Markdown to PDF (needs LaTeX engine for PDF)
pandoc paper.md -o paper.pdf
```

**PPTX workflow:** Codex writes Markdown with `---` slide breaks, Pandoc produces formatted slides. Approximately 20 lines of Markdown for a 10-slide deck.

**Template support:** Custom .docx/.pptx templates for branding and consistent formatting. Place templates in the environment's `Templates/` directory and reference them with `--reference-doc`.

- **When to use:** When user produces formatted documents for external audiences (clients, boards, regulators, publishers), presentations, or PDF reports.
- **When NOT to use:** When user only needs text summaries, basic internal docs, or Excel output.
- **Install justification:** No pip-only tool matches Pandoc's output quality for .pptx and .pdf. python-pptx requires 100+ lines of Python per deck; Pandoc needs approximately 20 lines of Markdown.

---

### 3. python-docx

- **Role:** Basic .docx creation/modification (pip only, no exe install)
- **Install:** `pip install python-docx`
- **Capabilities:** Headings, paragraphs, tables, images, basic styles

```python
from docx import Document
doc = Document()
doc.add_heading("Report Title", 0)
doc.add_paragraph("Content here.")
doc.save("output.docx")
```

- **When to use:** When user needs basic internal .docx output and Pandoc is not installed.
- **When NOT to use:** When professional formatting matters -- use Pandoc instead.
- **Limitation:** Requires Codex to build document structure programmatically. More code, less natural than Pandoc's Markdown-to-docx pipeline.

---

### 4. python-pptx

- **Role:** Programmatic .pptx modification (NOT for presentation generation from content)
- **Install:** `pip install python-pptx`

```python
from pptx import Presentation
prs = Presentation("template.pptx")
slide = prs.slides[0]
slide.shapes.title.text = "Updated Title"
prs.save("output.pptx")
```

- **When to use:** ONLY for modifying existing presentations, filling templates with data, or generating charts at specific slide positions.
- **When NOT to use:** For creating presentations from content. Pandoc is dramatically better for this use case.
- **Warning:** Requires 100+ lines of Python per 10-slide deck. Not a Pandoc replacement for presentation generation.

---

### 5. openpyxl

- **Role:** Excel (.xlsx) read/write with full formatting
- **Install:** `pip install openpyxl`
- **Capabilities:** Read/write cells, formulas, charts, styles, conditional formatting, pivot tables

```python
from openpyxl import load_workbook
wb = load_workbook("data.xlsx")
ws = wb.active
ws["A1"] = "Updated Value"
wb.save("data.xlsx")
```

- **When to use:** When user needs Excel round-trip (read -> process -> write back) or format-preserving modifications.
- **When NOT to use:** For read-only quick analysis of Excel files (MarkItDown is faster and simpler for that).
- **Pairs with:** MarkItDown (for quick reading) or direct openpyxl (for format-preserving reads).

---

### 6. ImportExcel (PowerShell)

- **Role:** Excel read/write for Windows environments
- **Install:** `Install-Module ImportExcel -Scope CurrentUser` (no admin, no exe)

```powershell
# Read
$data = Import-Excel .\data.xlsx
# Write
$data | Export-Excel .\output.xlsx -AutoSize -TableName "Results"
```

- **When to use:** Windows-centric environments that don't use Python, or as complement to openpyxl.
- **When NOT to use:** Cross-platform environments where Python is the primary toolchain.
- **Advantage:** PowerShell is already on every Windows machine. No Python dependency.

---

### 7. pdfplumber

- **Role:** Specialized PDF table extraction
- **Install:** `pip install pdfplumber`

```python
import pdfplumber
with pdfplumber.open("report.pdf") as pdf:
    page = pdf.pages[0]
    table = page.extract_table()
```

- **When to use:** ONLY when MarkItDown's PDF handling is not sufficient for complex tabular data (multi-column layouts, merged cells, nested tables).
- **When NOT to use:** For general PDF reading. MarkItDown or Codex's native Read tool handles standard PDFs.

---

### 8. ffmpeg

- **Role:** Media processing (audio/video conversion, metadata extraction, transcription prep)
- **Install:** `winget install ffmpeg` or exe download from ffmpeg.org

```bash
# Convert video format
ffmpeg -i input.mov -c:v libx264 output.mp4

# Extract audio from video
ffmpeg -i video.mp4 -vn -acodec pcm_s16le audio.wav

# Get media info
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

- **When to use:** ONLY for environments specifically focused on media processing (filmmakers, podcasters, content creators).
- **When NOT to use:** For basic audio metadata extraction (MarkItDown handles it).

---

## Dual-Mode Pattern

For environments that do both quick analysis AND formatted output, include both MarkItDown and Pandoc. The routing rule selects per-interaction based on the task:

| Task Pattern | Mode | Inbound | Outbound | Context Cost |
|---|---|---|---|---|
| "Summarize this report" | Quick | MarkItDown | Text/Markdown | Low |
| "What are the key findings?" | Quick | MarkItDown | Text/Markdown | Low |
| "Produce a client-ready brief" | Quality | MarkItDown | Pandoc -> .docx | Medium |
| "Create a board presentation" | Quality | MarkItDown | Pandoc -> .pptx | Medium |
| "Update formulas in this spreadsheet" | Fidelity | openpyxl | openpyxl | Higher |

**Routing logic for AGENTS.md or agent instructions:**

```
If the user asks to READ/ANALYZE/SUMMARIZE a file:
  -> Use MarkItDown to convert to Markdown, then respond in text.

If the user asks to PRODUCE/CREATE/GENERATE a formatted document:
  -> Use MarkItDown for any input files, then Pandoc for output.

If the user asks to MODIFY/UPDATE an existing Excel file:
  -> Use openpyxl for round-trip fidelity.
```

---

## Inbox/Outbox/Data Directory Pattern

For environments with file processing, generate this directory structure:

```
<project>/
  Inbox/           # User drops files here for processing
    README.md      # "Place files here for Codex to process"
  Outbox/          # Codex places results here
    README.md      # "Find your processed files here"
  Data/            # Working data (intermediate, reference)
    README.md      # "Working data files -- managed by Codex"
```

Each README.md should contain a one-line purpose description so the directories are self-documenting and not empty (which some version control systems ignore).

---

## Brand Guidance Pattern

For environments where users produce branded documents, presentations, or reports.

**Brand/ directory structure:**
```
Brand/
  Templates/        # Pandoc reference documents (.docx, .pptx)
  Guidelines/       # Brand guides, style docs (any format MarkItDown can read)
  brand-rules.md    # Auto-generated brand rules (persistent, self-updating)
  README.md
```

**How Pandoc uses brand templates:**
- .docx template: `pandoc report.md -o report.docx --reference-doc=Brand/Templates/company-report.docx`
  - Pandoc extracts styles (headings, body text, fonts, colors, margins) from the template
  - Content is formatted according to those styles automatically
- .pptx template: `pandoc slides.md -t pptx -o deck.pptx --reference-doc=Brand/Templates/company-deck.pptx`
  - Pandoc uses the template's slide layouts, theme colors, fonts, and backgrounds
  - Codex writes plain Markdown with slide breaks; Pandoc applies the brand look

**brand-rules.md structure:**
```markdown
# Brand Rules

## Source Tracking
Last Generated: YYYY-MM-DD HH:MM
Sources:
- Guidelines/brand-guide.pdf (modified: YYYY-MM-DD HH:MM)
- Templates/company-report.docx (modified: YYYY-MM-DD HH:MM)

## Tone and Voice
- [Extracted from brand guide: formal/casual, active/passive, person]

## Terminology
- [Preferred terms and terms to avoid]

## Visual Identity
- Colors: [extracted palette]
- Fonts: [extracted font preferences]
- Logo usage: [rules if specified]

## Document Structure
- Required sections: [e.g., executive summary, disclaimers]
- Header/footer requirements: [if specified]
- Legal disclaimers: [required text if any]

## Formatting Conventions
- [Heading styles, list preferences, table formatting]
```

**Auto-update mechanism:**
brand-rules.md includes a Source Tracking section listing every file it was generated from and their last-modified dates. Before quality-mode output, the assistant checks:
1. Are there files in Brand/ not listed in Source Tracking?
2. Are any listed files newer than the Last Generated date?
3. If either: re-analyze, update brand-rules.md, then proceed with output.

The user never has to manually trigger a refresh -- they just drop updated files.

**When to include brand guidance:**
- User produces formatted documents AND has organizational brand requirements
- User explicitly mentions brand guidelines, templates, or style standards
- User works in compliance/legal/financial where consistent formatting is expected

**When NOT to include:**
- Personal projects with no brand requirements
- Internal-only documents where formatting doesn't matter
- Data-only environments (Excel/CSV output)

---

## Setup Instructions Template

For GETTING_STARTED.md in generated environments, include this section when file processing tools are configured. Include only the tools selected for the specific environment.

```markdown
## File Processing Setup

### Required (one-time):

```bash
pip install 'markitdown[all]'                      # Universal file reader
winget install pandoc                               # Document/presentation generator (if selected)
pip install openpyxl                                # Excel processing (if selected)
Install-Module ImportExcel -Scope CurrentUser       # Excel via PowerShell (if selected)
pip install pdfplumber                              # Advanced PDF tables (if selected)
pip install python-docx                             # Basic Word generation (if selected)
```

### How to use:
1. Drop files in the `Inbox/` folder
2. Tell Codex what you want: "Summarize the report in Inbox/" or "Create a presentation from the data in Inbox/"
3. Find your results in the `Outbox/` folder
```

---

## Tool Selection Rules for component-generator

When the component-generator builds a file processing environment, apply these rules in order:

1. **MarkItDown is always included** if the environment processes non-text files. No exceptions.
2. **Pandoc is included** if any of these are true:
   - User profile mentions clients, reports, presentations, or external deliverables.
   - The environment description includes document generation or formatted output.
   - The starter profile indicates consulting, legal, finance, or executive roles.
3. **openpyxl is included** if the environment reads AND writes Excel files.
4. **python-docx is included** only if Pandoc is NOT selected and .docx output is needed.
5. **python-pptx is included** only if the user needs programmatic slide manipulation (NOT content-to-slides generation).
6. **pdfplumber is included** only if the user explicitly needs complex PDF table extraction beyond what MarkItDown provides.
7. **ImportExcel is included** only if the environment is PowerShell-centric and Python is not the primary toolchain.
8. **ffmpeg is included** only if the environment explicitly involves media processing.

When in doubt between Pandoc and python-docx/python-pptx, choose Pandoc. It produces better output with less code.
