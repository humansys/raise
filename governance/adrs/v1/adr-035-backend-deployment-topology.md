---
id: "ADR-035"
title: "Backend Deployment Topology — Adapter execution contexts across COMMUNITY, PRO, and ENTERPRISE"
date: "2026-02-19"
status: "Accepted"
---

# ADR-035: Backend Deployment Topology

## Context

ADR-033 and ADR-034 define the adapter Protocol contracts and entry point discovery mechanism.
Both assume a single execution context: the developer's machine. The `rai-cli` process
discovers adapters via Python entry points and calls them locally.

This assumption breaks down as soon as we introduce PRO (cloud-hosted backend) and
ENTERPRISE (self-hosted backend). Three problems emerge:

1. **Server-side-only adapters:** `TriggerAdapter` requires a public HTTPS endpoint to receive
   webhooks from Jira, GitHub, etc. A developer's laptop cannot serve webhooks. This adapter
   has no local deployment option.

2. **Org-level credentials:** In PRO and ENTERPRISE, Jira/Confluence credentials should be
   managed centrally by an admin — not distributed to every developer's machine. A
   `JiraBacklogParser` running on each developer's laptop requires each developer to hold
   org-level API tokens.

3. **Team aggregation:** `rai memory build` for shared team memory must aggregate data
   across all team members. This aggregation cannot happen on a single developer's machine —
   it requires a central process with access to all session data.

Two constraints shape the decision:

1. **COMMUNITY must work with zero backend** — no server required, no account, no internet
   connection beyond what the developer's LLM API key needs. Local-first is non-negotiable.

2. **ENTERPRISE requires full data sovereignty** — for regulated industries (banking, CNBV),
   no data can leave the organization's network. The backend must be deployable on-premise,
   including the adapters that call Jira and Confluence.

## Decision

### 1. Three deployment modes — same CLI, different backend configuration

The CLI is identical across all tiers. What changes is the presence and location of a backend.

```
COMMUNITY (no backend):
  dev → rai-cli → [local adapters via entry points] → external APIs
                → [local knowledge graph]

PRO (cloud backend):
  dev → rai-cli → [local adapters] → external APIs     ← client-side adapters
                ↘
                  backend.humansys.ai → [server adapters] → Jira, Confluence, etc.
                                      → [team knowledge graph on Supabase]

ENTERPRISE (self-hosted backend):
  dev → rai-cli → [local adapters] → external APIs     ← client-side adapters
                ↘
                  backend.acme.com  → [server adapters] → Jira on-prem, Confluence on-prem
  (all traffic stays inside the org's network)         → [team knowledge graph on customer DB]
```

Backend presence is configured in `.raise/manifest.yaml`:

```yaml
# COMMUNITY — no backend section
ide:
  type: claude

# PRO / ENTERPRISE — backend section present
ide:
  type: claude
backend:
  url: "https://api.humansys.ai"      # PRO
  # url: "https://rai.acme.com"       # ENTERPRISE
  auth: token                          # resolved from .raise/adapters/.backend-token (gitignored)
```

If `backend` is absent from manifest, the CLI operates fully local. No fallback, no error —
COMMUNITY is a first-class mode, not a degraded PRO.

---

### 2. Adapter execution contexts — client-side vs. server-side

Every adapter Protocol from ADR-033/034 has a natural execution context. Some adapters
belong exclusively on the client (developer's machine), others belong on the server, and
some can run in either context depending on deployment mode.

| Adapter | COMMUNITY | PRO | ENTERPRISE | Rationale |
|---|---|---|---|---|
| `GovernanceParser` (local files) | Client | Client | Client | Reads developer's local `.raise/` |
| `LocalMarkdownTarget` | Client | Client | Client | Writes to developer's local files |
| `CodeReviewAdapter` | Client | Client | Client | Creates PRs from developer's branch |
| `CICDAdapter` | Client | Client | Client | Checks pipelines for current branch |
| `JiraBacklogParser` | — | **Server** | **Server** (on-prem) | Org credentials, team aggregation |
| `ConfluenceTarget` | — | **Server** | **Server** (on-prem) | Org credentials, hierarchy config |
| `ProjectManagementAdapter` | — | **Server** | **Server** (on-prem) | Team-visible operations |
| `TriggerAdapter` | — | **Server only** | **Server** (on-prem) | Requires public/internal endpoint |
| `NotificationAdapter` | — | **Server** | **Server** (on-prem) | Team-level events, central aggregation |

**Rule of thumb:**
- Client-side: operates on the developer's current work (branch, local files, PR)
- Server-side: operates on org-level resources or requires receiving external events

---

### 3. CLI proxy pattern — how client talks to server adapters

The CLI does not install server-side adapters locally. Instead, it calls the backend through
a typed proxy API. The Protocol contracts (ADR-034) remain the same — only the transport
changes.

```
COMMUNITY (entry points, local):
  registry = get_governance_parsers()         # importlib.metadata entry_points()
  nodes = registry["local"].parse(locator)

PRO/ENTERPRISE (backend proxy):
  registry = get_governance_parsers()         # discovers BOTH local + backend
  nodes = registry["jira"].parse(locator)     # → HTTP POST /adapters/governance/parse
```

The backend exposes a unified adapter proxy API surface:

```
POST /adapters/governance/parse        → GovernanceParser.parse()
POST /adapters/governance/schemas      → GovernanceSchemaProvider.locate()
POST /adapters/docs/publish            → DocumentationTarget.publish()
POST /adapters/pm/{operation}          → ProjectManagementAdapter.*()
POST /adapters/triggers/register       → TriggerAdapter.listen()
GET  /adapters/list                    → all available server-side adapters
```

The CLI adapter registry is extended to include backend adapters when a backend is
configured. From the caller's perspective, a local `JiraBacklogParser` and a
backend-proxied `JiraBacklogParser` are indistinguishable — same Protocol, same call site.

---

### 4. Authentication model

Credentials flow differently depending on deployment mode:

**COMMUNITY:**
- Developer manages own API keys locally
- Stored in `.raise/adapters/<name>.yaml` (gitignored)
- No central management

**PRO (cloud):**
- Org admin configures Jira/Confluence credentials in humansys.ai backend once
- Developers authenticate to the backend (not to Jira directly) via a team token
- Backend holds org credentials — developers never see them
- BYOK for inference (developer's own LLM key) stays local

**ENTERPRISE (self-hosted):**
- Same model as PRO, but backend runs on customer infrastructure
- Org credentials stored in customer's secret manager (Vault, AWS SM, Azure Key Vault)
- Connects to `SecretManagerAdapter` concept (ADR-034 §Extension Points Futuros)
- No credential leaves the org's network

```
COMMUNITY:  dev machine → [local creds] → Jira
PRO:        dev machine → [team token] → humansys.ai backend → [org creds] → Jira
ENTERPRISE: dev machine → [team token] → on-prem backend → [vault] → Jira on-prem
```

---

### 5. Enterprise self-hosted deployment

The backend is packaged for self-hosted deployment with two options:

**Option A — Docker Compose (small teams, <50 devs)**

```yaml
# docker-compose.yml (distributed with ENTERPRISE license)
services:
  rai-backend:
    image: registry.humansys.ai/rai-backend:latest
    environment:
      DATABASE_URL: postgres://...
      SECRET_BACKEND: vault  # or: env, aws_sm, azure_kv
    ports:
      - "8443:8443"

  postgres:
    image: postgres:16
    volumes:
      - rai-data:/var/lib/postgresql/data
```

**Option B — Helm chart (large enterprises, air-gapped environments)**

```bash
helm install rai-backend oci://registry.humansys.ai/charts/rai-backend \
  --set database.url="..." \
  --set secrets.backend="vault"
```

Both options result in the same backend API surface. The CLI points to
`backend.url` in manifest.yaml — agnostic of how the backend was deployed.

**Air-gapped support:** All images pre-loaded from customer registry. No external
pulls at runtime. Required for CNBV-regulated environments (banking in Mexico).

---

### 6. Relationship between backend and raise-pro adapters

`raise-pro` is a Python package deployed on the backend, not on the developer's machine.
The developer installing `rai-cli` alone does not get PRO capabilities — the backend must
be configured and reachable.

```
raise-core (Apache 2.0, PyPI)    → installed on developer's machine
raise-pro  (commercial, private) → installed on the backend server
                                    (humansys.ai cloud OR customer on-prem)
```

The community adapter model (ADR-033) remains unchanged for client-side adapters:
anyone can `pip install raise-azuredevops-adapter` on their machine and use it in
COMMUNITY mode. Server-side community adapters (running on the backend) are a future
consideration post-V3 launch.

---

## Consequences

| Type | Impact |
|---|---|
| + | COMMUNITY stays fully local — zero backend dependency, BYOK inference |
| + | ENTERPRISE achieves full data sovereignty — no data leaves customer network |
| + | Org credentials managed centrally — developers never hold Jira/Confluence tokens |
| + | PRO and ENTERPRISE share the same backend codebase — one deployment artifact |
| + | TriggerAdapter becomes viable — backend provides the public/internal webhook endpoint |
| + | CLI is identical across tiers — backend presence is configuration, not a code fork |
| - | Server-side adapters require backend to be healthy — client degradation path needed |
| - | Backend adds operational complexity for ENTERPRISE customers (uptime, upgrades) |
| - | Backend proxy adds network latency to operations that were previously local |
| - | Air-gapped deployment requires maintaining private image registry |

**Degradation policy:** If backend is configured but unreachable, client-side adapters
continue operating. Server-side adapter calls fail with a clear error message pointing to
backend health endpoint. `rai memory build` runs with local-only data and warns that
team data is unavailable.

---

## Relationship to ADR-033 and ADR-034

```
ADR-033: Protocol contracts for PM adapters
ADR-034: Protocol contracts for governance adapters + extension points
ADR-035 (this): Where those adapters run and how the CLI reaches them

ADR-034 answers "what"   → adapter Protocols and entry points
ADR-035 answers "where"  → client vs. server, cloud vs. on-prem
```

The three ADRs together form a complete adapter architecture:
- Contracts (ADR-033/034) are deployment-agnostic
- Topology (ADR-035) determines which implementations are reachable in each tier

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| All adapters run on client (even in PRO) | Requires distributing org credentials to all developer machines; breaks TriggerAdapter |
| All adapters run on server (even in COMMUNITY) | Violates local-first requirement; adds backend dependency to free tier |
| Separate CLI binaries per tier | Maintenance overhead; confusing UX; breaks "same CLI" principle |
| gRPC instead of REST for proxy API | Added complexity for no practical gain at our scale; REST is simpler for community adapters |
| Backend only for ENTERPRISE (not PRO) | PRO shared memory requires server-side aggregation regardless; avoids hybrid model complexity |

## Open Questions

1. **Degradation UX:** When backend is unreachable, should `rai memory build` fail loudly
   or silently skip team data? Loud seems right — silent skips hide stale team context.
2. **Backend versioning:** How do we handle backend API version drift between a customer's
   on-prem deployment and the current CLI version? Semantic versioning + compatibility matrix.
3. **Local dev of server-side adapters:** How do contributors develop and test server-side
   adapters without a full backend? Docker Compose dev profile needed.
4. **Community server-side adapters:** Post-V3, should the backend support community-built
   server-side adapters (via trusted plugin mechanism)? Requires the supply-chain policy
   from ADR-034 §Open Questions to be resolved first.

---

*Status: Accepted*
*Created: 2026-02-19 (SES-223)*
*Supersedes: None*
*Extends: ADR-033, ADR-034*
*Validated by: ENTERPRISE requirement (data sovereignty for CNBV-regulated customers — Coppel, INVEX)*
