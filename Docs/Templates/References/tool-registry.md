# Tool Registry

Single source of truth for all third-party tools, plugins, and services recommended
by the Harness Generator. The environment-architect reads matching rules from here.
The /update skill verifies tools against this registry for currency.

**Last Updated:** 2026-05-31 (90-day verification pass; Kimi K2.5 -> K2.6, Nano Banana 2 reverified active, `/simplify` bundled skill renamed to `/code-review`; GPT-5.5 flagship)

---

## Registry Index

Every recommended tool appears here with key metadata. Status values:
- **Active**: Verified current, recommended when matching rules apply
- **Experimental**: New or emerging, recommend with caveats
- **Deprecated**: Superseded or abandoned, remove from new environments

| ID | Tool | Category | Last Verified | Status | Supersedes |
|----|------|----------|---------------|--------|------------|
| FP-01 | MarkItDown | File Processing | 2026-03 | Active | -- |
| FP-02 | Pandoc | File Processing | 2026-03 | Active | -- |
| FP-03 | python-docx | File Processing | 2026-03 | Active | -- |
| FP-04 | python-pptx | File Processing | 2026-03 | Active | -- |
| FP-05 | openpyxl | File Processing | 2026-03 | Active | -- |
| FP-06 | ImportExcel | File Processing | 2026-03 | Active | -- |
| FP-07 | pdfplumber | File Processing | 2026-03 | Active | -- |
| FP-08 | ffmpeg | File Processing | 2026-03 | Active | -- |
| DP-01 | PaddleOCR | Document Parsing | 2026-03 | Active | -- |
| DP-02 | MinerU | Document Parsing | 2026-03 | Active | -- |
| DP-03 | Docling | Document Parsing | 2026-03 | Active | -- |
| BA-01 | Playwright CLI | Browser Automation | 2026-03 | Active | BA-02 (preferred) |
| BA-02 | Playwright MCP | Browser Automation | 2026-03 | Active | -- |
| BA-03 | Chrome DevTools MCP | Browser Automation | 2026-03 | Active | -- |
| BA-04 | Codex browser/app workflows | Browser Automation | 2026-03 | Active | -- |
| PM-01 | Synabun | Persistent Memory | 2026-03 | Active | -- |
| PM-02 | codex memories | Persistent Memory | 2026-03 | Active | -- |
| PM-03 | mcp-memory-service | Persistent Memory | 2026-03 | Active | -- |
| CI-01 | Codex Context MCP | Codebase Intelligence | 2026-03 | Active | -- |
| CI-02 | Code-Graph-RAG | Codebase Intelligence | 2026-03 | Experimental | -- |
| SD-01 | skill-creator | Skill Development | 2026-03 | Active | -- |
| TT-01 | Beads | Task Tracking | 2026-03 | Active | -- |
| PK-01 | Obsidian (+ obsidian-mcp) | PKM Integration | 2026-03 | Active | -- |
| PK-02 | Logseq | PKM Integration | 2026-03 | Active | -- |
| IG-01 | ComfyUI (+ MCP) | Image Generation | 2026-03 | Active | -- |
| IG-02 | ModelsLab API (+ MCP) | Image Generation | 2026-03 | Active | -- |
| IG-03 | DALL-E 3 (OpenAI API) | Image Generation | 2026-03 | Active | -- |
| IG-04 | Nano Banana 2 (Google) | Image Generation | 2026-03 | Active | -- |
| VG-01 | Nano Banana Video (Google) | Video Generation | 2026-03 | Active | -- |
| VG-02 | Kling (Kuaishou) | Video Generation | 2026-03 | Active | -- |
| VG-03 | ComfyUI + AnimateDiff | Video Generation | 2026-03 | Active | -- |
| VG-04 | Runway Gen-3 | Video Generation | 2026-03 | Active | -- |
| LI-01 | Ollama | Local Inference | 2026-03 | Active | -- |
| LI-02 | LM Studio | Local Inference | 2026-03 | Active | -- |
| LI-03 | Kimi K2.6 (Moonshot) | Local Inference | 2026-05 | Active | Kimi K2.5 |
| LI-04 | vLLM | Local Inference | 2026-03 | Active | -- |
| AG-01 | ElevenLabs | Audio Generation | 2026-03 | Active | -- |
| AG-02 | Bark (Suno) | Audio Generation | 2026-03 | Active | -- |
| AG-03 | Coqui TTS | Audio Generation | 2026-03 | Active | -- |
| AP-01 | document-skills | OpenAI Official | 2026-03 | Active | -- |
| AP-02 | example-skills | OpenAI Official | 2026-03 | Active | -- |
| AP-03 | openai-api | OpenAI Official | 2026-03 | Active | -- |
| NB-01 | notebooklm-py | NotebookLM Integration | 2026-03 | Active | -- |
| WS-01 | Context7 | Web/Search | 2026-03 | Active | -- |
| WS-02 | Firecrawl | Web/Search | 2026-03 | Active | -- |
| WS-03 | Exa Search | Web/Search | 2026-03 | Active | -- |

---

## Category Details

### File Processing (FP-01 through FP-08)

Detailed specifications, install commands, usage examples, and selection rules
are in `tool-catalog.md` (same directory). That file is the authoritative
reference for this category. Do not duplicate its content here.

**Matching rule**: Include file processing tools when GENESIS.md mentions
reading, processing, or producing non-text files. See tool-catalog.md for
per-tool selection rules.

---

### Document Parsing (DP-01 through DP-03)

For environments with external reference documents (PDFs, design specs, API docs).
These tools convert complex documents to structured markdown for wiki ingestion.

| ID | Tool | Install | Best For | Limitations |
|----|------|---------|----------|-------------|
| DP-01 | PaddleOCR | `pip install paddleocr paddlepaddle` | Scanned docs, OCR-heavy | Large install (~2GB), GPU optional |
| DP-02 | MinerU | `pip install magic-pdf` | Structured markdown from PDFs | Research-focused, may need tuning |
| DP-03 | Docling | `pip install docling` | Hierarchical document structure | IBM project, active development |

**Matching rules**:
- 1-5 reference docs, simple formats -> Skip (Codex's native Read handles PDFs)
- 5-20 reference docs, mostly PDF -> DP-01 (PaddleOCR) for scanned, DP-03 (Docling) for digital
- 20+ reference docs or complex layouts -> DP-02 (MinerU) for bulk processing
- Mixed quality (some scanned, some digital) -> DP-01 + DP-03 together

**Architecture output**: Document in GETTING_STARTED.md setup section. Include
tool recommendation and brief pipeline description. Do NOT auto-install.

---

### Browser Automation (BA-01 through BA-04)

For environments needing web interaction: testing web apps, scraping, form automation.

| ID | Tool | Install | Token Cost | Best For |
|----|------|---------|------------|----------|
| BA-01 | Playwright CLI | `npm i -g @playwright/test` | ~27K/session | Codex + browser testing (default) |
| BA-02 | Playwright MCP | MCP server config | ~114K/session | Sandboxed agents without shell access |
| BA-03 | Chrome DevTools MCP | MCP server config | Varies | Performance profiling, Core Web Vitals |
| BA-04 | Codex browser/app workflows | Chrome extension | N/A | Authenticated workflows on logged-in sites |

**Key insight**: Playwright CLI is 4x more token-efficient than Playwright MCP
(~27K vs ~114K tokens per session). It saves page snapshots to disk as YAML,
keeping the context clean. Prefer BA-01 for Codex environments.

**Matching rules**:
- Frontend/web dev, testing, web scraping -> BA-01 (Playwright CLI, default)
- Sandboxed agents, no shell access -> BA-02 (Playwright MCP, fallback only)
- Performance profiling, Core Web Vitals -> BA-03 (Chrome DevTools MCP)
- Authenticated browser workflows (logged-in sites) -> BA-04 (Codex browser/app workflows)
- No web interaction mentioned -> Omit entirely

**Architecture output**: Include in section 10b Recommended Plugins. Document
setup in GETTING_STARTED.md.

---

### Persistent Memory (PM-01 through PM-03)

Optional enhancements for projects where built-in /state-save and markdown wiki
are insufficient. Never a requirement -- always framed as optional.

| ID | Tool | Install | Best For | Key Feature |
|----|------|---------|----------|-------------|
| PM-01 | Synabun | `npm install -g synabun && synabun start` | Non-coding, visual users | Semantic vector memory, 46 MCP tools, 3D visualization |
| PM-02 | codex memories | `npm install -g codex memories` | Heavy coding, long sessions | "Endless Mode" (~20x context), auto-summarize |
| PM-03 | mcp-memory-service | MCP server config | Multi-agent pipelines | Knowledge graph, ChromaDB backend |

**Matching rules** (recommend ONE, not multiple):
- Node.js or non-coding project, wants visual UI -> PM-01 (Synabun)
- Heavy coding, long sessions, context limit issues -> PM-02 (codex memories)
- Python project or multi-agent pipeline -> PM-03 (mcp-memory-service)

**Trigger signals** (must have at least one):
- User reports context loss between sessions ("Codex keeps forgetting")
- Multi-session projects with complex architectural decisions
- Large codebases (1000+ files)
- Teams sharing context across developers

**Architecture output**: Include in section 10c with "optional enhancement"
framing. Document in GETTING_STARTED.md. Note hook conflicts if environment
uses same hook events.

---

### Codebase Intelligence (CI-01 through CI-02)

For large codebases where grep/glob are insufficient for navigation.

| ID | Tool | Install | Best For | Maturity |
|----|------|---------|----------|----------|
| CI-01 | Codex Context MCP | MCP server config | Semantic code search, 1000+ files | Stable |
| CI-02 | Code-Graph-RAG | Custom setup | Cross-file dependency analysis | Experimental |

**Matching rules**:
- 1000+ source files, frequent "where is X" questions -> CI-01
- Complex dependency chains, architectural analysis -> CI-02 (with caveats)
- < 1000 files -> Omit (shell-first search + /map-codebase sufficient)

**Architecture output**: Document in GETTING_STARTED.md. Include MCP config
in .codex/config.toml suggestions.

---

### Skill Development (SD-01)

| ID | Tool | Install | Purpose |
|----|------|---------|---------|
| SD-01 | skill-creator | `/plugin marketplace add openai/skills` then `/plugin install skill-creator` | Eval framework for validating and improving custom skills (from the openai/skills marketplace) |

**What it does**: 4 modes (Create/Eval/Improve/Benchmark), 4 sub-agents
(Executor/Grader/Comparator/Analyzer). Creates eval test suites that verify
skill triggering accuracy, output quality, and edge case handling.

**Matching rules**:
- Environment has 3+ custom skills AND intermediate+ user -> Recommend in GETTING_STARTED.md
- Fewer than 3 custom skills -> Omit (overhead not justified)
- Beginner users -> Omit (too complex for onboarding)

**Architecture output**: "Refining Your Skills" section in GETTING_STARTED.md
with install command and brief workflow description.

---

### Task Tracking (TT-01)

| ID | Tool | Install | Purpose |
|----|------|---------|---------|
| TT-01 | Beads | `pip install beads-cli && bd init` | Git-backed task tracker for complex multi-session projects |

**Matching rules**:
- Complex multi-session project with interdependent subtasks -> Recommend
- Intermediate+ user required (beginners: too complex)
- Git required as persistence layer (non-Git VCS: flag trade-off)
- Simple projects or single-session work -> Omit

**Architecture output**: Include `bd init` setup, Codex hooks,
.codex/config.toml permissions. Complements (does not replace) /state-save.

---

### PKM Integration (PK-01 through PK-02)

Personal knowledge management tools that Codex reads/writes to as a shared
knowledge layer. Different from Codex-specific memory plugins (PM category):
PKM tools are user-managed, general-purpose knowledge stores.

| ID | Tool | Integration | Best For |
|----|------|-------------|----------|
| PK-01 | Obsidian (+ obsidian-mcp) | File-based (direct vault access) or MCP server | Research, note-taking, zettelkasten workflows |
| PK-02 | Logseq | File-based (direct vault access) | Outliner-style knowledge capture, daily journals |

**Matching rules**:
- User explicitly mentions Obsidian, Logseq, or "my notes app" -> Include
- User describes research accumulation workflow -> Ask about PKM tool
- User does NOT mention a PKM tool -> Omit entirely (never recommend speculatively)

**Architecture output**: Vault path in .codex/config.toml, conventions rule file,
optional `/capture-knowledge` skill. See Pattern H in architect.

---

### Image Generation (IG-01 through IG-04)

Extends Codex with image creation capabilities. Codex orchestrates:
writes prompts, invokes the tool, analyzes results, iterates.

| ID | Tool | Type | Cost | Integration | Best For |
|----|------|------|------|-------------|----------|
| IG-01 | ComfyUI (+ MCP) | Local | Free (needs GPU) | MCP server | Full control, custom workflows, SD/FLUX models |
| IG-02 | ModelsLab API (+ MCP) | Cloud | Freemium | MCP server | Hundreds of models, easy setup, no local GPU |
| IG-03 | DALL-E 3 (OpenAI) | Cloud | Pay-per-image | API skill | High quality, simple API, widely known |
| IG-04 | Nano Banana 2 (Google) | Cloud | Gemini API | API skill | Fast, real-time knowledge, text rendering |

**Matching rules** (recommend based on budget tier + needs):
- Budget-conscious + has GPU -> IG-01 (ComfyUI, free, full control)
- Budget-conscious + no GPU -> IG-02 (ModelsLab, free tier available)
- Balanced + wants simplicity -> IG-03 (DALL-E, familiar API) or IG-04 (Nano Banana)
- Quality-first -> IG-01 + IG-03 (local for iteration, cloud for final)
- Game dev / needs specific styles -> IG-01 (ComfyUI, LoRA/ControlNet support)

**Architecture output**: MCP config or API skill in Pass 3. API keys in
local config profile. Routing entry for image generation requests.

---

### Video Generation (VG-01 through VG-04)

| ID | Tool | Type | Cost | Integration | Best For |
|----|------|------|------|-------------|----------|
| VG-01 | Nano Banana Video | Cloud | Gemini API | API skill | Studio quality, text-to-video, multi-scene |
| VG-02 | Kling (Kuaishou) | Cloud | Freemium | API skill | High quality, affordable |
| VG-03 | ComfyUI + AnimateDiff | Local | Free (needs GPU) | MCP server | Full control, privacy, no per-video cost |
| VG-04 | Runway Gen-3 | Cloud | Subscription | API skill | Established, reliable, professional |

**Matching rules**:
- Budget-conscious -> VG-03 (local) or skip video gen
- Balanced -> VG-01 (Nano Banana, Google ecosystem) or VG-02 (Kling)
- Quality-first / professional -> VG-01 + VG-04 (compare outputs)
- Needs privacy / offline -> VG-03 only

**Architecture output**: API skill in Pass 3. Document setup in GETTING_STARTED.md.

---

### Local Inference (LI-01 through LI-04)

Run open-source models locally for privacy, cost savings, or specialized tasks.

| ID | Tool | Install | Integration | Best For |
|----|------|---------|-------------|----------|
| LI-01 | Ollama | `curl -fsSL https://ollama.ai/install.sh \| sh` | Native Codex (v0.14+), MCP server | Simplest setup, any model, 98% token savings |
| LI-02 | LM Studio | Desktop app download | OpenAI-compatible endpoint | GUI-first users, model browsing |
| LI-03 | Kimi K2.6 | HuggingFace weights + vLLM/KTransformers | API endpoint | Vision + agent swarm, 1T MoE (32B active); K2.6 is the current production release (supersedes K2.5) |
| LI-04 | vLLM | `pip install vllm` | OpenAI-compatible endpoint | Production serving, high throughput |

**Matching rules**:
- Wants local LLM + easy setup -> LI-01 (Ollama, simplest path)
- Wants GUI for model management -> LI-02 (LM Studio)
- Needs vision + code + long context -> LI-03 (Kimi K2.6)
- Production/team serving -> LI-04 (vLLM)
- No local GPU or simple project -> Omit

**Architecture output**: MCP config (OllamaCodex MCP) or environment variables
for Codex native Ollama support. Document model recommendations in
GETTING_STARTED.md.

---

### Audio Generation (AG-01 through AG-03)

| ID | Tool | Type | Cost | Integration | Best For |
|----|------|------|------|-------------|----------|
| AG-01 | ElevenLabs | Cloud | Freemium | API skill | Highest quality TTS, voice cloning |
| AG-02 | Bark (Suno) | Local | Free | CLI wrapping | Free TTS with emotion, multilingual |
| AG-03 | Coqui TTS | Local | Free (open source) | CLI wrapping | Open source, customizable voices |

**Matching rules**:
- Needs voice/narration + budget -> AG-02 (Bark) or AG-03 (Coqui)
- Needs professional quality -> AG-01 (ElevenLabs)
- Content creation / podcasting -> AG-01 + Whisper (for transcription)
- No audio needs -> Omit entirely

**Architecture output**: API skill or CLI-wrapping skill. Document setup in
GETTING_STARTED.md.

---

### OpenAI Official Skills (AP-01 through AP-03)

From `developers.openai.com/codex/concepts/customization`. Installed via marketplace, not statically copied.

| ID | Collection | Key Skills | Matching Signals |
|----|-----------|------------|------------------|
| AP-01 | document-skills | Word/Excel/PDF processing | Office documents, spreadsheets |
| AP-02 | example-skills | skill-creator, web testing, brand guide | Frontend dev, custom skills, brand guidelines |
| AP-03 | openai-api | API/SDK development helpers | Building with OpenAI API |

**Matching rules**:
- Office documents (Excel, Word, PowerPoint, PDF) -> AP-01 (document-skills)
- Frontend/web dev or web testing -> AP-02 (example-skills)
- Building MCP servers -> AP-02 (example-skills)
- Brand/design guidelines -> AP-02 (example-skills)
- OpenAI API/SDK development -> AP-03 (openai-api)
- User wants to create custom skills -> AP-02 (example-skills, includes skill-creator)

**Bundled skills** (no install needed, just mention in GETTING_STARTED.md):
- `/code-review` -- Correctness review of changed files at chosen effort (`--fix`, `--comment`); renamed from `/simplify` (v2.1.147)
- `/batch` -- Process multiple files with same operation (useful for 50k+ line codebases)
- `/debug` -- Structured debugging workflow
- `/openai-api` -- OpenAI API development helper

---

## Verified MCP Servers

**CRITICAL**: The architect and component-generator may ONLY recommend MCP servers
listed in this table. If a user mentions an external service with no verified MCP
server here, do NOT invent one. Instead, suggest browser/API/export workflows.

### Vendor-Official Servers (maintained by the product company)

| ID | Server | Package / Command | Verified | Status | Use Case |
|----|--------|-------------------|----------|--------|----------|
| MC-01 | GitHub (official) | `npx -y @modelcontextprotocol/server-github` | 2026-03 | Active | Issues, PRs, repos, code search |
| MC-02 | Playwright (Microsoft) | `npx @playwright/mcp@latest` | 2026-03 | Active | Browser automation (sandboxed) |
| MC-03 | Notion (official) | `npx -y @notionhq/notion-mcp-server` | 2026-03 | Active | Pages, databases, blocks, search |
| MC-04 | Brave Search (official) | `npx -y @brave/brave-search-mcp-server` | 2026-03 | Active | Web/news/image search |
| MC-05 | Sentry (official) | `npx @sentry/mcp-server` or remote `https://mcp.sentry.dev/mcp` | 2026-03 | Active | Error tracking, stack traces |
| MC-06 | Linear (official) | Remote: `codex mcp add linear -- npx -y mcp-remote https://mcp.linear.app/sse` | 2026-03 | Active | Issues, projects, teams |
| MC-07 | Figma (official) | Remote: `codex mcp add --transport http figma https://mcp.figma.com/mcp` | 2026-03 | Active | Design files, components, tokens |
| MC-08 | Supabase (official) | `npx -y @supabase/mcp-server-supabase` | 2026-03 | Active | Database, auth, storage |
| MC-09 | Vercel (official) | Remote: `codex mcp add --transport http vercel https://mcp.vercel.com` | 2026-03 | Active | Deployments, builds, domains |
| MC-10 | AWS (awslabs) | `uvx awslabs.core-mcp-server@latest` (router for all AWS servers) | 2026-03 | Active | AWS docs, CDK, ECS, Lambda, etc. |

### MCP Reference Servers (modelcontextprotocol org)

| ID | Server | Package / Command | Verified | Status | Use Case |
|----|--------|-------------------|----------|--------|----------|
| MC-20 | Filesystem | `npx -y @modelcontextprotocol/server-filesystem <path>` | 2026-03 | Active | Sandboxed file access |
| MC-21 | Git | `uvx mcp-server-git --repository <path>` | 2026-03 | Active | Git repo read, diff, log, blame |
| MC-22 | Memory (knowledge graph) | `npx -y @modelcontextprotocol/server-memory` | 2026-03 | Active | Entity-relation persistent memory |
| MC-23 | Sequential Thinking | `npx -y @modelcontextprotocol/server-sequential-thinking` | 2026-03 | Active | Step-by-step reasoning |
| MC-24 | Fetch | `uvx mcp-server-fetch` | 2026-03 | Active | URL fetch + convert to markdown |
| MC-25 | SQLite | `uvx mcp-server-sqlite --db-path <path>` | 2026-03 | Active | SQLite database access |

### Third-Party Verified Servers (high-quality community)

| ID | Server | Package / Command | Verified | Status | Use Case |
|----|--------|-------------------|----------|--------|----------|
| MC-30 | MarkItDown | `uvx markitdown-mcp` | 2026-03 | Active | Document conversion to markdown |
| MC-31 | Synabun | `npm install -g synabun && synabun start` | 2026-03 | Active | Persistent vector memory, 46 tools |
| MC-32 | mcp-memory-service | `npx -y mcp-memory-service` | 2026-03 | Active | ChromaDB-backed memory |
| MC-33 | Obsidian MCP | `npx -y obsidian-mcp` | 2026-03 | Active | Obsidian vault access |
| MC-34 | ComfyUI MCP | `npx -y comfyui-mcp` | 2026-03 | Experimental | Image generation |
| MC-35 | Chrome DevTools | `npx -y chrome-devtools-mcp` | 2026-03 | Active | Performance profiling |
| MC-36 | Context7 | `npx -y @upstash/context7-mcp` | 2026-03 | Active | Up-to-date library docs (48K stars) |
| MC-37 | Firecrawl | `npx -y firecrawl-mcp` | 2026-03 | Active | Web scraping, site crawling |
| MC-38 | Exa Search | `npx -y exa-mcp-server` | 2026-03 | Active | Semantic web/academic search |
| MC-39 | Google Workspace | `uvx workspace-mcp` | 2026-03 | Community | Gmail, Drive, Docs, Sheets, Calendar |
| MC-40 | Jira (community) | `npx @aashari/mcp-server-atlassian-jira` | 2026-03 | Community | Issues, projects, JQL search |
| MC-41 | notebooklm-py | `pip install notebooklm-py` (Python library + Codex skills) | 2026-03 | Active | Google NotebookLM automation (3.7K stars) |

### Deprecated MCP Packages (DO NOT recommend)

| Old Package | Status | Replacement |
|-------------|--------|-------------|
| `@modelcontextprotocol/server-github` | Archived 2025-05 | MC-01 (`@modelcontextprotocol/server-github` from github org) |
| `@modelcontextprotocol/server-postgres` | Archived 2025-07 | Use Supabase (MC-08) or direct `psql` |
| `@modelcontextprotocol/server-brave-search` | Archived 2025-05 | MC-04 (`@brave/brave-search-mcp-server`) |
| `@modelcontextprotocol/server-puppeteer` | Archived 2025-05 | MC-02 (`@playwright/mcp`) |
| `@modelcontextprotocol/server-gdrive` | Archived 2025-05 | MC-39 (`workspace-mcp`) |
| `@modelcontextprotocol/server-slack` | Archived 2025-05 | No drop-in replacement yet |
| `@modelcontextprotocol/server-sentry` | Archived 2025-05 | MC-05 (`@sentry/mcp-server`) |

### Services WITHOUT verified MCP servers (do not recommend MCP)

- Microsoft 365 (Word, Excel, Outlook)
- Slack (archived reference server; no stable replacement yet)
- Discord
- Asana
- Confluence (no standalone verified server)

For these services, recommend: export/download files for local processing,
use browser automation (Playwright CLI) for interactive workflows, or use
direct API calls via skills.

### MCP Verification Protocol

Before adding a new MCP server to this registry, verify:
1. **Repository exists** and is publicly accessible
2. **Recent activity**: commits within the last 6 months
3. **Install works**: package exists on npm/PyPI/uvx
4. **Not archived/deprecated**: check GitHub repo status and README
5. **Minimum quality**: vendor-official OR 50+ stars OR referenced by official docs
6. **No known security issues**: check GitHub security advisories

The /update skill runs this protocol when verifying MCP servers. The architect
must NEVER recommend an MCP server not in this registry.

---

## Verification Protocol

The /update skill uses this protocol to keep the registry current:

1. **Check verification dates**: Flag tools not verified in 90+ days
2. **Web search per flagged tool**: Search for "[tool name] latest version 2026"
3. **Check for supersession**: Search for "alternative to [tool name]" or "[tool name] deprecated"
4. **Update registry**: Bump Last Verified date, update version/status, add Supersedes column
5. **Propagate changes**: If a tool's status changes to Deprecated, update:
   - Relevant topic file in Docs/AgentGuidelines/Topics/ (remove or mark deprecated)
   - environment-architect.md (update matching rules)
   - Downstream references (starter profiles, generation standards, quality gates)

### Adding a New Tool

When a new tool is identified (via /update web research or local-only ingest, or user report):

1. Add entry to Registry Index table with status "Experimental" or "Active"
2. Add detail entry in the appropriate Category section
3. Write matching rules (what GENESIS.md signals trigger this tool)
4. Add reference in the relevant topic file under Docs/AgentGuidelines/Topics/
5. Update environment-architect.md if matching rules affect architecture decisions
6. Update INDEX.md if the tool changes the topic's key takeaway

### Removing a Tool

1. Change status to "Deprecated" in Registry Index (do not delete the row)
2. Add Supersedes note pointing to replacement (if any)
3. Remove from matching rules (stop recommending for new environments)
4. Add note to the relevant topic file explaining deprecation
5. Keep row in registry for 6 months for audit trail, then archive

---

## Cross-Reference Map

Shows where each tool category is referenced across the project.
When updating a tool, check all referenced files.

| Category | Topics/NN-name.md | Architect | Gen Standards | Quality Gates | Intake | Profiles |
|----------|--------------|-----------|---------------|---------------|--------|----------|
| File Processing | 22.x | Pattern E | -- | -- | -- | All |
| Document Parsing | 22.x | Pattern E | Item 19 | Check 30 | Probe | -- |
| Browser Automation | 17.6 | 10b | -- | -- | Follow-up | -- |
| Persistent Memory | 5.10 | 10c | Item 29 | Check 38 | Probe | -- |
| PKM Integration | 5.11 | Pattern H | -- | -- | Follow-up | -- |
| Codebase Intelligence | 21.x | -- | Item 21 | -- | Probe | SW, Game |
| Skill Development | 3.10 | 10b | Item 28 | Check 37 | -- | -- |
| Task Tracking | 9.5 | Pattern | Item 24 | Check 32 | Probe | -- |
| OpenAI Official | 20.x | 10b | Item 27 | Check 36 | -- | -- |
| Image Generation | 23.3 | Pattern I | -- | -- | Probe | -- |
| Video Generation | 23.3 | Pattern I | -- | -- | Probe | -- |
| Local Inference | 23.3 | Pattern I | -- | -- | Probe | -- |
| Audio Generation | 23.3 | Pattern I | -- | -- | Probe | -- |
| Pipeline Skills | 3.11, 3.12 | Pattern G | -- | -- | Follow-up | -- |
