# Domain Library

Pre-built, tested **bundled domain profiles** -- ready-to-adapt starting points
for domains beyond the 4 base starter profiles. Each follows the slim profile
format (`Docs/StarterProfiles/PROFILE_FORMAT.md`); most are adapted from a
revfactory/harness-100 reference domain. Each points at templates, uses the four
core skills, and tiers models per role.

Use a bundled domain in **preset mode** when it matches the user's field (fast,
fewer interview rounds). For a domain not listed here, see
`Docs/StarterProfiles/DOMAIN_REFERENCE.md` for the closest match, or use
**custom mode** (the architect synthesizes a tailored DOMAIN_PROFILE.md).

## Bundled domains (16)

These domains map to a base via `Docs/StarterProfiles/DOMAIN_REFERENCE.md`.

| Domain | File | For | Source |
|---|---|---|---|
| API Design | api-design.md | REST/GraphQL API design, contracts, docs, client generation | harness-100 18 |
| Book Publishing | book-publishing.md | Long-form manuscript workflow, editing passes, style consistency | harness-100 11 |
| Course Design | course-design.md | Curriculum, lesson plans, assessments, learning objectives | harness-100 08 |
| Customer Support | customer-support.md | Support-documentation systems: FAQs, response manuals, escalation policies, CS analytics (grounded, draft-only; not a live chatbot) | harness-100 49 |
| Data Engineering | data-engineering.md | ETL/data pipelines, schema design, data validation, monitoring | harness-100 27 |
| Data Science | data-science.md | ML/statistical model building: EDA, training, evaluation, experiment tracking -- offline (not LLM apps, not production pipelines) | -- |
| Financial Modeling | financial-modeling.md | Financial models, projections, scenario analysis, investor-facing output | harness-100 53 |
| Game Development | game-development.md | Engine work (Unreal/Unity/Godot): gameplay/crash/replication/perf, manual playtest gate, binary-asset protection | -- |
| Grant Writing | grant-writing.md | Grant proposals, funding narratives, budget justifications | harness-100 54 |
| Hiring Pipeline | hiring-pipeline.md | Job specs, rubrics, interview kits, candidate evaluation | harness-100 90 |
| Legal Research | legal-research.md | Case/statute research, memos, citation discipline (advisory, not legal advice) | harness-100 70 |
| LLM App | llm-app.md | Building LLM-powered apps (RAG, agents, prompt/eval pipelines) | harness-100 41 |
| Market Research | market-research.md | Market sizing, competitor/landscape analysis, research reports | harness-100 44 |
| Product Management | product-management.md | PRDs, roadmaps, prioritization, stakeholder specs | harness-100 46 |
| Security Audit | security-audit.md | Code/dependency/IaC security audits, pentest reports, remediation roadmaps | harness-100 28 |
| Social Media | social-media.md | Content calendars, post copy, campaign planning, analytics | harness-100 10 |

## Adding more

The Harness Generator does not bundle all 100 harness-100 domains (a 1,800+ file
distribution). For breadth beyond these 16, prefer custom generation (a reusable
DOMAIN_PROFILE.md) over hand-authoring. `DOMAIN_REFERENCE.md` lists which common
domains map to which starting point.
