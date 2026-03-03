# Evidence Catalog: Workflow Adapter Patterns

## Sources

### S1: Azure DevOps — State Categories Model
- **URL:** https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories
- **Type:** Primary (official documentation, production system)
- **Evidence Level:** Very High (Microsoft, millions of users, 15+ years in production)
- **Key Finding:** Azure DevOps uses 4 abstract **state categories** (Proposed, In Progress, Resolved, Complete) that are fixed. Each work item type (Epic, Story, Task, Bug) defines its own **workflow states** (New, Active, Resolved, Closed) that map to these categories. Tools (boards, backlogs, burndowns) operate on categories, not states. Custom states map to one of the 4 categories.
- **Relevance:** HIGH — This is exactly the two-layer model we're designing.

### S2: Microsoft — Anti-Corruption Layer Pattern
- **URL:** https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer
- **Type:** Primary (Azure Architecture Center, Eric Evans DDD)
- **Evidence Level:** Very High (foundational DDD pattern, industry standard)
- **Key Finding:** ACL isolates subsystems with different semantics via facade + adapter + translator. Communication with subsystem A uses A's model; ACL translates to B's model. Domain model is never corrupted by external concepts. Adds latency but protects integrity.
- **Relevance:** HIGH — The adapter protocol IS an ACL between RaiSE's work model and Jira/file backends.

### S3: Nango — Unified API Best Practices
- **URL:** https://nango.dev/blog/best-practices-build-unified-api
- **Type:** Secondary (practitioner blog from production unified API platform)
- **Evidence Level:** High (Nango is a Y Combinator company, open source, 5k+ stars)
- **Key Finding:** Use YOUR internal data model as the unified schema, not a generic one. Start minimal, plan for nullable properties. Some fields won't map to all providers — leave as null rather than force-mapping. Validate at the external API boundary (Zod/Pydantic).
- **Relevance:** HIGH — Directly applicable. RaiSE's model should be RaiSE's, not Jira's.

### S4: Nango — Unified API Implementation Guide
- **URL:** https://nango.dev/docs/implementation-guides/use-cases/unified-apis
- **Type:** Secondary (implementation documentation)
- **Evidence Level:** High (working code examples, production patterns)
- **Key Finding:** Each provider gets its own implementation file with same interface signature. Unified model defined as Zod schema. Provider-specific features handled via: extended models, custom fields, or raw data attachment. "Even partial alignment is sufficient."
- **Relevance:** HIGH — The per-adapter implementation pattern matches our protocol approach.

### S5: Teiva Harsanyi — Canonical Data Model as Anti-Pattern
- **URL:** https://teivah.medium.com/why-is-a-canonical-data-model-an-anti-pattern-441b5c4cbff8
- **Type:** Secondary (expert practitioner, counter-argument)
- **Evidence Level:** Medium (single author, but well-cited in integration community)
- **Key Finding:** Enterprise-wide canonical models become bloated (many optional fields, few mandatory). They shift coupling rather than removing it. Better: bounded contexts with ACL between them. One model per context, explicit boundaries.
- **Relevance:** MEDIUM — Counter-argument to over-generalizing. Our scope is narrow (2 adapters, not enterprise-wide), which mitigates this risk.

### S6: Jira Align — State/Process Step Mapping
- **URL:** https://confluence.atlassian.com/jakb/mapping-states-process-steps-and-statuses-between-jira-align-and-jira-software-1387599540.html
- **Type:** Primary (Atlassian official documentation)
- **Evidence Level:** High (Atlassian production system, enterprise scale)
- **Key Finding:** Jira Align has TWO layers: Align States (system-defined, non-customizable) and Process Steps (user-defined, customizable). Both map bidirectionally to Jira Software statuses via configurable paths. Work item type determines which mapping applies. 5 color-coded mapping paths for different directions.
- **Relevance:** HIGH — Atlassian themselves use a two-layer state model with mapping tables.

### S7: Plane.so — GitHub Sync State Mapping
- **URL:** https://docs.plane.so/integrations/github
- **Type:** Secondary (open source project management tool)
- **Evidence Level:** Medium (29k+ stars, production use, but newer project)
- **Key Finding:** Plane maps GitHub issue states (open/closed) to Plane workflow states via user-configurable mapping. PR lifecycle also maps to workflow states. Bidirectional sync updates both sides when state changes.
- **Relevance:** MEDIUM — Shows state mapping pattern in open-source PM tool.

### S8: Exalate — Distributed Sync Architecture
- **URL:** https://exalate.com/blog/unito-app/
- **Type:** Tertiary (comparison blog)
- **Evidence Level:** Medium (commercial product, Groovy scripting engine)
- **Key Finding:** Exalate uses distributed architecture with scripting engine per tool. Each side has independent logic. Unito uses centralized flows. Both handle field/state mapping but with different tradeoffs (flexibility vs simplicity).
- **Relevance:** LOW — Confirms mapping pattern exists but too generic for our needs.

### S9: InfoQ — Avoid Canonical Data Models
- **URL:** https://www.infoq.com/news/2015/04/canonical-data-models/
- **Type:** Secondary (industry news, community discussion)
- **Evidence Level:** Medium (InfoQ editorial, multiple expert citations)
- **Key Finding:** Canonical models create bottleneck teams. Better: domain-specific models with translators. Integration should be point-to-point with ACLs, not hub-and-spoke through a canonical model.
- **Relevance:** MEDIUM — Reinforces S5's counter-argument. Again, our scope is narrow enough to mitigate.
