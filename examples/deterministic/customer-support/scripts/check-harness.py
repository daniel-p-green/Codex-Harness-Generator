#!/usr/bin/env python3
"""Local smoke check for a generated Codex harness."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "AGENTS.md",
    ".codex/config.toml",
    ".codex/agents/reviewer.toml",
    ".codex/rules/core.md",
    ".agents/skills/health-check/SKILL.md",
    "Docs/GETTING_STARTED.md",
    "Docs/Environment/GENESIS.md",
    "Docs/Environment/ARCHITECTURE.md",
    "Docs/Environment/ASSUMPTIONS.md",
    "Docs/Environment/MANIFEST.md",
    "Docs/Environment/EVAL_PLAN.md",
    "Docs/Environment/SOURCE_MAP.md",
    "Docs/Environment/VALIDATION_REPORT.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_skill_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    metadata = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
    return metadata


def parse_config(text: str) -> dict:
    if tomllib is not None:
        return tomllib.loads(text)

    config: dict = {"agents": {}, "skills": {"config": []}}
    current_agent = None
    current_skill = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[agents.") and line.endswith("]"):
            current_agent = line[len("[agents.") : -1]
            current_skill = None
            config["agents"].setdefault(current_agent, {})
            continue
        if line == "[[skills.config]]":
            current_agent = None
            current_skill = {}
            config["skills"]["config"].append(current_skill)
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"')
        if current_agent and key == "config_file":
            config["agents"][current_agent]["config_file"] = value
        if current_skill is not None and key == "path":
            current_skill["path"] = value
    return config


def main() -> int:
    issues = []
    for required in REQUIRED_PATHS:
        if not (ROOT / required).exists():
            issues.append(f"missing required path: {required}")

    config = {}
    config_path = ROOT / ".codex/config.toml"
    if config_path.exists():
        try:
            config = parse_config(read_text(config_path))
        except Exception as exc:
            issues.append(f".codex/config.toml does not parse: {exc}")

    for name, entry in config.get("agents", {}).items():
        if not isinstance(entry, dict):
            continue
        config_file = entry.get("config_file")
        if not isinstance(config_file, str):
            issues.append(f"agent {name} has no config_file")
            continue
        agent_path = ROOT / ".codex" / config_file
        if not agent_path.exists():
            issues.append(f"agent {name} config_file missing: {config_file}")

    for index, entry in enumerate(config.get("skills", {}).get("config", []), 1):
        if not isinstance(entry, dict):
            issues.append(f"skills.config entry {index} is not an object")
            continue
        skill_path = entry.get("path")
        if not isinstance(skill_path, str):
            issues.append(f"skills.config entry {index} has no path")
            continue
        skill_md = ROOT / ".codex" / skill_path / "SKILL.md"
        if not skill_md.exists():
            issues.append(f"skill path missing SKILL.md: {skill_path}")
            continue
        metadata = parse_skill_metadata(read_text(skill_md))
        if not metadata.get("name"):
            issues.append(f"skill lacks name metadata: {skill_path}")

    payload = {"status": "pass" if not issues else "fail", "issues": issues}
    print(json.dumps(payload, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
