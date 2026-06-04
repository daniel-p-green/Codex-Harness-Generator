#!/usr/bin/env python3
"""Inspect a local project and recommend Codex harness starter profiles."""

from __future__ import annotations

import argparse
import json
import shlex
from collections import Counter
from pathlib import Path

from profile_catalog import PROFILE_HINTS, PROFILES, recommendation_payload


DEFAULT_IGNORE_DIRS = {
    ".codex",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
}
DEFAULT_IGNORE_FILES = {
    ".DS_Store",
}

MAX_TEXT_SIGNAL_BYTES = 12_000
TEXT_SIGNAL_SUFFIXES = {
    ".json",
    ".md",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

CONFIG_SIGNALS = {
    "package.json": "JavaScript or TypeScript package",
    "pyproject.toml": "Python package or tool",
    "requirements.txt": "Python dependency file",
    "setup.py": "Python package",
    "Pipfile": "Python dependency file",
    "poetry.lock": "Python lockfile",
    "uv.lock": "Python lockfile",
    "Cargo.toml": "Rust package",
    "go.mod": "Go module",
    "Gemfile": "Ruby application",
    "Dockerfile": "container build",
    "docker-compose.yml": "local service stack",
    "compose.yml": "local service stack",
    "terraform.tf": "Terraform infrastructure",
    "openapi.yaml": "OpenAPI spec",
    "openapi.yml": "OpenAPI spec",
    "openapi.json": "OpenAPI spec",
    "schema.graphql": "GraphQL schema",
    "README.md": "project README",
}

EXTENSION_SIGNALS = {
    ".ipynb": "notebooks",
    ".md": "Markdown docs",
    ".py": "Python code",
    ".js": "JavaScript code",
    ".jsx": "React code",
    ".ts": "TypeScript code",
    ".tsx": "React TypeScript code",
    ".go": "Go code",
    ".rs": "Rust code",
    ".tf": "Terraform config",
    ".sql": "SQL",
    ".csv": "CSV data",
    ".xlsx": "spreadsheet",
    ".docx": "Word document",
    ".pdf": "PDF document",
}

DIRECTORY_SIGNALS = {
    ".github": "GitHub automation",
    "api": "API code",
    "app": "application code",
    "data": "data files",
    "docs": "documentation",
    "infra": "infrastructure",
    "notebooks": "notebooks",
    "prompts": "LLM prompts",
    "src": "application code",
    "tests": "test suite",
}

SIGNAL_TERMS = {
    "api": "API endpoints service contract OpenAPI schema",
    "data": "data analysis CSV metric notebook dashboard",
    "docs": "knowledge work document notes planning source fidelity",
    "infra": "DevOps infrastructure deployment Docker Terraform CI/CD",
    "notebooks": "data science experiment notebook validation metric",
    "prompts": "LLM app prompts evals RAG retrieval agent tool call",
    "tests": "software development tests code refactor",
}

DIRECTORY_PROFILE_BOOSTS = {
    "api": {"api-design": 30, "software-development": 8},
    "data": {"data-analysis": 12},
    "docs": {"knowledge-work": 16},
    "infra": {"devops-infrastructure": 30},
    "notebooks": {"data-science": 26, "data-analysis": 12},
    "prompts": {"llm-app": 34},
    "tests": {"software-development": 8},
}

CONFIG_PROFILE_BOOSTS = {
    "Dockerfile": {"devops-infrastructure": 18, "software-development": 6},
    "docker-compose.yml": {"devops-infrastructure": 24},
    "compose.yml": {"devops-infrastructure": 24},
    "go.mod": {"software-development": 14},
    "openapi.json": {"api-design": 34},
    "openapi.yaml": {"api-design": 34},
    "openapi.yml": {"api-design": 34},
    "package.json": {"software-development": 12},
    "pyproject.toml": {"software-development": 10},
    "requirements.txt": {"software-development": 10},
    "schema.graphql": {"api-design": 30},
}

EXTENSION_PROFILE_BOOSTS = {
    ".csv": {"data-analysis": 8},
    ".ipynb": {"data-science": 24, "data-analysis": 8},
    ".md": {"knowledge-work": 4},
    ".py": {"software-development": 8},
    ".sql": {"data-engineering": 14, "data-analysis": 8},
    ".tf": {"devops-infrastructure": 28},
    ".tsx": {"software-development": 8},
    ".ts": {"software-development": 8},
}

KNOWN_PROFILE_TERMS = tuple(
    sorted({term for terms in PROFILE_HINTS.values() for term in terms}, key=lambda term: (len(term), term))
)


def should_skip(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return path.name in DEFAULT_IGNORE_FILES or any(part in DEFAULT_IGNORE_DIRS for part in relative.parts)


def is_config_signal(relative: Path) -> bool:
    name = relative.name
    if name not in CONFIG_SIGNALS:
        return False
    if name == "README.md":
        return len(relative.parts) == 1
    if name.startswith("openapi.") or name == "schema.graphql":
        return True
    return len(relative.parts) <= 2


def extract_known_terms(text: str) -> list[str]:
    normalized = text.lower().replace("_", " ").replace("-", " ")
    matches = []
    for term in KNOWN_PROFILE_TERMS:
        if term.lower() in normalized:
            matches.append(term)
    return sorted(set(matches))


def read_text_signal_terms(path: Path) -> list[str]:
    if path.suffix.lower() not in TEXT_SIGNAL_SUFFIXES:
        return []
    try:
        text = path.read_bytes()[:MAX_TEXT_SIGNAL_BYTES].decode("utf-8", errors="ignore")
    except OSError:
        return []
    return extract_known_terms(text)


def scan_project(root: Path, max_files: int) -> dict:
    if not root.exists():
        raise SystemExit(f"Project path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Project path must be a directory: {root}")
    if max_files < 1:
        raise SystemExit("--max-files must be at least 1")

    files_seen = 0
    truncated = False
    extensions: Counter[str] = Counter()
    config_files: list[str] = []
    directories: set[str] = set()
    content_terms: set[str] = set()
    sample_files: list[str] = []

    for path in sorted(root.rglob("*")):
        if should_skip(path, root):
            continue
        if path.is_dir():
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            if len(relative.parts) == 1 and relative.as_posix() in DIRECTORY_SIGNALS:
                directories.add(relative.as_posix())
            continue
        files_seen += 1
        if files_seen > max_files:
            truncated = True
            break
        relative = path.relative_to(root).as_posix()
        content_terms.update(extract_known_terms(relative))
        content_terms.update(read_text_signal_terms(path))
        if len(sample_files) < 12:
            sample_files.append(relative)
        name = path.name
        relative_path = Path(relative)
        if is_config_signal(relative_path):
            config_files.append(relative)
        if path.suffix:
            extensions[path.suffix.lower()] += 1

    return {
        "name": root.name,
        "files_scanned": min(files_seen, max_files),
        "truncated": truncated,
        "config_files": sorted(config_files),
        "directories": sorted(directories),
        "content_terms": sorted(content_terms),
        "extensions": dict(sorted(extensions.items(), key=lambda item: (-item[1], item[0]))[:12]),
        "sample_files": sample_files,
    }


def build_brief(scan: dict) -> str:
    terms: list[str] = [scan["name"]]
    for path in scan["config_files"]:
        terms.append(CONFIG_SIGNALS.get(Path(path).name, Path(path).name))
    for directory in scan["directories"]:
        terms.append(DIRECTORY_SIGNALS.get(directory, directory))
        terms.append(SIGNAL_TERMS.get(directory, ""))
    if scan["content_terms"]:
        terms.append("project signals " + " ".join(scan["content_terms"]))
    for extension, count in scan["extensions"].items():
        signal = EXTENSION_SIGNALS.get(extension, extension)
        terms.append(f"{signal} ({count})")
    return " ".join(term for term in terms if term).strip()


def profile_boosts(scan: dict) -> dict[str, int]:
    boosts: Counter[str] = Counter()
    for directory in scan["directories"]:
        boosts.update(DIRECTORY_PROFILE_BOOSTS.get(directory, {}))
    for path in scan["config_files"]:
        boosts.update(CONFIG_PROFILE_BOOSTS.get(Path(path).name, {}))
    for extension in scan["extensions"]:
        boosts.update(EXTENSION_PROFILE_BOOSTS.get(extension, {}))
    return dict(boosts)


def apply_inspection_boosts(recommendations: dict, boosts: dict[str, int], limit: int) -> dict:
    adjusted = []
    for item in recommendations["recommendations"]:
        boost = boosts.get(item["slug"], 0)
        adjusted_item = {**item, "inspection_boost": boost, "inspection_score": item["score"] + boost}
        adjusted.append(adjusted_item)
    adjusted.sort(key=lambda item: (-item["inspection_score"], -item["score"], item["slug"]))
    return {**recommendations, "recommendation_count": min(limit, len(adjusted)), "recommendations": adjusted[:limit]}


def build_payload(path: Path, max_files: int, limit: int) -> dict:
    if limit < 1:
        raise SystemExit("--limit must be at least 1")
    scan = scan_project(path.resolve(), max_files=max_files)
    inferred_brief = build_brief(scan)
    boosts = profile_boosts(scan)
    recommendations = apply_inspection_boosts(recommendation_payload(inferred_brief, limit=len(PROFILES)), boosts, limit=limit)
    top = recommendations["recommendations"][0]
    next_command = " ".join(
        [
            "codex-harness",
            "init",
            "<target>",
            "--brief",
            shlex.quote(inferred_brief),
            "--project-name",
            shlex.quote(scan["name"]),
            "--force",
        ]
    )
    return {
        "status": "pass",
        "project": scan["name"],
        "files_scanned": scan["files_scanned"],
        "truncated": scan["truncated"],
        "signals": {
            "config_files": scan["config_files"],
            "directories": scan["directories"],
            "content_terms": scan["content_terms"],
            "extensions": scan["extensions"],
            "sample_files": scan["sample_files"],
        },
        "inferred_brief": inferred_brief,
        "inspection_boosts": boosts,
        "recommendations": recommendations,
        "next_command": next_command,
        "recommended_profile": top["slug"],
        "confidence": top["confidence"],
    }


def format_payload(payload: dict) -> str:
    lines = [
        f"Project inspection: {payload['project']}",
        f"Files scanned: {payload['files_scanned']}{' (truncated)' if payload['truncated'] else ''}",
        "",
        "Signals:",
    ]
    signals = payload["signals"]
    for label, values in (
        ("Config files", signals["config_files"]),
        ("Directories", signals["directories"]),
        ("Content terms", signals["content_terms"]),
    ):
        lines.append(f"- {label}: {', '.join(values) if values else 'none detected'}")
    extension_summary = ", ".join(f"{key}={value}" for key, value in signals["extensions"].items())
    lines.append(f"- Extensions: {extension_summary or 'none detected'}")
    lines.extend(["", "Recommended deterministic profiles:"])
    for index, item in enumerate(payload["recommendations"]["recommendations"], 1):
        matched = ", ".join(item["matched_terms"]) if item["matched_terms"] else "no strong keyword match"
        lines.append(f"{index}. {item['slug']} ({item['confidence']}, score={item['score']}) - matched: {matched}")
    lines.extend(["", "Next command:", payload["next_command"]])
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Project directory to inspect")
    parser.add_argument("--max-files", type=int, default=800, help="Maximum files to scan before truncating")
    parser.add_argument("--limit", type=int, default=3, help="Number of profile recommendations")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload")
    args = parser.parse_args()

    payload = build_payload(Path(args.path), max_files=args.max_files, limit=args.limit)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_payload(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
