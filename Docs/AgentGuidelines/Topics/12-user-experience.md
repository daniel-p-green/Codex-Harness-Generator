# 12. User Experience

## 12.1 First-Run Onboarding

- **Established**: Baseline
- **Source**: Derived from https://developers.openai.com/codex/concepts/customization, https://developers.openai.com/api/docs/guides/reasoning | Tier 1
- **Recommendation**: Generate a first-run detection mechanism: check `Docs/index.md`
  for a `Status: NEW_ENVIRONMENT` marker. On first run:
  - Plain-language greeting explaining what the environment does
  - Available commands with brief descriptions
  - 2-3 suggested first actions
  - Link to GETTING_STARTED.md

  On returning sessions: normal operation without the onboarding message. Remove the
  NEW_ENVIRONMENT marker after first successful session.
- **Anti-pattern**: No first-run guidance. Users do not know what commands are available or
  how to start using the environment. They either give up or use it suboptimally.

## 12.2 Plain Language

- **Established**: Baseline
- **Source**: Derived from https://developers.openai.com/api/docs/guides/reasoning | Tier 1
- **Recommendation**: Use plain language in all user-facing output. Technical vocabulary only
  in generated configuration files. Vocabulary adaptation:
  - "assistant" not "agent" (for non-technical users)
  - "save your progress" not "/state-save"
  - "check environment health" not "/health-check"
  - "improve based on usage" not "self-learning friction log"

  Generated environments should adapt vocabulary based on the intake profile. A software
  developer sees technical terms; a legal professional sees plain language.
- **Anti-pattern**: Using jargon in user-facing output for non-technical users. Terms like
  "subagent orchestration" and "context compaction" confuse users outside the AI/ML domain.

## 12.3 Progress Indicators

- **Established**: Baseline
- **Source**: Derived from common-workflows.md | Tier 1
- **Recommendation**: For multi-step operations (environment generation, health checks,
  updates), provide progress indicators:
  - "Creating foundation files... done (1/5)"
  - "Validating environment... 15/22 checks passed"
  - "Analyzing friction patterns... found 3 proposals"

  Use the `statusMessage` field in hooks for custom spinner text during long operations.
- **Anti-pattern**: Silent long-running operations. Users cannot tell if the process is
  working, stuck, or failed without progress feedback.

## 12.4 GETTING_STARTED.md

- **Established**: Baseline
- **Source**: Derived from multiple sources | Tier 1
- **Recommendation**: Every generated environment must include `Docs/GETTING_STARTED.md`:
  - What this environment is (1-2 sentences)
  - Quick start (3-5 steps to first useful interaction)
  - Available commands with plain-language descriptions
  - How to save/restore progress
  - How the environment improves with use
  - Common first-time issues and solutions
  - Where to find more detailed documentation

  This file is for humans, not for Codex. Keep it concise and actionable.
- **Anti-pattern**: No GETTING_STARTED.md or an overly technical one. Users should be
  productive within 5 minutes of reading this file.

---
