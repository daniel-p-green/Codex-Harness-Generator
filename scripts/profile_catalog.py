#!/usr/bin/env python3
"""Show deterministic Codex harness starter profile details."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict

from generate_minimal_harness import PROFILES, Profile


BASE_PROFILE_SLUGS = {
    "software-development",
    "knowledge-work",
    "data-analysis",
    "devops-infrastructure",
}

PROFILE_HINTS = {
    "api-design": (
        "api",
        "endpoint",
        "graphql",
        "openapi",
        "rest",
        "schema",
        "service contract",
        "versioning",
    ),
    "book-publishing": (
        "book",
        "chapter",
        "copyedit",
        "editorial",
        "manuscript",
        "publishing",
        "style guide",
    ),
    "course-design": (
        "assessment",
        "course",
        "curriculum",
        "lesson",
        "learning objective",
        "rubric",
        "training",
    ),
    "customer-support": (
        "customer",
        "escalation",
        "faq",
        "refund",
        "support",
        "ticket",
        "user complaint",
    ),
    "data-analysis": (
        "analysis",
        "analyst",
        "csv",
        "dashboard",
        "excel",
        "metric",
        "notebook",
        "spreadsheet",
    ),
    "data-engineering": (
        "data contract",
        "etl",
        "pipeline",
        "schema migration",
        "warehouse",
        "backfill",
        "partition",
    ),
    "data-science": (
        "experiment",
        "feature engineering",
        "leakage",
        "model assessment",
        "notebook",
        "training data",
        "validation metric",
    ),
    "devops-infrastructure": (
        "ci/cd",
        "deployment",
        "docker",
        "infrastructure",
        "kubernetes",
        "rollback",
        "terraform",
    ),
    "financial-modeling": (
        "assumptions",
        "forecast",
        "financial model",
        "investment",
        "scenario",
        "sensitivity",
        "valuation",
    ),
    "game-development": (
        "asset",
        "build",
        "engine",
        "game",
        "gameplay",
        "scene",
        "unity",
        "unreal",
    ),
    "grant-writing": (
        "budget narrative",
        "eligibility",
        "funder",
        "grant",
        "proposal",
        "submission",
    ),
    "hiring-pipeline": (
        "candidate",
        "hiring",
        "interview",
        "job description",
        "recruiting",
        "rubric",
        "scorecard",
    ),
    "knowledge-work": (
        "brief",
        "document",
        "memo",
        "notes",
        "operations",
        "planning",
        "research",
        "summary",
    ),
    "legal-research": (
        "case law",
        "contract",
        "jurisdiction",
        "legal",
        "memo",
        "policy",
        "statute",
    ),
    "llm-app": (
        "agent",
        "eval",
        "hallucination",
        "llm",
        "prompt",
        "rag",
        "retrieval",
        "tool call",
    ),
    "market-research": (
        "competitor",
        "customer segment",
        "landscape",
        "market",
        "market sizing",
        "tam",
        "trend",
    ),
    "product-management": (
        "acceptance criteria",
        "prd",
        "prioritization",
        "product",
        "requirements",
        "roadmap",
        "stakeholder",
    ),
    "security-audit": (
        "audit",
        "cve",
        "exploit",
        "penetration",
        "security",
        "threat model",
        "vulnerability",
    ),
    "social-media": (
        "campaign",
        "content calendar",
        "instagram",
        "linkedin",
        "post",
        "social",
        "twitter",
    ),
    "software-development": (
        "bug",
        "cli",
        "code",
        "library",
        "python",
        "refactor",
        "software",
        "test",
    ),
}

STOP_WORDS = {
    "about",
    "after",
    "also",
    "before",
    "brief",
    "check",
    "checks",
    "create",
    "from",
    "help",
    "into",
    "model",
    "need",
    "project",
    "quality",
    "review",
    "task",
    "that",
    "this",
    "thing",
    "tool",
    "tools",
    "with",
    "work",
}


def profile_to_dict(profile: Profile) -> dict:
    payload = asdict(profile)
    payload["kind"] = "base" if profile.slug in BASE_PROFILE_SLUGS else "domain"
    return payload


def catalog_payload(profile_slug: str | None = None) -> dict:
    if profile_slug:
        profile = PROFILES.get(profile_slug)
        if not profile:
            supported = ", ".join(sorted(PROFILES))
            raise SystemExit(f"Unsupported profile {profile_slug!r}. Supported profiles: {supported}")
        profiles = [profile_to_dict(profile)]
    else:
        profiles = [profile_to_dict(PROFILES[slug]) for slug in sorted(PROFILES)]

    return {
        "status": "pass",
        "profile_count": len(profiles),
        "total_supported_profiles": len(PROFILES),
        "profiles": profiles,
    }


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def profile_search_text(profile: Profile) -> str:
    parts = [
        profile.slug,
        profile.default_project_name,
        profile.domain,
        profile.target,
        profile.permission_profile,
        profile.reviewer_description,
        profile.agent_focus,
        *profile.verification,
        *profile.first_tasks,
        *profile.assumptions,
        *profile.extra_guidance,
        *PROFILE_HINTS.get(profile.slug, ()),
    ]
    return normalized(" ".join(parts))


def term_matches(brief: str, profile: Profile) -> tuple[str, ...]:
    brief_text = normalized(brief)
    search_text = profile_search_text(profile)
    matched = []
    for term in PROFILE_HINTS.get(profile.slug, ()):
        if normalized(term) in brief_text:
            matched.append(term)
    for token in re.findall(r"[a-z0-9][a-z0-9/+.-]*", brief_text):
        if len(token) < 4:
            continue
        if token in STOP_WORDS:
            continue
        if token in search_text and token not in matched:
            matched.append(token)
    return tuple(matched)


def confidence_for_score(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 35:
        return "medium"
    if score > 0:
        return "low"
    return "none"


def recommendation_payload(brief: str, limit: int = 3) -> dict:
    if not brief.strip():
        raise SystemExit("--recommend requires a non-empty project brief")
    if limit < 1:
        raise SystemExit("--limit must be at least 1")

    recommendations = []
    for slug in sorted(PROFILES):
        profile = PROFILES[slug]
        matches = term_matches(brief, profile)
        score = min(100, len(matches) * 12)
        if profile.domain in normalized(brief):
            score = min(100, score + 20)
        recommendations.append(
            {
                "slug": slug,
                "score": score,
                "confidence": confidence_for_score(score),
                "matched_terms": list(matches[:10]),
                "domain": profile.domain,
                "target": profile.target,
                "kind": "base" if slug in BASE_PROFILE_SLUGS else "domain",
            }
        )

    recommendations.sort(key=lambda item: (-item["score"], item["slug"]))
    positive = [item for item in recommendations if item["score"] > 0]
    selected = (positive or recommendations)[:limit]
    return {
        "status": "pass",
        "brief": brief,
        "confidence": selected[0]["confidence"],
        "guidance": (
            "Use this deterministic starter, then inspect generated PROFILE_SELECTION.md and run eval/smoke."
            if selected[0]["confidence"] in {"high", "medium"}
            else "Low confidence: prefer full /create custom intake unless you understand and accept the selected starter."
            if selected[0]["confidence"] == "low"
            else "No deterministic profile matched: use full /create custom intake or provide a clearer brief."
        ),
        "recommendation_count": len(selected),
        "total_supported_profiles": len(PROFILES),
        "recommendations": selected,
    }


def wrap(text: str, width: int = 88) -> str:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        next_len = current_len + len(word) + (1 if current else 0)
        if current and next_len > width:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len = next_len
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def indent_wrapped(text: str, width: int, continuation: str) -> str:
    return wrap(text, width).replace("\n", "\n" + continuation)


def format_catalog(payload: dict) -> str:
    lines = [
        f"Supported deterministic profiles: {payload['total_supported_profiles']}",
        "",
    ]
    for profile in payload["profiles"]:
        lines.extend(
            [
                f"{profile['slug']} ({profile['kind']})",
                f"  Domain: {profile['domain']}",
                f"  Target: {indent_wrapped(profile['target'], 78, '          ')}",
                f"  Permission profile: {profile['permission_profile']}",
                f"  Reviewer: {indent_wrapped(profile['reviewer_description'], 78, '            ')}",
                "  First tasks:",
            ]
        )
        for task in profile["first_tasks"]:
            lines.append(f"    - {task}")
        if profile["extra_guidance"]:
            lines.append("  Guardrails:")
            for item in profile["extra_guidance"]:
                lines.append(f"    - {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_recommendations(payload: dict) -> str:
    lines = [
        "Recommended deterministic profiles",
        f"Brief: {payload['brief']}",
        "",
    ]
    for index, item in enumerate(payload["recommendations"], 1):
        lines.extend(
            [
                f"{index}. {item['slug']} ({item['kind']}, score={item['score']}, confidence={item['confidence']})",
                f"   Domain: {item['domain']}",
                f"   Target: {indent_wrapped(item['target'], 76, '           ')}",
                f"   Matched: {', '.join(item['matched_terms']) if item['matched_terms'] else 'no strong keyword match'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="Show one profile instead of the full catalog")
    parser.add_argument("--recommend", help="Recommend deterministic profiles for a project brief")
    parser.add_argument("--limit", type=int, default=3, help="Number of recommendations to show")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.profile and args.recommend:
        parser.error("--profile and --recommend cannot be used together")

    payload = recommendation_payload(args.recommend, args.limit) if args.recommend else catalog_payload(args.profile)
    if args.json:
        print(json.dumps(payload, indent=2))
    elif args.recommend:
        print(format_recommendations(payload), end="")
    else:
        print(format_catalog(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
