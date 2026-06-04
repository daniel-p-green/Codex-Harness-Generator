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
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support for the Homebrew pytest shim.
    import tomli as tomllib


TEXT_SUFFIXES = {
    ".bash",
    ".cjs",
    ".fish",
    ".js",
    ".jsx",
    ".md",
    ".mjs",
    ".json",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
    ".txt",
    ".zsh",
}

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
SKIP_FORBIDDEN_TEXT_PATHS = {
    "scripts/eval_codex_port.py",
    "scripts/eval_generated_harness.py",
    "tests/test_eval_codex_port.py",
    "tests/test_generated_harness_contract.py",
}
REASONING_EFFORT_VALUES = {"minimal", "low", "medium", "high", "xhigh"}
MODEL_VERBOSITY_VALUES = {"low", "medium", "high"}
APPROVAL_POLICY_VALUES = {"untrusted", "on-request", "never"}
SANDBOX_MODE_VALUES = {"read-only", "workspace-write", "danger-full-access"}
BUILT_IN_PERMISSION_PROFILES = {":read-only", ":workspace", ":danger-full-access"}
PROJECT_LOCAL_IGNORED_KEYS = {
    "openai_base_url",
    "chatgpt_base_url",
    "apps_mcp_product_sku",
    "model_provider",
    "model_providers",
    "notify",
    "profile",
    "profiles",
    "experimental_realtime_ws_base_url",
    "otel",
}

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
    (r"\.codex/skills", "Codex skills must live under .agents/skills"),
    (r"\.codexignore", "unsupported legacy ignore file remains"),
    (r"settings-json", "legacy settings-json check name remains"),
    (r"\.codex/config\.toml[^.\n]*(valid|invalid|contains invalid) JSON", "Codex TOML described as JSON"),
    (r"valid JSON[^.\n]*\.codex/config\.toml", "Codex TOML described as JSON"),
    (r"\bYAML frontmatter\b", "legacy agent YAML schema remains"),
    (r"\bagent YAML\b", "legacy agent YAML schema remains"),
    (r"\bagent templates? with full frontmatter\b", "legacy agent frontmatter schema remains"),
    (r"\bagent frontmatter\b", "legacy agent frontmatter schema remains"),
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
    (r"\bpermission JSON\b", "legacy JSON permission schema remains"),
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
    "https://developers.openai.com/codex/permissions",
    "https://developers.openai.com/codex/skills",
    "https://developers.openai.com/api/docs/guides/reasoning",
]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_text_candidate(path: Path) -> bool:
    if path.suffix in TEXT_SUFFIXES:
        return True
    if path.suffix:
        return False
    try:
        return path.read_bytes()[:2] == b"#!"
    except OSError:
        return False


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and is_text_candidate(path):
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
        relative = rel(path, root)
        if relative in SKIP_FORBIDDEN_TEXT_PATHS:
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern, message in compiled:
                if pattern.search(line):
                    failures.append(
                        {
                            "check": "forbidden_text",
                            "path": relative,
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


def parse_skill_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return {}


def check_skill_contracts(root: Path) -> list[dict]:
    failures = []
    skills_root = root / ".agents/skills"
    if not skills_root.exists():
        return failures

    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        relative = rel(skill_path, root)
        metadata = parse_skill_metadata(read_text(skill_path))
        name = metadata.get("name")
        description = metadata.get("description", "")

        if not name:
            failures.append(
                {
                    "check": "skill_metadata",
                    "path": relative,
                    "message": "Skill must declare name in its SKILL.md metadata block.",
                }
            )
        elif name != skill_path.parent.name:
            failures.append(
                {
                    "check": "skill_metadata",
                    "path": relative,
                    "message": f"Skill name must match directory name: expected {skill_path.parent.name}, found {name}.",
                }
            )

        if not description:
            failures.append(
                {
                    "check": "skill_metadata",
                    "path": relative,
                    "message": "Skill must declare description in its SKILL.md metadata block.",
                }
            )
        elif len(description) < 80 or "Use when" not in description:
            failures.append(
                {
                    "check": "skill_metadata",
                    "path": relative,
                    "message": "Skill description should state what it does and include explicit trigger guidance with 'Use when'.",
                }
            )

    return failures


def has_broad_web_access(config: dict) -> bool:
    default_permissions = config.get("default_permissions")
    if not default_permissions or default_permissions in BUILT_IN_PERMISSION_PROFILES:
        return default_permissions == ":danger-full-access"

    permissions = config.get("permissions", {})
    profile = permissions.get(default_permissions, {})
    domains = profile.get("network", {}).get("domains", {})
    return domains.get("*") == "allow"


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

    ignored_keys = sorted(PROJECT_LOCAL_IGNORED_KEYS & set(config))
    for key in ignored_keys:
        failures.append(
            {
                "check": "codex_config_scope",
                "path": ".codex/config.toml",
                "message": f"Project-local Codex config cannot override machine-local key: {key}",
            }
        )

    if config.get("model") != "gpt-5.5":
        failures.append(
            {
                "check": "codex_config_model",
                "path": ".codex/config.toml",
                "message": "Project config must pin model = \"gpt-5.5\".",
            }
        )
    effort = config.get("model_reasoning_effort")
    if effort is None:
        failures.append(
            {
                "check": "codex_config_reasoning",
                "path": ".codex/config.toml",
                "message": "Project config must set model_reasoning_effort.",
            }
        )
    elif effort not in REASONING_EFFORT_VALUES:
        failures.append(
            {
                "check": "codex_config_reasoning",
                "path": ".codex/config.toml",
                "message": f"Invalid model_reasoning_effort: {effort}",
            }
        )
    verbosity = config.get("model_verbosity")
    if verbosity is not None and verbosity not in MODEL_VERBOSITY_VALUES:
        failures.append(
            {
                "check": "codex_config_model_verbosity",
                "path": ".codex/config.toml",
                "message": f"Invalid model_verbosity: {verbosity}",
            }
        )
    approval_policy = config.get("approval_policy")
    if isinstance(approval_policy, str):
        if approval_policy not in APPROVAL_POLICY_VALUES:
            failures.append(
                {
                    "check": "codex_config_approval_policy",
                    "path": ".codex/config.toml",
                    "message": f"Invalid approval_policy: {approval_policy}",
                }
            )
    elif isinstance(approval_policy, dict):
        if not isinstance(approval_policy.get("granular"), dict):
            failures.append(
                {
                    "check": "codex_config_approval_policy",
                    "path": ".codex/config.toml",
                    "message": "Granular approval_policy must contain a granular table.",
                }
            )
    elif approval_policy is not None:
        failures.append(
            {
                "check": "codex_config_approval_policy",
                "path": ".codex/config.toml",
                "message": "approval_policy must be a string or granular policy table.",
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

    permissions = config.get("permissions", {})
    for profile_name, profile in permissions.items():
        filesystem = profile.get("filesystem", {}) if isinstance(profile, dict) else {}
        if profile_name not in BUILT_IN_PERMISSION_PROFILES and isinstance(profile, dict) and not profile.get("extends"):
            failures.append(
                {
                    "check": "codex_config_permissions",
                    "path": ".codex/config.toml",
                    "message": f"Permission profile {profile_name} must declare extends for Codex portability.",
                }
            )
        workspace_rules = filesystem.get(":workspace_roots", {})
        for pattern, access in workspace_rules.items():
            if access not in {"read", "write", "deny"}:
                failures.append(
                    {
                        "check": "codex_config_permissions",
                        "path": ".codex/config.toml",
                        "message": f"Permission profile {profile_name} filesystem rule {pattern} has invalid access value: {access}",
                    }
                )
        deny_patterns = [
            pattern
            for pattern, access in workspace_rules.items()
            if isinstance(pattern, str) and access == "deny"
        ]
        if any("**" in pattern for pattern in deny_patterns) and "glob_scan_max_depth" not in filesystem:
            failures.append(
                {
                    "check": "codex_config_permissions",
                    "path": ".codex/config.toml",
                    "message": f"Permission profile {profile_name} uses recursive deny globs without filesystem.glob_scan_max_depth.",
                }
            )
        joined_patterns = "\n".join(deny_patterns).lower()
        for sensitive_token in [".env", "secret", "token", "credential", ".pem", ".key"]:
            if sensitive_token not in joined_patterns:
                failures.append(
                    {
                        "check": "codex_config_permissions",
                        "path": ".codex/config.toml",
                        "message": f"Permission profile {profile_name} should deny sensitive pattern containing {sensitive_token}.",
                    }
                )

    features = config.get("features", {})
    if (
        isinstance(features, dict)
        and features.get("hooks") is True
        and "hooks" not in config
        and not (root / ".codex/hooks.json").exists()
    ):
        failures.append(
            {
                "check": "codex_config_hooks",
                "path": ".codex/config.toml",
                "message": "features.hooks is true but no hooks.json or inline [hooks] config exists.",
            }
        )
    hooks = config.get("hooks", {})
    if isinstance(hooks, dict):
        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                failures.append(
                    {
                        "check": "codex_config_hooks",
                        "path": ".codex/config.toml",
                        "message": f"hooks.{event_name} must be an array of hook command objects.",
                    }
                )
                continue
            for index, hook in enumerate(event_hooks, 1):
                if not isinstance(hook, dict) or not isinstance(hook.get("command"), str):
                    failures.append(
                        {
                            "check": "codex_config_hooks",
                            "path": ".codex/config.toml",
                            "message": f"hooks.{event_name} entry {index} must include a command string.",
                        }
                    )

    skills_config = config.get("skills", {}).get("config", [])
    if skills_config and not isinstance(skills_config, list):
        failures.append(
            {
                "check": "codex_config_skills",
                "path": ".codex/config.toml",
                "message": "skills.config must be an array of skill config objects.",
            }
        )
        skills_config = []
    for index, skill_config in enumerate(skills_config, 1):
        if not isinstance(skill_config, dict):
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config entry {index} must be an object.",
                }
            )
            continue
        skill_path = skill_config.get("path")
        enabled = skill_config.get("enabled")
        if not isinstance(skill_path, str):
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config entry {index} must include a string path.",
                }
            )
            continue
        if enabled is None:
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config entry {index} must include enabled.",
                }
            )
        elif not isinstance(enabled, bool):
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config entry {index} enabled must be boolean when present.",
                }
            )
        resolved_skill_path = (config_path.parent / skill_path).resolve()
        if not resolved_skill_path.exists():
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config path does not exist: {skill_path}",
                }
            )
        elif not (resolved_skill_path / "SKILL.md").is_file():
            failures.append(
                {
                    "check": "codex_config_skills",
                    "path": ".codex/config.toml",
                    "message": f"skills.config path lacks SKILL.md: {skill_path}",
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
    agents_section = config.get("agents", {})
    registry_agent_paths = {}
    for agent_key, agent_config in agents_section.items():
        if not isinstance(agent_config, dict):
            continue
        config_file = agent_config.get("config_file")
        if not isinstance(config_file, str):
            failures.append(
                {
                    "check": "agent_registry",
                    "path": ".codex/config.toml",
                    "message": f"Agent registry entry {agent_key} must include config_file.",
                }
            )
            continue
        resolved_agent_path = (config_path.parent / config_file).resolve()
        registry_agent_paths[resolved_agent_path] = agent_key
        if not resolved_agent_path.is_file():
            failures.append(
                {
                    "check": "agent_registry",
                    "path": ".codex/config.toml",
                    "message": f"Agent registry config_file does not exist for {agent_key}: {config_file}",
                }
            )

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
        agent_name = agent.get("name")
        if agent_name and agent_name != agent_path.stem:
            failures.append(
                {
                    "check": "agent_schema",
                    "path": relative,
                    "message": f"Agent name must match filename stem: expected {agent_path.stem}, found {agent_name}.",
                }
            )
        registry_key = registry_agent_paths.get(agent_path.resolve())
        if registry_key and agent_name and agent_name != registry_key:
            failures.append(
                {
                    "check": "agent_registry",
                    "path": ".codex/config.toml",
                    "message": f"Agent registry key {registry_key} does not match agent name {agent_name}.",
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
        agent_effort = agent.get("model_reasoning_effort")
        if agent_effort and agent_effort not in REASONING_EFFORT_VALUES:
            failures.append(
                {
                    "check": "agent_schema",
                    "path": relative,
                    "message": f"Invalid agent model_reasoning_effort: {agent_effort}",
                }
            )
        sandbox_mode = agent.get("sandbox_mode")
        if sandbox_mode and sandbox_mode not in SANDBOX_MODE_VALUES:
            failures.append(
                {
                    "check": "agent_schema",
                    "path": relative,
                    "message": f"Invalid agent sandbox_mode: {sandbox_mode}",
                }
            )
        instructions = agent.get("developer_instructions", "")
        if "Search the web" in instructions and not has_broad_web_access(config):
            failures.append(
                {
                    "check": "agent_network_policy",
                    "path": relative,
                    "message": "Agent asks to search the web, but the default permission profile does not allow broad web access.",
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
            body = block.group("body")
            try:
                parsed = tomllib.loads(body)
            except Exception as exc:
                failures.append(
                    {
                        "check": "embedded_agent_toml",
                        "path": relative,
                        "message": f"Invalid embedded TOML block {index}: {exc}",
                    }
                )
                continue
            missing = sorted(
                {
                    "name",
                    "description",
                    "developer_instructions",
                    "model",
                    "model_reasoning_effort",
                    "sandbox_mode",
                }
                - set(parsed)
            )
            if missing:
                failures.append(
                    {
                        "check": "embedded_agent_toml",
                        "path": relative,
                        "message": f"Embedded agent TOML block {index} is missing required fields: {', '.join(missing)}",
                    }
                )
            effort = parsed.get("model_reasoning_effort")
            if effort and effort not in REASONING_EFFORT_VALUES:
                failures.append(
                    {
                        "check": "embedded_agent_toml",
                        "path": relative,
                        "message": f"Embedded agent TOML block {index} has invalid model_reasoning_effort: {effort}",
                    }
                )
    return failures


def collect_failures(root: Path) -> list[dict]:
    failures = []
    failures.extend(check_paths(root))
    failures.extend(check_forbidden_text(root))
    failures.extend(check_required_concepts(root))
    failures.extend(check_official_sources(root))
    failures.extend(check_skill_contracts(root))
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
