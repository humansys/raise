# Evidence Catalog: Open-Core Storage Patterns (YAML-in-Repo vs Service/Database)

**Research date:** 2026-03-03
**Session type:** research
**Goal:** Understand how open-core developer tools bridge the gap between file-based storage (OSS/free tier) and scalable service/database storage (Pro/Enterprise tiers).

---

## Sources

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| 1 | [Backstage OSS catalog docs](https://backstage.io/docs/features/software-catalog/) | Primary | Very High | YAML files in repos are "source of truth" but catalog backend DB is a **cache**, not the authority. Entity Providers + Processors ingest YAML into PostgreSQL. |
| 2 | [Backstage entity lifecycle](https://backstage.io/docs/features/software-catalog/life-of-an-entity/) | Primary | Very High | Ingestion loop: Entity Providers emit mutations -> Processors transform -> DB stores. Incremental provider supports delta mutations for scale. |
| 3 | [Backstage external integrations](https://backstage.io/docs/features/software-catalog/external-integrations/) | Primary | Very High | Two extension points: Entity Providers (fetch from external sources) and Processors (transform/validate). Both feed into same DB. |
| 4 | [Backstage incremental ingestion](https://backstage.io/blog/2023/01/31/incremental-entity-provider/) | Primary | High | Incremental Entity Provider uses delta mutations + orphan detection for large-scale ingestion without full reconciliation each cycle. |
| 5 | [Spotify Portal vs Backstage OSS](https://info.backstage.spotify.com/portal-vs-backstage) | Primary | High | Same core foundation. Portal = managed SaaS with premium plugins (RBAC, Soundcheck, Insights). Catalog model identical; difference is operational, not architectural. |
| 6 | [Backstage 5-year retrospective](https://engineering.atspotify.com/2025/4/celebrating-five-years-of-backstage) | Secondary | Medium | Confirms open-core trajectory: OSS framework + managed enterprise product (Spotify Portal). |
| 7 | [HCP Terraform state management](https://developer.hashicorp.com/terraform/cloud-docs/workspaces/state) | Primary | Very High | HCL files local, state managed remotely. Cloud block in config = bridge. Same binary, behavior changes based on backend config. |
| 8 | [Terraform remote state](https://developer.hashicorp.com/terraform/language/state/remote) | Primary | Very High | State file = the "database". Local->remote migration via backend config change. Locking, versioning, encryption added by remote backends. |
| 9 | [HCP Terraform workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces) | Primary | High | Workspaces = multi-tenancy unit. Granular permissions per workspace. Project-level scoping for team isolation. |
| 10 | [Terraform Cloud overview (Spacelift)](https://spacelift.io/blog/what-is-terraform-cloud) | Secondary | Medium | Confirms: same CLI, different backend. Cloud adds collaboration (state locking, RBAC, audit trail, policy-as-code). |
| 11 | [Pulumi state and backends](https://www.pulumi.com/docs/iac/concepts/state-and-backends/) | Primary | Very High | Three tiers: local filesystem, self-managed (S3/Azure/GCS/PostgreSQL), Pulumi Cloud. Same CLI, `pulumi login` switches backend. |
| 12 | [Pulumi Cloud vs OSS](https://www.pulumi.com/docs/iac/concepts/pulumi-cloud/) | Primary | Very High | Cloud adds: transactional checkpointing, concurrent state locking, deployment history, secrets management, RBAC, audit logs. |
| 13 | [Pulumi state management guide (Spacelift)](https://spacelift.io/blog/pulumi-state-management) | Secondary | High | Migration: `pulumi stack export > state.json` -> login to new backend -> `pulumi stack import`. Clean, portable state format. |
| 14 | [Pulumi ESC secrets](https://www.pulumi.com/blog/why-every-cloud-engineer-needs-pulumi-esc-secrets-management/) | Primary | High | ESC environments = YAML-based config that serves as centralized secrets management. Separate concern from IaC state. |
| 15 | [GitLab architecture docs](https://docs.gitlab.com/development/architecture/) | Primary | Very High | `.gitlab-ci.yml` in repo defines pipelines. Pipeline metadata in PostgreSQL, artifacts in object storage. Single codebase, tier-gated features. |
| 16 | [GitLab pricing/tiers](https://about.gitlab.com/pricing/) | Primary | High | Free (5 users, 400 CI min), Premium ($29/user: approval rules, code ownership), Ultimate ($99/user: SAST/DAST, compliance). "Buyer-Based Open Core" philosophy. |
| 17 | [GitLab CI/CD architecture (KodeKloud)](https://notes.kodekloud.com/docs/GitLab-CICD-Architecting-Deploying-and-Optimizing-Pipelines/Architecture-Core-Concepts/GitLab-CICD-Architecture-SaaS) | Secondary | Medium | Server orchestrates pipeline from YAML. SaaS vs self-managed share same architecture; difference is operational responsibility. |
| 18 | [Cortex entity descriptors](https://docs.cortex.io/ingesting-data-into-cortex/entities/yaml) | Primary | High | `cortex.yaml` in repos = entity descriptor. GitOps mode auto-syncs from default branch. Can also use API or UI for non-GitOps workflows. |
| 19 | [Cortex GitOps docs](https://docs.cortex.io/configure/gitops) | Primary | High | Two models: centralized repo with catalog/domains/teams dirs, or distributed cortex.yaml per repo. Auto-parsing on push to default branch. |
| 20 | [Port.dev GitOps docs](https://docs.port.io/build-your-software-catalog/sync-data-to-catalog/git/github/gitops/) | Primary | High | `port.yml` in repos ingested on commit to main. JQ-based mapping transforms external API data into Port entities. Database is primary store; YAML is an ingestion channel. |
| 21 | [Port.dev data model blog](https://www.port.io/blog/what-you-need-to-know-about-the-data-model-in-an-internal-developer-portal) | Primary | High | Blueprints (custom entity definitions) are the core. No-code portal; YAML/API/integrations are all ingestion channels into the database. |
| 22 | [OpsLevel vs Cortex vs Port comparison](https://www.opslevel.com/resources/port-vs-cortex-whats-the-best-internal-developer-portal) | Secondary | Medium | OpsLevel = automated API-based discovery. Cortex = YAML-in-repo. Port = UI/API + GitOps hybrid. Three distinct approaches to the same problem. |
| 23 | [Harness IDP catalog ingestion API](https://developer.harness.io/docs/internal-developer-portal/catalog/catalog-ingestion/catalog-ingestion-api/) | Primary | High | Hybrid: YAML-based catalog definitions + API-based metadata ingestion. API updates don't require YAML edits. Cron-based sync pipelines. |
| 24 | [Harness IDP catalog ingestion blog](https://www.harness.io/blog/introducing-new-catalog-ingestion-apis-to-make-harness-idp-truly-yours) | Primary | Medium | "Avoiding the need for manual and expensive YAML updates from developers." API enrichment layer on top of YAML base definitions. |
| 25 | [Datadog service catalog setup](https://docs.datadoghq.com/internal_developer_portal/software_catalog/set_up/) | Primary | High | Scans repos for `service.datadog.yaml` and `catalog-info.yaml`. Also accepts POST of YAML to API. Runtime telemetry auto-discovers services. |
| 26 | [Nx Cloud remote cache](https://nx.dev/docs/features/ci-features/remote-cache) | Primary | Very High | Local `nx.json` config. Remote cache = managed or self-hosted. Token-based auth: read-only (branch-isolated) vs read-write (shared). |
| 27 | [Nx self-hosted cache](https://nx.dev/docs/guides/tasks--caching/self-hosted-caching) | Primary | High | OpenAPI spec for custom cache servers. S3/GCS plugins available. Enterprise adds SSO, SAML, dedicated hosting. |
| 28 | [Nx self-hosted cache evolution (Medium)](https://emilyxiong.medium.com/exploring-of-nx-self-hosted-cache-5bc39bd2ed7f) | Secondary | Medium | Nx initially made self-hosted cache paid, then reversed to free after community backlash. Shows tension in open-core cache monetization. |
| 29 | [Snyk vs Dependabot comparison (codeYaan)](https://codeyaan.com/blog/how-to-guides/snyk-vs-dependabot-security-scanning-compared-8361) | Secondary | Medium | Dependabot = repo-centric (dependabot.yml). Snyk = cloud-first (dashboard + CLI + .snyk file). Different philosophies on where config authority lives. |
| 30 | [Snyk/Dependabot ignore configs (jeffry.in)](https://jeffry.in/snyk-dependabot-ignore-configs/) | Primary | Medium | `.snyk` file for policy-as-code, but `snyk monitor` uploads to cloud dashboard. Dependabot.yml stays in repo. Snyk's cloud dashboard is the aggregation layer. |
| 31 | [Humanitec: service catalogs and IDPs](https://humanitec.com/blog/service-catalogs-and-internal-developer-platforms) | Secondary | Medium | Service catalogs shifted from centralized CMDBs to distributed git-based YAML. Modern trend is hybrid: YAML for declarations, database for aggregation. |
| 32 | [Kong OSS to Enterprise migration](https://konghq.com/blog/engineering/how-and-why-to-migrate-from-kong-open-source-to-kong-enterprise-api-gateway) | Secondary | Medium | Database-based migration. Same core, enterprise adds RBAC, workspaces, audit logging on top. Relevant parallel pattern. |

---

## Architectural Patterns Identified

### Pattern 1: "Repo YAML as Source of Truth, DB as Cache" (Backstage, Cortex)

**How it works:**
- YAML files in repositories are the authoritative source
- Backend service ingests/reconciles YAML into a database (PostgreSQL for Backstage)
- Database serves as a read-optimized cache for the UI and APIs
- Changes flow: Git commit -> ingestion loop -> DB update -> UI reflects
- The DB is never edited directly in the OSS model

**Sync mechanism:**
- Polling-based ingestion loops (Backstage: configurable interval)
- Webhook-triggered on push to default branch (Cortex)
- Incremental/delta mutations for scale (Backstage Incremental Entity Provider)
- Orphan detection: entities not seen in latest ingestion cycle are deleted

**Multi-tenancy:**
- OSS: single-tenant, self-hosted
- Enterprise (Spotify Portal): managed multi-tenant SaaS, same catalog model
- Permissions via RBAC plugin (enterprise) or basic auth (OSS)

**Migration path:**
- No migration needed between storage layers -- DB is always a derived cache
- Migration is OSS self-hosted -> managed SaaS (operational, not data model change)

**Strengths:** Git-native, developer-friendly, auditable, decentralized ownership
**Weaknesses:** Eventual consistency, ingestion lag, no real-time updates, YAML sprawl at scale

---

### Pattern 2: "Same CLI, Different Backend" (Terraform, Pulumi)

**How it works:**
- Configuration files (HCL, Pulumi programs) always live in the repo
- **State** (the "database" of what's deployed) has tiered backends:
  - Free: local filesystem (`terraform.tfstate`, `.pulumi/`)
  - Mid: self-managed remote (S3, GCS, Azure Blob, PostgreSQL)
  - Pro: managed cloud service (HCP Terraform, Pulumi Cloud)
- Same CLI binary, `login` or config block switches backend
- Config never moves; only state management scales up

**Sync mechanism:**
- State locking (DynamoDB for S3, built-in for Cloud)
- Versioned state with rollback capability
- Transactional checkpointing (Pulumi Cloud)
- No reconciliation needed -- state IS the database

**Multi-tenancy:**
- Terraform Cloud: Organizations -> Projects -> Workspaces
- Pulumi Cloud: Organizations -> Projects -> Stacks
- Granular RBAC per workspace/stack
- Team-based access scoping

**Migration path:**
- Terraform: change `backend {}` block, run `terraform init -migrate-state`
- Pulumi: `pulumi stack export > state.json`, `pulumi login <new-backend>`, `pulumi stack import < state.json`
- Clean, well-documented, reversible

**Strengths:** Clean separation (config vs state), smooth upgrade path, same developer experience
**Weaknesses:** State is opaque (not human-readable at scale), vendor lock-in on state format

---

### Pattern 3: "YAML Definition, Tier-Gated Execution" (GitLab, Nx)

**How it works:**
- Configuration always lives in repo (`.gitlab-ci.yml`, `nx.json`)
- The **runner/executor** is where tier differentiation happens
- Free: basic execution, limited compute/storage
- Premium: more compute, advanced pipeline features, remote caching
- Ultimate/Enterprise: security scanning, compliance, distributed execution

**Sync mechanism:**
- No sync needed between repo config and service -- config is read at execution time
- Pipeline metadata, artifacts, cache stored server-side
- GitLab: PostgreSQL for metadata, object storage for artifacts
- Nx: managed or self-hosted cache servers with OpenAPI spec

**Multi-tenancy:**
- GitLab: Groups -> Projects, tier-based feature gating
- Nx Cloud: Organizations -> Workspaces, token-based cache isolation

**Migration path:**
- Config stays the same; add `cloud {}` block or change runner config
- No data migration -- just enable the service
- GitLab: same YAML works on free, premium, or ultimate

**Strengths:** Zero config change needed, pure feature gating, no storage migration
**Weaknesses:** Lock-in on execution platform, less flexibility for self-hosting

---

### Pattern 4: "Database-Primary with YAML as Ingestion Channel" (Port.dev, Datadog, Harness IDP)

**How it works:**
- Database/API is the primary store and source of truth
- YAML files in repos are ONE of several ingestion channels (alongside API, UI, integrations)
- No pretense that YAML is authoritative -- it's a convenient input format
- Blueprints/data model defined in the platform, not in YAML

**Sync mechanism:**
- GitOps: `port.yml` or `service.datadog.yaml` ingested on commit
- API: direct POST/PUT to platform endpoints
- Integrations: automated discovery from SCM, CI/CD, cloud providers
- JQ-based mapping transforms (Port) for flexible data extraction
- Cron-based sync pipelines (Harness)

**Multi-tenancy:**
- Fully managed SaaS, built-in multi-tenancy
- No self-hosted OSS option (or very limited)
- RBAC at entity/blueprint level

**Migration path:**
- From Backstage YAML: Harness auto-converts `catalog-info.yaml`
- From nothing: UI-first, no YAML required
- YAML can be adopted incrementally for GitOps workflows

**Strengths:** Real-time, no ingestion lag, flexible data model, multi-source aggregation
**Weaknesses:** No OSS self-hosted option, vendor lock-in, YAML is second-class citizen

---

### Pattern 5: "Repo Config + Cloud Dashboard Aggregation" (Snyk, Dependabot)

**How it works:**
- Config files in repo define per-repo policy (`.snyk`, `dependabot.yml`)
- Cloud dashboard aggregates across all repos for org-wide visibility
- CLI can both read local config and push to cloud
- `snyk monitor` = bridge from local to cloud

**Sync mechanism:**
- Dependabot: GitHub reads `dependabot.yml` on schedule, creates PRs
- Snyk: CLI reads `.snyk` for local policy, `snyk monitor` uploads to cloud dashboard
- Cloud-to-repo: automated PRs for dependency updates

**Multi-tenancy:**
- Organization -> Projects/repos
- Cloud dashboard provides cross-repo aggregation
- Free tier = limited repos/scans; paid = unlimited + priority features

**Migration path:**
- Start with repo config only (free)
- Add cloud dashboard for visibility (pro)
- Add org-wide policies from dashboard (enterprise)

**Strengths:** Familiar file-in-repo DX, centralized visibility, incremental adoption
**Weaknesses:** Two sources of truth risk, config drift between local and cloud policies

---

## Cross-Cutting Findings

### The Source of Truth Question

The fundamental architectural decision is: **where does authority live?**

| Approach | Authority | Database Role | Examples |
|----------|-----------|---------------|----------|
| Repo-first | Git/YAML files | Cache/index | Backstage, Cortex, Dependabot |
| State-as-DB | Repo has config, service has state | Primary (state) | Terraform, Pulumi |
| DB-first | Platform database | Primary (all data) | Port.dev, OpsLevel, Harness IDP |
| Hybrid | Split (config in repo, metadata in DB) | Co-primary | Snyk, Datadog, Harness (hybrid mode) |

### Common Tier Escalation Strategy

```
Free/OSS Tier          Mid Tier              Enterprise Tier
-----------------      -----------------     -----------------
Local files            Self-hosted backend   Managed SaaS
Single user            Team collaboration    Org-wide governance
No sync needed         State locking         RBAC + audit + SSO
Manual management      API access            Policy-as-code
                       Basic auth            Multi-tenancy
```

### The Reconciliation Spectrum

From simplest to most complex:

1. **No reconciliation** (Terraform/Pulumi): config and state are separate concerns
2. **One-way ingestion** (Backstage, Cortex): YAML -> DB, never DB -> YAML
3. **Bidirectional with primary** (Snyk): repo config is primary, cloud enriches
4. **Multi-source aggregation** (Port, Datadog): DB is primary, multiple inputs converge

### Key Insight: The "Backend Swap" Pattern

The cleanest open-core storage pattern is **backend swappable, interface identical**:
- Same CLI/API commands work regardless of backend
- `login` or config block changes the storage tier
- No data model changes between tiers
- Migration is export/import, not schema transformation

This is what Terraform and Pulumi do. Backstage approximates it (same catalog model, different hosting). Port/OpsLevel skip it entirely (SaaS-only from the start).

### Key Insight: YAML Sprawl is the Growth Signal

Tools that start with YAML-in-repo consistently face the same scaling challenge:
- 10 repos: YAML works great
- 100 repos: need automation to keep YAML consistent
- 1000 repos: need a database to aggregate, search, and enforce standards
- This scaling pain IS the enterprise sales motion

### Key Insight: The Three Things That Move to the Service

Across all tools, the same three capabilities consistently move from local to service tier:

1. **State/aggregation** -- cross-repo/cross-team visibility
2. **Collaboration** -- locking, RBAC, audit trails
3. **Policy enforcement** -- compliance, standards, automated governance

Configuration/definition almost never moves. It stays in the repo.

---

## Relevance to RaiSE

The RaiSE CLI currently uses YAML/files in `.raise/` for all configuration. Key takeaways for a potential Pro/Enterprise tier:

1. **Keep definitions in `.raise/`** -- this is the Terraform/Pulumi pattern. Config stays local.
2. **State/aggregation is the Pro play** -- cross-repo pattern propagation, team dashboards, backlog sync status.
3. **Backend swap via `rai login`** -- same CLI commands, different storage backend (local files vs hosted service).
4. **One-way ingestion for catalog** -- `.raise/` YAML ingested into a service DB for aggregation, never the reverse.
5. **YAML remains source of truth for single-repo** -- the service adds cross-repo intelligence, not per-repo authority.

---

## Confidence Assessment

| Finding | Confidence | Basis |
|---------|------------|-------|
| Backend-swap pattern (Terraform/Pulumi) is the cleanest open-core storage model | **Very High** | Direct documentation from both tools, widely adopted |
| YAML-as-source-of-truth + DB-as-cache is the dominant service catalog pattern | **High** | Backstage (dominant OSS), Cortex, confirmed by multiple sources |
| DB-primary tools (Port, OpsLevel) don't offer OSS tiers | **High** | Multiple comparison sources, product pages |
| Enterprise value is in aggregation/collaboration, not per-repo config | **Very High** | Consistent across all 7+ tools studied |
| Migration from file-based to service-based is export/import, not schema change | **High** | Terraform and Pulumi document this explicitly; Backstage migration is operational |
| Self-hosted cache monetization is contentious (Nx backlash) | **Medium** | Single source (Medium article), but well-documented community discussion |
