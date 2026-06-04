#!/usr/bin/env python3
"""Run lightweight smoke checks against generated Codex harnesses.

The default mode is CI-safe and offline: it proves Codex-facing files can be
read, parsed, and resolved. Use --codex-live locally when an authenticated Codex
CLI is available and you want a real instruction-loading smoke check.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 support for the Homebrew pytest shim.
    import tomli as tomllib


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def smoke_offline(root: Path) -> dict:
    issues: list[str] = []
    agents_md = root / "AGENTS.md"
    config_path = root / ".codex/config.toml"

    if not agents_md.is_file():
        issues.append("AGENTS.md is missing")
    elif not read_text(agents_md).strip():
        issues.append("AGENTS.md is empty")

    config = {}
    if not config_path.is_file():
        issues.append(".codex/config.toml is missing")
    else:
        try:
            config = tomllib.loads(read_text(config_path))
        except Exception as exc:
            issues.append(f".codex/config.toml does not parse: {exc}")

    resolved_agents = []
    for name, entry in config.get("agents", {}).items():
        if not isinstance(entry, dict):
            continue
        config_file = entry.get("config_file")
        if not isinstance(config_file, str):
            issues.append(f"agent {name} has no config_file")
            continue
        agent_path = root / ".codex" / config_file
        if not agent_path.is_file():
            issues.append(f"agent {name} config_file is missing: {config_file}")
            continue
        try:
            agent = tomllib.loads(read_text(agent_path))
        except Exception as exc:
            issues.append(f"agent {name} TOML does not parse: {exc}")
            continue
        resolved_agents.append(agent.get("name", name))

    resolved_skills = []
    for index, entry in enumerate(config.get("skills", {}).get("config", []), 1):
        if not isinstance(entry, dict):
            issues.append(f"skills.config entry {index} is not an object")
            continue
        skill_path = entry.get("path")
        if not isinstance(skill_path, str):
            issues.append(f"skills.config entry {index} has no path")
            continue
        skill_md = root / ".codex" / skill_path / "SKILL.md"
        if not skill_md.is_file():
            issues.append(f"skill path is missing SKILL.md: {skill_path}")
            continue
        metadata = parse_skill_metadata(read_text(skill_md))
        if not metadata.get("name"):
            issues.append(f"skill path lacks name metadata: {skill_path}")
            continue
        resolved_skills.append(metadata["name"])

    return {
        "path": root.as_posix(),
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "agents": resolved_agents,
        "skills": resolved_skills,
    }


def smoke_codex_live(root: Path, prompt: str) -> dict:
    codex = shutil.which("codex")
    if not codex:
        return {
            "path": root.as_posix(),
            "status": "skip",
            "reason": "codex CLI not found",
        }

    command = [
        codex,
        "--cd",
        root.as_posix(),
        "--ask-for-approval",
        "never",
        prompt,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=120)
    return {
        "path": root.as_posix(),
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-2000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Generated harness directory paths to smoke-test")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--codex-live", action="store_true", help="Also run an authenticated Codex CLI instruction-loading smoke check")
    parser.add_argument(
        "--prompt",
        default="Summarize the current project instructions in one sentence.",
        help="Prompt to use with --codex-live",
    )
    args = parser.parse_args()

    results = []
    for raw_path in args.paths:
        root = Path(raw_path).resolve()
        offline = smoke_offline(root)
        live = smoke_codex_live(root, args.prompt) if args.codex_live else None
        result = {"offline": offline}
        if live is not None:
            result["codex_live"] = live
        results.append(result)

    status = "pass"
    for result in results:
        if result["offline"]["status"] != "pass":
            status = "fail"
        live = result.get("codex_live")
        if live and live["status"] == "fail":
            status = "fail"

    payload = {"status": status, "results": results}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Generated harness smoke: {status.upper()}")
        for result in results:
            offline = result["offline"]
            print(f"- {offline['path']}: offline={offline['status'].upper()} agents={offline.get('agents', [])} skills={offline.get('skills', [])}")
            for issue in offline["issues"]:
                print(f"  - {issue}")
            live = result.get("codex_live")
            if live:
                print(f"  codex-live={live['status'].upper()}")

    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
