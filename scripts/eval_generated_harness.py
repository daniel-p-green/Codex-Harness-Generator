#!/usr/bin/env python3
"""Evaluate a generated Codex harness directory.

This checks the artifact this project promises to create: a runnable Codex
harness with AGENTS.md, config, rules, agents, skills, docs, and safety guards.
It is intentionally stricter than a smoke test and more product-oriented than
the repo port evaluator.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support for the Homebrew pytest shim.
    import tomli as tomllib


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

TEXT_SUFFIXES = {
    ".bash",
    ".cjs",
    ".fish",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
    ".zsh",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".eggs", "build", "dist"}

FORBIDDEN_TEXT = [
    (r"\bClaude\b", "Claude naming remains"),
    (r"\bAnthropic\b", "Anthropic platform reference remains"),
    (r"\bCLAUDE\.md\b", "legacy instruction filename remains"),
    (r"(^|/)\.claude(/|$)", "legacy runtime path remains"),
    (r"\bsettings\.json\b", "legacy settings file remains"),
    (r"\bWebSearch\b", "legacy web-search tool name remains"),
    (r"\bWebFetch\b", "legacy web-fetch tool name remains"),
    (r"\.codex/skills", "skills must live under .agents/skills"),
    (r"\bagent YAML\b", "legacy agent YAML schema remains"),
    (r"\bagent frontmatter\b", "legacy agent frontmatter schema remains"),
    (r"\bpermission JSON\b", "legacy JSON permission schema remains"),
]

CATEGORY_WEIGHTS = {
    "correctness": 25,
    "codex_compatibility": 25,
    "safety_privacy": 20,
    "user_clarity": 10,
    "maintainability": 10,
    "source_alignment": 10,
}

HIGH_RISK_DOMAIN_REQUIREMENTS = [
    {
        "domain": "security audit",
        "triggers": ["security audit", "vulnerability", "exploit", "penetration test", "threat model"],
        "requirements": [
            ("secret handling", ["secret", "token", "credential", "private key"]),
            ("authorization boundary", ["authorization", "permission", "approval", "active testing"]),
            ("destructive action boundary", ["destructive", "exploit", "active testing"]),
        ],
    },
    {
        "domain": "legal research",
        "triggers": ["legal research", "legal review", "contract review", "jurisdiction"],
        "requirements": [
            ("jurisdiction and limits", ["jurisdiction", "not legal advice", "attorney", "lawyer"]),
            ("source citation", ["source", "citation", "cite", "statute", "case"]),
            ("uncertainty handling", ["uncertain", "assumption", "limit", "verify"]),
        ],
    },
    {
        "domain": "financial analysis",
        "triggers": ["financial modeling", "investment", "valuation", "financial forecast", "portfolio analysis"],
        "requirements": [
            ("advice boundary", ["not financial advice", "not investment advice", "decision support"]),
            ("assumption disclosure", ["assumption", "scenario", "sensitivity", "limit"]),
            ("risk disclosure", ["risk", "uncertainty", "downside", "caveat"]),
        ],
    },
    {
        "domain": "hiring",
        "triggers": ["hiring pipeline", "candidate evaluation", "interview process", "recruiting", "applicant tracking"],
        "requirements": [
            ("bias mitigation", ["bias", "discrimination", "fairness", "protected class"]),
            ("structured criteria", ["criteria", "rubric", "scorecard", "job-related"]),
            ("candidate privacy", ["privacy", "candidate data", "personal data", "pii"]),
        ],
    },
    {
        "domain": "customer support",
        "triggers": ["customer support", "support ticket", "user complaint"],
        "requirements": [
            ("customer privacy", ["privacy", "personal data", "pii", "do not expose"]),
            ("escalation path", ["escalate", "escalation", "handoff", "human review"]),
            ("claim discipline", ["source", "verify", "do not promise", "do not overpromise"]),
        ],
    },
]


@dataclass(frozen=True)
class Finding:
    check: str
    category: str
    severity: str
    path: str
    message: str

    def to_dict(self) -> dict:
        return {
            "check": self.check,
            "category": self.category,
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def parse_skill_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return {}


def add(
    findings: list[Finding],
    check: str,
    category: str,
    severity: str,
    path: str,
    message: str,
) -> None:
    findings.append(Finding(check, category, severity, path, message))


def load_toml(root: Path, path: str, findings: list[Finding]) -> dict | None:
    target = root / path
    try:
        return tomllib.loads(read_text(target))
    except Exception as exc:
        add(findings, "toml_parse", "codex_compatibility", "fail", path, f"Invalid TOML: {exc}")
        return None


def has_broad_web_access(config: dict) -> bool:
    default_permissions = config.get("default_permissions")
    if default_permissions == ":danger-full-access":
        return True
    if not default_permissions or default_permissions in BUILT_IN_PERMISSION_PROFILES:
        return False

    profile = config.get("permissions", {}).get(default_permissions, {})
    domains = profile.get("network", {}).get("domains", {})
    return domains.get("*") == "allow"


def check_required_paths(root: Path, findings: list[Finding]) -> None:
    required_paths = [
        "AGENTS.md",
        ".codex/config.toml",
        ".codex/rules",
        ".agents/skills",
        "Docs/GETTING_STARTED.md",
        "Docs/Environment/MANIFEST.md",
        "Docs/Environment/GENESIS.md",
        "Docs/Environment/ARCHITECTURE.md",
        "Docs/Environment/ASSUMPTIONS.md",
        "Docs/Environment/VALIDATION_REPORT.md",
        "Docs/Environment/SOURCE_MAP.md",
    ]
    for required in required_paths:
        if not (root / required).exists():
            add(findings, "required_path", "correctness", "fail", required, "Required generated harness path is missing.")

    forbidden_paths = ["CLAUDE.md", ".claude", ".codex/skills", ".codexignore"]
    for forbidden in forbidden_paths:
        if (root / forbidden).exists():
            add(findings, "forbidden_path", "codex_compatibility", "fail", forbidden, "Forbidden legacy or unsupported path exists.")


def check_agents_md(root: Path, findings: list[Finding]) -> None:
    path = root / "AGENTS.md"
    if not path.exists():
        return

    text = read_text(path)
    size = len(text.encode("utf-8"))
    if size > 32_768:
        add(findings, "agents_md_size", "maintainability", "fail", "AGENTS.md", f"AGENTS.md is {size} bytes; keep under the default 32 KiB project-doc cap.")

    lowered = text.lower()
    for required_phrase in ["verify", "test", "do not", "security"]:
        if required_phrase not in lowered:
            add(findings, "agents_md_guidance", "user_clarity", "warn", "AGENTS.md", f"AGENTS.md should include guidance containing '{required_phrase}'.")


def check_forbidden_text(root: Path, findings: list[Finding]) -> None:
    compiled = [(re.compile(pattern), message) for pattern, message in FORBIDDEN_TEXT]
    for path in iter_text_files(root):
        relative = rel(path, root)
        for line_no, line in enumerate(read_text(path).splitlines(), 1):
            for pattern, message in compiled:
                if pattern.search(line):
                    add(findings, "forbidden_text", "codex_compatibility", "fail", f"{relative}:{line_no}", message)


def check_config(root: Path, findings: list[Finding]) -> dict:
    config = load_toml(root, ".codex/config.toml", findings)
    if not config:
        return {}

    ignored_keys = sorted(PROJECT_LOCAL_IGNORED_KEYS & set(config))
    for key in ignored_keys:
        add(findings, "config_scope", "codex_compatibility", "fail", ".codex/config.toml", f"Project-local config cannot override machine-local key: {key}")

    if "sandbox_mode" in config and "default_permissions" in config:
        add(findings, "config_permissions", "codex_compatibility", "fail", ".codex/config.toml", "Do not combine top-level sandbox_mode with default_permissions.")

    model = config.get("model")
    if not model:
        add(findings, "config_model", "codex_compatibility", "fail", ".codex/config.toml", "Generated config must set model.")

    effort = config.get("model_reasoning_effort")
    if effort not in REASONING_EFFORT_VALUES:
        add(findings, "config_reasoning", "codex_compatibility", "fail", ".codex/config.toml", f"Invalid or missing model_reasoning_effort: {effort}")

    verbosity = config.get("model_verbosity")
    if verbosity is not None and verbosity not in MODEL_VERBOSITY_VALUES:
        add(findings, "config_model_verbosity", "codex_compatibility", "fail", ".codex/config.toml", f"Invalid model_verbosity: {verbosity}")

    approval_policy = config.get("approval_policy")
    if isinstance(approval_policy, str) and approval_policy not in APPROVAL_POLICY_VALUES:
        add(findings, "config_approval_policy", "codex_compatibility", "fail", ".codex/config.toml", f"Invalid approval_policy: {approval_policy}")
    elif isinstance(approval_policy, dict) and not isinstance(approval_policy.get("granular"), dict):
        add(findings, "config_approval_policy", "codex_compatibility", "fail", ".codex/config.toml", "Granular approval_policy must contain a granular table.")
    elif approval_policy is not None and not isinstance(approval_policy, (str, dict)):
        add(findings, "config_approval_policy", "codex_compatibility", "fail", ".codex/config.toml", "approval_policy must be a string or granular policy table.")

    default_permissions = config.get("default_permissions")
    permissions = config.get("permissions", {})
    if not default_permissions:
        add(findings, "config_permissions", "safety_privacy", "fail", ".codex/config.toml", "Generated config must set default_permissions.")
    elif default_permissions not in BUILT_IN_PERMISSION_PROFILES and default_permissions not in permissions:
        add(findings, "config_permissions", "safety_privacy", "fail", ".codex/config.toml", f"default_permissions references missing profile: {default_permissions}")

    for profile_name, profile in permissions.items():
        filesystem = profile.get("filesystem", {}) if isinstance(profile, dict) else {}
        if profile_name not in BUILT_IN_PERMISSION_PROFILES and isinstance(profile, dict) and not profile.get("extends"):
            add(findings, "config_permissions", "safety_privacy", "fail", ".codex/config.toml", f"Permission profile {profile_name} must declare extends for Codex portability.")
        workspace_rules = filesystem.get(":workspace_roots", {})
        for pattern, access in workspace_rules.items():
            if access not in {"read", "write", "deny"}:
                add(findings, "permission_values", "codex_compatibility", "fail", ".codex/config.toml", f"Permission profile {profile_name} filesystem rule {pattern} has invalid access value: {access}")
        deny_patterns = [
            pattern
            for pattern, access in workspace_rules.items()
            if isinstance(pattern, str) and access == "deny"
        ]
        if any("**" in pattern for pattern in deny_patterns) and "glob_scan_max_depth" not in filesystem:
            add(findings, "permission_globs", "safety_privacy", "fail", ".codex/config.toml", f"Permission profile {profile_name} uses recursive deny globs without filesystem.glob_scan_max_depth.")

        joined = "\n".join(deny_patterns).lower()
        for token in [".env", "secret", "token", "credential", ".pem", ".key"]:
            if token not in joined:
                add(findings, "permission_sensitive_denies", "safety_privacy", "fail", ".codex/config.toml", f"Permission profile {profile_name} should deny sensitive pattern containing {token}.")

    features = config.get("features", {})
    if isinstance(features, dict) and features.get("hooks") is True and "hooks" not in config and not (root / ".codex/hooks.json").exists():
        add(findings, "hooks_config", "codex_compatibility", "fail", ".codex/config.toml", "features.hooks is true but no hooks.json or inline [hooks] config exists.")
    hooks = config.get("hooks", {})
    if isinstance(hooks, dict):
        for event_name, event_hooks in hooks.items():
            if not isinstance(event_hooks, list):
                add(findings, "hooks_config", "codex_compatibility", "fail", ".codex/config.toml", f"hooks.{event_name} must be an array of hook command objects.")
                continue
            for index, hook in enumerate(event_hooks, 1):
                if not isinstance(hook, dict) or not isinstance(hook.get("command"), str):
                    add(findings, "hooks_config", "codex_compatibility", "fail", ".codex/config.toml", f"hooks.{event_name} entry {index} must include a command string.")

    return config


def check_agent_contracts(root: Path, config: dict, findings: list[Finding]) -> None:
    agent_root = root / ".codex/agents"
    if not agent_root.exists():
        add(findings, "agent_presence", "correctness", "warn", ".codex/agents", "No custom agent directory found.")
        return

    agents_section = config.get("agents", {}) if config else {}
    registry_paths: dict[Path, str] = {}
    for key, value in agents_section.items():
        if not isinstance(value, dict):
            continue
        config_file = value.get("config_file")
        if not isinstance(config_file, str):
            add(findings, "agent_registry", "codex_compatibility", "fail", ".codex/config.toml", f"Agent registry entry {key} must include config_file.")
            continue
        resolved = (root / ".codex" / config_file).resolve()
        registry_paths[resolved] = key
        if not resolved.is_file():
            add(findings, "agent_registry", "codex_compatibility", "fail", ".codex/config.toml", f"Agent registry config_file does not exist for {key}: {config_file}")

    agent_files = sorted(agent_root.glob("*.toml"))
    if not agent_files:
        add(findings, "agent_presence", "correctness", "warn", ".codex/agents", "No custom agent TOML files found.")

    required = {"name", "description", "developer_instructions", "model", "model_reasoning_effort", "sandbox_mode"}
    for agent_file in agent_files:
        relative = rel(agent_file, root)
        agent = load_toml(root, relative, findings)
        if not agent:
            continue
        missing = sorted(required - set(agent))
        if missing:
            add(findings, "agent_schema", "codex_compatibility", "fail", relative, f"Missing required agent fields: {', '.join(missing)}")
        if agent.get("name") and agent["name"] != agent_file.stem:
            add(findings, "agent_schema", "codex_compatibility", "fail", relative, f"Agent name must match filename stem: {agent_file.stem}")
        registry_key = registry_paths.get(agent_file.resolve())
        if registry_key and agent.get("name") != registry_key:
            add(findings, "agent_registry", "codex_compatibility", "fail", ".codex/config.toml", f"Registry key {registry_key} does not match agent name {agent.get('name')}.")
        if agent.get("model_reasoning_effort") not in REASONING_EFFORT_VALUES:
            add(findings, "agent_schema", "codex_compatibility", "fail", relative, f"Invalid model_reasoning_effort: {agent.get('model_reasoning_effort')}")
        if agent.get("sandbox_mode") not in SANDBOX_MODE_VALUES:
            add(findings, "agent_schema", "codex_compatibility", "fail", relative, f"Invalid sandbox_mode: {agent.get('sandbox_mode')}")
        instructions = agent.get("developer_instructions", "")
        if "Search the web" in instructions and not has_broad_web_access(config):
            add(findings, "agent_network_policy", "safety_privacy", "fail", relative, "Agent asks to search the web, but default permissions do not allow broad web access.")


def check_skill_contracts(root: Path, config: dict, findings: list[Finding]) -> None:
    skills_root = root / ".agents/skills"
    if not skills_root.exists():
        return

    skill_files = sorted(skills_root.glob("*/SKILL.md"))
    if not skill_files:
        add(findings, "skill_presence", "correctness", "fail", ".agents/skills", "No SKILL.md files found.")

    for readme in sorted(skills_root.glob("*/README.md")):
        add(findings, "skill_readme", "maintainability", "fail", rel(readme, root), "Skill folders should use SKILL.md, not README.md.")

    for skill_file in skill_files:
        relative = rel(skill_file, root)
        metadata = parse_skill_metadata(read_text(skill_file))
        name = metadata.get("name")
        description = metadata.get("description", "")
        if not name:
            add(findings, "skill_metadata", "codex_compatibility", "fail", relative, "Skill must declare name in SKILL.md metadata.")
        elif name != skill_file.parent.name:
            add(findings, "skill_metadata", "codex_compatibility", "fail", relative, f"Skill name must match directory name: {skill_file.parent.name}")
        if not description:
            add(findings, "skill_metadata", "codex_compatibility", "fail", relative, "Skill must declare description in SKILL.md metadata.")
        elif len(description) < 80 or "Use when" not in description:
            add(findings, "skill_metadata", "user_clarity", "warn", relative, "Skill description should state what it does and include explicit 'Use when' trigger guidance.")

    skills_config = config.get("skills", {}).get("config", []) if config else []
    if skills_config and not isinstance(skills_config, list):
        add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", "skills.config must be an array.")
        return
    for index, skill_config in enumerate(skills_config, 1):
        if not isinstance(skill_config, dict):
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config entry {index} must be an object.")
            continue
        skill_path = skill_config.get("path")
        if not isinstance(skill_path, str):
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config entry {index} must include path.")
            continue
        if "enabled" not in skill_config:
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config entry {index} must include enabled.")
        elif not isinstance(skill_config.get("enabled"), bool):
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config entry {index} enabled must be boolean.")
        resolved = (root / ".codex" / skill_path).resolve()
        if not resolved.exists():
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config path does not exist: {skill_path}")
        elif not (resolved / "SKILL.md").is_file():
            add(findings, "skills_config", "codex_compatibility", "fail", ".codex/config.toml", f"skills.config path lacks SKILL.md: {skill_path}")


def check_rules(root: Path, findings: list[Finding]) -> None:
    rules_root = root / ".codex/rules"
    if not rules_root.exists():
        return
    text = "\n".join(read_text(path).lower() for path in sorted(rules_root.glob("*.md")))
    required_purposes = {
        "routing": ["route", "routing"],
        "autonomy": ["autonomy", "approval"],
        "context": ["context", "summarize"],
        "error handling": ["error", "fail"],
        "self-learning": ["self-learning", "retro"],
    }
    for purpose, keywords in required_purposes.items():
        if not any(keyword in text for keyword in keywords):
            add(findings, "rule_purpose", "correctness", "fail", ".codex/rules", f"Rules should include {purpose} guidance.")


def check_docs(root: Path, findings: list[Finding]) -> None:
    getting_started = root / "Docs/GETTING_STARTED.md"
    if getting_started.exists():
        text = read_text(getting_started).lower()
        for phrase in ["codex", "verify", "permission"]:
            if phrase not in text:
                add(findings, "getting_started", "user_clarity", "warn", "Docs/GETTING_STARTED.md", f"Getting started guide should mention {phrase}.")

    source_map = root / "Docs/Environment/SOURCE_MAP.md"
    if source_map.exists():
        text = read_text(source_map)
        for source in [
            "https://developers.openai.com/codex/config-reference",
            "https://developers.openai.com/codex/guides/agents-md",
            "https://developers.openai.com/codex/subagents",
            "https://developers.openai.com/codex/skills",
            "https://developers.openai.com/codex/permissions",
        ]:
            if source not in text:
                add(findings, "source_map", "source_alignment", "warn", "Docs/Environment/SOURCE_MAP.md", f"Source map should cite {source}.")

    assumptions = root / "Docs/Environment/ASSUMPTIONS.md"
    if assumptions.exists():
        text = read_text(assumptions).lower()
        for phrase in ["assumption", "limit", "verify"]:
            if phrase not in text:
                add(findings, "assumptions", "maintainability", "warn", "Docs/Environment/ASSUMPTIONS.md", f"Assumptions ledger should mention {phrase}.")


def check_manifest(root: Path, findings: list[Finding]) -> None:
    manifest = root / "Docs/Environment/MANIFEST.md"
    if not manifest.exists():
        return

    for line_no, line in enumerate(read_text(manifest).splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        entry = stripped[2:].strip().split(" #", 1)[0].strip("` ")
        if not entry or " " in entry:
            continue
        if not (root / entry).exists():
            add(
                findings,
                "manifest_reference",
                "correctness",
                "fail",
                f"Docs/Environment/MANIFEST.md:{line_no}",
                f"Manifest entry does not exist on disk: {entry}",
            )


def check_high_risk_domain_guardrails(root: Path, findings: list[Finding]) -> None:
    text_by_path = {
        rel(path, root): read_text(path).lower()
        for path in iter_text_files(root)
    }
    combined_text = "\n".join(text_by_path.values())
    if not combined_text:
        return

    for domain in HIGH_RISK_DOMAIN_REQUIREMENTS:
        if not any(trigger in combined_text for trigger in domain["triggers"]):
            continue
        for label, accepted_phrases in domain["requirements"]:
            if any(phrase in combined_text for phrase in accepted_phrases):
                continue
            add(
                findings,
                "domain_guardrails",
                "safety_privacy",
                "fail",
                "AGENTS.md",
                f"High-risk {domain['domain']} harness is missing explicit {label} guardrail.",
            )


def score_findings(findings: list[Finding]) -> tuple[int, dict[str, int]]:
    category_scores = dict(CATEGORY_WEIGHTS)
    for finding in findings:
        deduction = 12 if finding.severity == "fail" else 4
        category_scores[finding.category] = max(0, category_scores[finding.category] - deduction)
    total = sum(category_scores.values())
    return total, category_scores


def evaluate(root: Path) -> dict:
    root = root.resolve()
    findings: list[Finding] = []
    check_required_paths(root, findings)
    check_agents_md(root, findings)
    check_forbidden_text(root, findings)
    config = check_config(root, findings)
    check_agent_contracts(root, config, findings)
    check_skill_contracts(root, config, findings)
    check_rules(root, findings)
    check_docs(root, findings)
    check_manifest(root, findings)
    check_high_risk_domain_guardrails(root, findings)
    score, category_scores = score_findings(findings)
    fail_count = sum(1 for finding in findings if finding.severity == "fail")
    warn_count = sum(1 for finding in findings if finding.severity == "warn")
    return {
        "path": root.as_posix(),
        "status": "pass" if fail_count == 0 else "fail",
        "score": score,
        "category_scores": category_scores,
        "failure_count": fail_count,
        "warning_count": warn_count,
        "findings": [finding.to_dict() for finding in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Generated harness directory paths to evaluate")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--min-score", type=int, default=90, help="Minimum passing score when no failures are present")
    args = parser.parse_args()

    results = [evaluate(Path(path)) for path in args.paths]
    overall_status = "pass"
    for result in results:
        if result["status"] != "pass" or result["score"] < args.min_score:
            overall_status = "fail"

    payload = {"status": overall_status, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Generated harness eval: {overall_status.upper()}")
        for result in results:
            print(f"- {result['path']}: {result['status'].upper()} score={result['score']} failures={result['failure_count']} warnings={result['warning_count']}")
            for finding in result["findings"]:
                print(f"  - [{finding['severity']}/{finding['check']}] {finding['path']}: {finding['message']}")

    return 0 if overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
