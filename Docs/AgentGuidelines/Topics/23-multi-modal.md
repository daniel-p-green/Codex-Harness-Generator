# 23. Multi-Modal Workflows

## 23.1 Model Selection by Task

- **Established**: 2026-03
- **Source**: Model routing playbook, IntuitionLabs pricing, web research | Tier 2
- **Recommendation**: No single model wins all tasks. During intake, determine which
  tasks the user performs and recommend model allocation across budget tiers:

  **Current specializations (early 2026)**:
  | Task | Best Model | Tier |
  |---|---|---|
  | Code implementation | Claude Opus 4.7 / Sonnet 4.6 | Any |
  | Architecture/complex reasoning | GPT-5.2 or Claude Opus 4.7 | Mid+ |
  | UI/Frontend work | Gemini 2.5 Pro | Mid+ |
  | Image/video understanding | Kimi K2.5 | Mid+ |
  | Budget/high-volume tasks | DeepSeek R1 / Gemini Flash | Any |
  | Quick exploration | Haiku / Flash | Any |

  **Budget tiers for intake recommendations**:

  | Tier | Monthly Cost | Strategy |
  |---|---|---|
  | Claude Only | $20-200 | Claude Pro/Max, no external models |
  | Claude + Free/Local | $20-50 | Claude Pro + Gemini free + local models (Ollama) |
  | Claude + Limited Expense | $100-300 | Claude Max + ChatGPT Plus + Gemini Advanced |
  | Rolls Royce | $500+ | API-first with intelligent routing, all models |

  Generated environments should document the user's chosen tier in GENESIS.md and
  configure MCP servers, API keys, and routing accordingly.

- **Anti-pattern**: Assuming the user only uses Claude. Ask during intake. Also: recommending
  expensive multi-model setups to users with budget constraints.

## 23.2 Multi-Model Orchestration Patterns

- **Established**: 2026-03
- **Source**: Addy Osmani workflow blog, LangChain/CrewAI docs, web research | Tier 2
- **Recommendation**: Four orchestration patterns, matched to user sophistication:

  **Manual routing** (beginners/solo): Copy prompts between web interfaces (ChatGPT,
  Claude, Gemini). No setup, surprisingly effective. Document which service to use for
  which task type in the environment's routing table comments.

  **CLI multi-tool** (intermediate): Use Claude Code for implementation, pipe output
  to other CLIs (Gemini CLI, Codex CLI) for review. gitingest or repo2txt for context
  packaging. Document commands in GETTING_STARTED.md.

  **MCP-bridged** (advanced): Use MCP servers to give Claude access to other models'
  capabilities (e.g., an MCP server wrapping Gemini's vision API for image understanding).
  Configure in .mcp.json.

  **API orchestration** (teams/enterprise): LangChain/LangGraph for stateful multi-model
  workflows, CrewAI for agent team coordination. Requires custom integration code.

- **Anti-pattern**: Building complex orchestration for a solo developer who would be fine
  with manual model switching. Match complexity to actual need.

## 23.3 AI Capability Extension (Beyond Claude's Native Abilities)

- **Established**: 2026-03
- **Source**: ComfyUI MCP ecosystem, ModelsLab API, Ollama integration docs,
  Google Nano Banana, community workflow patterns | Tier 2
- **Recommendation**: Claude Code excels at text reasoning, code generation, and
  file processing, but cannot natively generate images, video, audio, or 3D content.
  When intake reveals the user's workflow requires these capabilities, the generated
  environment should **extend Claude by integrating external AI tools**, not simply
  document them.

  **Philosophy: Proactive capability gap identification**

  During intake, don't just ask "what tools do you use?" -- identify what the
  user's workflow *needs* and proactively check whether Claude can do it natively.
  If not, present options, walk through trade-offs, and help the user choose.
  The generated environment then integrates the chosen tools so Claude can
  orchestrate workflows that span its native abilities and external AI capabilities.

  **Capability gap categories**:

  | Capability | Claude Native? | Extension Approach |
  |-----------|---------------|-------------------|
  | Text reasoning, code gen | Yes | N/A |
  | File processing (read/write) | Yes (with tools) | N/A |
  | Image understanding | Yes (Read tool) | N/A |
  | Browser automation | No (needs Playwright/MCP) | CLI or MCP |
  | **Image generation** | No | MCP server (ComfyUI, ModelsLab) or API skill |
  | **Video generation** | No | API skill (Nano Banana, Kling) or MCP |
  | **Audio/voice synthesis** | No | API skill (ElevenLabs) or CLI (Bark, Coqui) |
  | **3D model generation** | No | API skill (Meshy, Tripo) |
  | **Local model inference** | No | MCP server (Ollama) or CLI |
  | **Music generation** | No | API skill (Suno, Udio) |

  **Integration approaches** (from lightest to heaviest):

  1. **MCP server** (preferred when available): Claude calls tools natively.
     Example: ComfyUI MCP gives Claude `generate_image`, `run_workflow` tools.
     Add to .mcp.json, no custom code needed.
  2. **CLI wrapping** (for tools with CLIs): Generate a skill that invokes the
     CLI via Bash and parses output. Example: `ollama run <model> <prompt>`.
     Add Bash permission to settings.json.
  3. **API skill** (for cloud services): Generate a skill that makes HTTP calls
     to the service API. Requires API key management (settings.local.json for
     secrets, never settings.json).
  4. **Hybrid local+cloud**: Use local tools (ComfyUI, Ollama) for iteration
     and drafting, cloud APIs (DALL-E, Nano Banana) for final quality output.
     The environment routing table specifies when to use which.

  **Recommendation methodology for generated environments**:

  When intake reveals a capability gap, present the user with:
  1. The top 2-3 options for that capability (one local/free, one cloud/quality)
  2. A recommendation based on their budget tier and technical comfort
  3. Trade-offs: cost, quality, setup complexity, privacy
  4. Whether the tool has MCP integration (simplest path) or needs CLI wrapping

  The architect should consult `tool-registry.md` for the specific tools in each
  capability category and their matching rules.

  **Key tools by capability** (see tool-registry.md for full details):

  **Image Generation**:
  - Local/free: ComfyUI + Stable Diffusion/FLUX (MCP server available, full control)
  - Cloud/API: DALL-E 3 (OpenAI API), Midjourney (API), ModelsLab (MCP available)
  - Google: Nano Banana 2 (via Gemini API, high quality, fast)

  **Video Generation**:
  - Cloud/API: Nano Banana Video (Google, studio quality), Kling (Kuaishou),
    Runway Gen-3, Minimax
  - Local: ComfyUI + AnimateDiff / LTX Video / CogVideoX (GPU-intensive)

  **Local Model Inference**:
  - Ollama (simplest setup, native Claude Code integration since v0.14,
    Anthropic Messages API compatible)
  - LM Studio (GUI-first, OpenAI-compatible endpoint)
  - vLLM / KTransformers (for larger models, production use)
  - Kimi K2.5 (1T MoE, 32B active, open weights, vision + agent swarm)

  **Audio/Voice**:
  - Cloud: ElevenLabs (highest quality TTS), PlayHT
  - Local: Bark (Suno), Coqui TTS (open source), Whisper (transcription)

  **Budget-aware defaults**:
  - Claude Only tier: Skip generative AI or use free local tools only
  - Claude + Free/Local tier: ComfyUI for images, Ollama for local LLM, Bark for TTS
  - Claude + Limited Expense tier: Add cloud APIs for higher quality (DALL-E, ElevenLabs)
  - Rolls Royce tier: Best-in-class for each capability, intelligent routing

- **Anti-pattern**: Recommending generative AI tools when the user's workflow
  doesn't need them. Also: defaulting to expensive cloud APIs when free local
  alternatives exist and the user is budget-conscious. Also: generating complex
  multi-tool integration when the user would be fine opening a separate app
  (Midjourney in Discord, ComfyUI in browser). Integration should add value
  by enabling Claude to orchestrate the workflow, not just add complexity.

## 23.4 Guided Tool Selection During Intake

- **Established**: 2026-03
- **Source**: Intake design patterns, capability gap analysis | Tier 2
- **Recommendation**: When intake reveals a capability gap, the Harness Generator should
  walk the user through selection rather than silently picking a tool:

  **Selection flow** (embedded in intake, not a separate step):
  1. **Identify the gap**: "Your workflow involves [capability]. Claude can't
     do this natively, but it can orchestrate external tools that can."
  2. **Present options**: Show 2-3 options with a recommendation, formatted as:
     - Tool name, one-line description
     - Setup complexity (easy/moderate/advanced)
     - Cost (free/freemium/paid with price range)
     - Integration quality (MCP native / CLI wrap / API skill)
  3. **Recommend**: "For your setup, I'd recommend [tool] because [reason]."
     Let the user override.
  4. **Record in GENESIS.md**: Capture the chosen tool(s) in a new
     "AI Ecosystem Extensions" section so the architect can generate
     integration components.

  **Multiple tools for the same capability**: Some users want both a local
  option (for iteration/privacy) and a cloud option (for final quality).
  Record both in GENESIS.md. The architect generates routing rules that
  let the user specify which to use per-invocation.

  This approach respects user agency -- the Harness Generator recommends but doesn't
  dictate. Users know their budget, privacy requirements, and quality bar
  better than any automated system.

- **Anti-pattern**: Silently selecting tools without explaining trade-offs.
  Also: presenting too many options (decision paralysis). Two or three options
  with a clear recommendation is optimal.

---
