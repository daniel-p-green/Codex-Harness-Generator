#!/usr/bin/env python3
"""Evaluate whether this repository has been fully ported to Codex.

This is intentionally strict. The goal is to keep the port honest: no hidden
Claude runtime assumptions, no stale Anthropic model guidance, and no generated
environment that still targets `.claude/` or `CLAUDE.md`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from pathlib import Path


TEXT_SUFFIXES = {
    ".md",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".txt",
}

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}

FORBIDDEN_PATTERNS = [
    (r"\bClaude\b", "Claude naming remains"),
    (r"\bClaude Code\b", "Claude Code platform reference remains"),
    (r"\bAnthropic\b", "Anthropic platform reference remains"),
    (r"\bOpus\b", "Anthropic model family reference remains"),
    (r"\bSonnet\b", "Anthropic model family reference remains"),
    (r"\bHaiku\b", "Anthropic model family reference remains"),
    (r"\bCLAUDE\.md\b", "Claude instruction filename remains"),
    (r"(^|/)\.claude(/|$)", "Claude runtime path remains"),
    (r"\bsettings\.json\b", "Claude settings file remains"),
    (r"\ballowed-tools\b", "Claude skill frontmatter remains"),
    (r"\bmaxTurns\b", "Claude agent schema remains"),
    (r"\bTask tool\b", "Claude Task tool reference remains"),
    (r"\bclaude\b", "lowercase claude command or path remains"),
    (r"\bopus\b", "legacy lowercase model family reference remains"),
    (r"\bsonnet\b", "legacy lowercase model family reference remains"),
    (r"\bhaiku\b", "legacy lowercase model family reference remains"),
    (r"\banthropic\b", "legacy lowercase platform reference remains"),
    (r"ANTHROPIC_", "legacy provider environment variable remains"),
    (r"\.codex/\.codex", "duplicated Codex config path remains"),
    (r"\.codexignore", "unsupported legacy ignore file remains"),
    (r"settings-json", "legacy settings-json check name remains"),
    (r"\.codex/config\.toml[^.\n]*(valid|invalid|contains invalid) JSON", "Codex TOML described as JSON"),
    (r"valid JSON[^.\n]*\.codex/config\.toml", "Codex TOML described as JSON"),
    (r"\bYAML frontmatter\b", "legacy agent YAML schema remains"),
    (r"\bfrontmatter\b[^.\n]*runtime budget", "legacy agent frontmatter schema remains"),
    (r"\bruntime budget\b", "legacy agent runtime budget field remains"),
    (r"\bdisallowedTools\b", "legacy agent tool blacklist field remains"),
    (r"\.codex/agents/[^`\s]+\.md", "legacy Markdown agent path remains"),
    (r"code\.codex\.com", "unofficial Codex documentation URL remains"),
    (r"platform\.codex\.com", "unofficial Codex documentation URL remains"),
    (r"13-opus-specifics", "legacy model topic filename remains"),
    (r"opus-4-6-guide", "legacy model source filename remains"),
    (r"\bfastMode\b", "unsupported fast mode config remains"),
    (r"\bfastModePerSessionOptIn\b", "unsupported fast mode config remains"),
    (r"GPT-5\.4 4\.6", "legacy model-version hybrid reference remains"),
    (r"\bGPT-5\.4\b", "legacy GPT-5.4 model reference remains"),
    (r"4\.7\+", "legacy model-version marker remains"),
    (r"\[4\.[678]", "legacy bracketed model-version marker remains"),
    (r"GPT-5\.5/4\.", "legacy mixed model-version target remains"),
    (r"openai-codex-docs\.md", "legacy source filename remains"),
    (r"openai-codex-best-practices\.md", "legacy source filename remains"),
    (r"openai-codex-subagents\.md", "legacy source filename remains"),
    (r"platform-agent-patterns\.md", "legacy source filename remains"),
    (r"openai-reasoning-guide\.md", "legacy source filename remains"),
    (r"agent-skills-best-practices\.md", "legacy source filename remains"),
    (r"cost/performance mode", "unsupported speed-mode prose remains"),
    (r"per-session cost/performance", "unsupported speed-mode config guidance remains"),
    (r"\bWebSearch\b", "legacy web-search tool name remains"),
    (r"\bWebFetch\b", "legacy web-fetch tool name remains"),
    (r"\bGlob/Grep\b", "legacy search tool shorthand remains"),
    (r"Glob -> Grep", "legacy search workflow shorthand remains"),
    (r"\bUse Glob\b", "legacy Glob tool instruction remains"),
    (r"\bUse Grep\b", "legacy Grep tool instruction remains"),
    (r"\bPrefer Glob\b", "legacy Glob tool instruction remains"),
    (r"\bPrefer Grep\b", "legacy Grep tool instruction remains"),
    (r"\bNo Bash\b", "legacy Bash tool wording remains"),
    (r"\bBash access\b", "legacy Bash access wording remains"),
    (r"\bFull tool access\b", "legacy tool access wording remains"),
    (r"\bRead/Write/Edit\b", "legacy file tool bundle remains"),
    (r"\bWrite/Edit\b", "legacy write/edit tool bundle remains"),
    (r"Read\(\./", "legacy Read(...) permission syntax remains"),
    (r"Edit\(\./", "legacy Edit(...) permission syntax remains"),
    (r"Write\(\./", "legacy Write(...) permission syntax remains"),
    (r"Bash\(", "legacy Bash(...) permission syntax remains"),
    (r'"permissions"\s*:', "legacy JSON permissions block remains"),
    (r"permissions\.allow", "legacy JSON permissions field remains"),
    (r"\ballow lists?\b", "legacy permission allow-list wording remains"),
    (r"\ballowed commands\b", "legacy command allow-list wording remains"),
]

REQUIRED_PATHS = [
    "AGENTS.md",
    ".codex/config.toml",
    ".codex/agents/intake-interviewer.toml",
    ".codex/agents/environment-architect.toml",
    ".codex/agents/component-generator.toml",
    ".codex/agents/environment-validator.toml",
    ".codex/agents/upgrade-analyzer.toml",
    ".agents/skills/create/SKILL.md",
    ".agents/skills/validate-environment/SKILL.md",
    ".agents/skills/upgrade-environment/SKILL.md",
    ".agents/skills/update/SKILL.md",
    "Docs/Environment/MANIFEST.md",
    "Docs/Templates/Core/agents-md.md",
    "Docs/Templates/Core/codex-config-toml.md",
]

FORBIDDEN_PATHS = [
    "CLAUDE.md",
    ".claude",
    ".claudeignore",
    "Docs/Templates/Core/claude-md.md",
    "Docs/Templates/Core/parent-claude-md.md",
    "Docs/Templates/Core/settings-json.md",
    "Docs/AgentGuidelines/Topics/13-opus-specifics.md",
]

REQUIRED_CONCEPTS = {
    "AGENTS.md": ["README.md", "AGENTS.md", "Docs/OVERVIEW.md"],
    ".codex/config.toml": ["README.md", "AGENTS.md", "Docs/OVERVIEW.md"],
    ".agents/skills": ["README.md", "AGENTS.md", "Docs/OVERVIEW.md"],
    "gpt-5.5": ["README.md", "AGENTS.md", "Docs/OVERVIEW.md"],
    "model_reasoning_effort": [".codex/config.toml", "Docs/OVERVIEW.md"],
    "MCP": ["README.md", "Docs/OVERVIEW.md"],
    "subagents": ["README.md", "Docs/OVERVIEW.md"],
    "OpenAI": ["README.md", "SECURITY.md", "Docs/OVERVIEW.md"],
}

OFFICIAL_DOC_URLS = [
    "https://developers.openai.com/codex/concepts/customization",
    "https://developers.openai.com/codex/guides/agents-md",
    "https://developers.openai.com/codex/config-reference",
    "https://developers.openai.com/codex/subagents",
    "https://developers.openai.com/api/docs/guides/reasoning",
]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_paths(root: Path) -> list[dict]:
    failures = []
    for required in REQUIRED_PATHS:
        if not (root / required).exists():
            failures.append(
                {
                    "check": "required_path",
                    "path": required,
                    "message": f"Missing required Codex path: {required}",
                }
            )
    for forbidden in FORBIDDEN_PATHS:
        if (root / forbidden).exists():
            failures.append(
                {
                    "check": "forbidden_path",
                    "path": forbidden,
                    "message": f"Forbidden Claude path still exists: {forbidden}",
                }
            )
    return failures


def check_forbidden_text(root: Path) -> list[dict]:
    failures = []
    compiled = [(re.compile(pattern), message) for pattern, message in FORBIDDEN_PATTERNS]
    for path in iter_text_files(root):
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern, message in compiled:
                if pattern.search(line):
                    failures.append(
                        {
                            "check": "forbidden_text",
                            "path": rel(path, root),
                            "line": line_no,
                            "message": message,
                            "text": line.strip()[:220],
                        }
                    )
    return failures


def check_required_concepts(root: Path) -> list[dict]:
    failures = []
    for concept, candidate_paths in REQUIRED_CONCEPTS.items():
        found = False
        searched = []
        for candidate in candidate_paths:
            path = root / candidate
            if path.exists() and path.is_file():
                searched.append(candidate)
                if concept in read_text(path):
                    found = True
                    break
        if not found:
            failures.append(
                {
                    "check": "required_concept",
                    "concept": concept,
                    "searched": searched or candidate_paths,
                    "message": f"Missing required Codex/OpenAI concept: {concept}",
                }
            )
    return failures


def check_official_sources(root: Path) -> list[dict]:
    failures = []
    docs_text = []
    for path in iter_text_files(root):
        relative = rel(path, root)
        if relative.startswith("Docs/") or relative in {"README.md", "CONTRIBUTING.md"}:
            docs_text.append(read_text(path))
    haystack = "\n".join(docs_text)
    for url in OFFICIAL_DOC_URLS:
        if url not in haystack:
            failures.append(
                {
                    "check": "official_source",
                    "url": url,
                    "message": f"Missing official OpenAI source citation: {url}",
                }
            )
    return failures


def check_toml_contracts(root: Path) -> list[dict]:
    failures = []
    config_path = root / ".codex/config.toml"
    try:
        config = tomllib.loads(read_text(config_path))
    except Exception as exc:
        failures.append(
            {
                "check": "codex_config_toml",
                "path": ".codex/config.toml",
                "message": f"Invalid Codex TOML: {exc}",
            }
        )
        return failures

    if config.get("model") != "gpt-5.5":
        failures.append(
            {
                "check": "codex_config_model",
                "path": ".codex/config.toml",
                "message": "Project config must pin model = \"gpt-5.5\".",
            }
        )
    if "model_reasoning_effort" not in config:
        failures.append(
            {
                "check": "codex_config_reasoning",
                "path": ".codex/config.toml",
                "message": "Project config must set model_reasoning_effort.",
            }
        )
    if "sandbox_mode" in config and "default_permissions" in config:
        failures.append(
            {
                "check": "codex_config_permissions",
                "path": ".codex/config.toml",
                "message": "Do not combine top-level sandbox_mode with default_permissions.",
            }
        )
    default_permissions = config.get("default_permissions")
    if not default_permissions:
        failures.append(
            {
                "check": "codex_config_permissions",
                "path": ".codex/config.toml",
                "message": "Project config must set top-level default_permissions.",
            }
        )
    elif default_permissions not in {
        ":read-only",
        ":workspace",
        ":danger-full-access",
    } and default_permissions not in config.get("permissions", {}):
        failures.append(
            {
                "check": "codex_config_permissions",
                "path": ".codex/config.toml",
                "message": f"default_permissions references missing profile: {default_permissions}",
            }
        )

    def find_nested_default_permissions(value, path=()):
        nested = []
        if isinstance(value, dict):
            for key, child in value.items():
                next_path = (*path, key)
                if key == "default_permissions" and path:
                    nested.append(".".join(next_path))
                nested.extend(find_nested_default_permissions(child, next_path))
        return nested

    for nested_path in find_nested_default_permissions(config):
        failures.append(
            {
                "check": "codex_config_permissions",
                "path": ".codex/config.toml",
                "message": f"default_permissions must be top-level, not nested at {nested_path}.",
            }
        )

    required_agent_fields = {
        "name",
        "description",
        "developer_instructions",
        "model",
        "model_reasoning_effort",
        "sandbox_mode",
    }
    for agent_path in sorted((root / ".codex/agents").glob("*.toml")):
        relative = rel(agent_path, root)
        try:
            agent = tomllib.loads(read_text(agent_path))
        except Exception as exc:
            failures.append(
                {
                    "check": "agent_toml",
                    "path": relative,
                    "message": f"Invalid Codex subagent TOML: {exc}",
                }
            )
            continue
        missing = sorted(required_agent_fields - set(agent))
        if missing:
            failures.append(
                {
                    "check": "agent_schema",
                    "path": relative,
                    "message": f"Missing Codex subagent fields: {', '.join(missing)}",
                }
            )
        if agent.get("model") != "gpt-5.5":
            failures.append(
                {
                    "check": "agent_model",
                    "path": relative,
                    "message": "Codex subagent must use model = \"gpt-5.5\" unless the port contract is updated.",
                }
            )
    return failures


def check_embedded_toml_blocks(root: Path) -> list[dict]:
    failures = []
    fence_pattern = re.compile(
        r"^(?P<fence>`{3,})toml\s*\n(?P<body>.*?)(?m:^)(?P=fence)\s*$",
        re.MULTILINE | re.DOTALL,
    )
    for path in sorted((root / "Docs/Templates/Agents").glob("*.md")):
        relative = rel(path, root)
        text = read_text(path)
        blocks = list(fence_pattern.finditer(text))
        if not blocks:
            failures.append(
                {
                    "check": "embedded_agent_toml",
                    "path": relative,
                    "message": "Agent template must include a TOML code block.",
                }
            )
            continue
        for index, block in enumerate(blocks, 1):
            try:
                tomllib.loads(block.group("body"))
            except Exception as exc:
                failures.append(
                    {
                        "check": "embedded_agent_toml",
                        "path": relative,
                        "message": f"Invalid embedded TOML block {index}: {exc}",
                    }
                )
    return failures


def collect_failures(root: Path) -> list[dict]:
    failures = []
    failures.extend(check_paths(root))
    failures.extend(check_forbidden_text(root))
    failures.extend(check_required_concepts(root))
    failures.extend(check_official_sources(root))
    failures.extend(check_toml_contracts(root))
    failures.extend(check_embedded_toml_blocks(root))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--max-failures", type=int, default=80)
    args = parser.parse_args()

    root = Path.cwd()
    failures = collect_failures(root)

    result = {
        "status": "pass" if not failures else "fail",
        "failure_count": len(failures),
        "failures": failures[: args.max_failures],
        "truncated": len(failures) > args.max_failures,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Codex port eval: {result['status'].upper()} ({len(failures)} failures)")
        for failure in result["failures"]:
            loc = failure.get("path", "<repo>")
            if "line" in failure:
                loc = f"{loc}:{failure['line']}"
            print(f"- [{failure['check']}] {loc}: {failure['message']}")
        if result["truncated"]:
            print(f"... {len(failures) - args.max_failures} more failures omitted")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
