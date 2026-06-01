# Domain Reference

A fetch-on-demand map from common domains to the best starting point: a base
starter profile, a bundled domain (`Docs/DomainLibrary/`), or custom generation.
Use during intake to route the user quickly. "Closest + deviations" means: start
from that profile/domain and adjust the listed points during customization.

Coverage today: 4 base profiles + 16 bundled domains = 20 first-class starting
points. Anything else maps to the closest one (with deviations) or custom mode.

## Base profiles (4)

| Domain | Profile |
|---|---|
| Web apps, APIs, CLIs, libraries, services | software-development |
| Research, writing, legal, finance, consulting (document-centric) | knowledge-work |
| Analytics, reporting, dashboards, spreadsheet analysis | data-analysis |
| Cloud infra, IaC, CI/CD, SRE/reliability | devops-infrastructure |

## Bundled domains (16)

See `Docs/DomainLibrary/INDEX.md`. One-line: api-design, book-publishing,
course-design, customer-support, data-engineering, data-science,
financial-modeling, game-development, grant-writing, hiring-pipeline,
legal-research, llm-app, market-research, product-management, security-audit,
social-media.

## Common domains -> closest starting point + deviations

| User's domain | Start from | Key deviations |
|---|---|---|
| Mobile app (iOS/Android/React Native) | software-development | Swap ecosystem perms (Xcode/Gradle/RN); add device/simulator build skill |
| Microservices / distributed backend | software-development + api-design | Add service-boundary routing; per-service ecosystem perms |
| Machine-learning experiments / model training | data-science | Experiment tracking, held-out validation, leakage/reproducibility discipline built in |
| Compliance / regulatory frameworks (HIPAA/SOX/PCI/GDPR) | knowledge-work (interpretation) or security-audit (technical controls) | Add sensitive-data rule + deterministic PII hooks; framework mapping; adverse-decision rule if it drives decisions about people |
| Healthcare / clinical documentation or decision-support | knowledge-work + sensitive-data + adverse-decision rules | Custom mode for depth; never finalize a clinical decision (human owns it); HIPAA handling |
| Contract / policy drafting | legal-research + grant-writing | Add template-management + clause library; conservative autonomy |
| Technical writing / documentation | knowledge-work | Add doc-build skill; doc-parsing pipeline; style guide |
| E-commerce store / marketplace | software-development | Add payments/PII deny rules; inventory + catalog routing |
| Startup / fundraising ops | product-management + financial-modeling | Add pitch/investor-report deliverables; market-research cross-link |
| Sales enablement / proposals | grant-writing (proposal mechanics) | Swap funder framing for buyer framing; CRM integration |
| Academic paper / thesis | knowledge-work + grant-writing | Add citation manager; venue/format templates; literature-review routing |
| Content / video / podcast production | social-media | Add asset/transcript handling; per-channel publishing routing |
| HR / people operations | hiring-pipeline | Add onboarding + policy-doc routing; PII handling |
| Personal finance / accounting | financial-modeling | Add ledger/spreadsheet routing; conservative (no auto-transactions) |
| Embedded / firmware | software-development | Add toolchain perms (gcc-arm, openocd); hardware-in-the-loop notes |
| Incident response / on-call | devops-infrastructure | Add postmortem + runbook routing; alerting integrations |

## When nothing fits

If the user's domain matches none of the above closely, use **custom mode**:
the intake runs a fuller interview and the architect synthesizes a reusable
`DOMAIN_PROFILE.md` in the target environment (more tokens + time, best for
long-term harnesses). harness-100 (revfactory) has 100 domains as additional
inspiration if you need a reference shape -- never bundle it wholesale.
