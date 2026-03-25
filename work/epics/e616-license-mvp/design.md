# E616: raise-server License MVP — Design

## Gemba (Current State)

raise-server is a FastAPI application with:
- **DB**: PostgreSQL 16 via SQLAlchemy 2.0 async + Alembic (2 migrations)
- **Auth**: API key (SHA-256 hash, per-org, `Bearer rsk_...`)
- **Tables**: organizations, api_keys, graph_nodes, graph_edges, agent_events, memory_patterns
- **Endpoints**: health, graph (sync/query), memory (patterns), agent (events)
- **Deploy**: Docker multi-stage + docker-compose (postgres + server)
- **Pattern**: thin routers → services → queries. Stateless services, session_factory injected.
- **Config**: pydantic-settings, `RAI_*` env vars

No license or member infrastructure exists. `api_keys` is a flat table with no
user identity — just org-level auth tokens.

## Key Insight: Always-Connected Model

raise-pro **requires** raise-server for its core features (cross-repo graphs,
governance, shared memory). There is no disconnected scenario — if you can't
reach the server, pro features don't work regardless of licensing.

This eliminates the need for offline JWT validation, embedded public keys,
and client-side crypto. **The server validates the license on every request**
as part of the auth flow.

Enterprise clients get an **on-prem** server, not a disconnected client.

## Vision: Organization → Members → Permissions

### MVP (E616)

```
Organization
  ├── License (plan=pro, features=[...], seats=5, expires_at)
  └── Members (email, role, api_key)
       └── all inherit org plan features
```

### V2 (future)

```
Organization
  ├── License (plan=enterprise)
  ├── Members
  │    ├── member_features (per-member override)
  │    └── roles (admin, developer, viewer, billing)
  └── Admin Console (web UI for all of this)
```

### Enterprise (future)

```
Organization
  ├── SSO/SAML integration
  ├── Per-member feature granularity
  ├── Audit log
  └── On-prem server deployment
```

## Target Components

### New: `raise_server.db.models.MemberRow`

Replaces `api_keys` table. Each member = one human with their own API key.

```
members table:
  id          UUID PK
  org_id      FK → organizations
  email       String(255)         -- unique per org
  name        String(255)
  role        String(20)          -- "admin", "member"
  key_hash    String(128)         -- SHA-256 of API key (was in api_keys)
  key_prefix  String(12)          -- first 12 chars for identification
  is_active   Boolean
  created_at  DateTime(tz)
  updated_at  DateTime(tz)

  unique constraint: (org_id, email)
```

### New: `raise_server.db.models.LicenseRow`

```
licenses table:
  id          UUID PK
  org_id      FK → organizations  -- unique (one active license per org)
  plan        String(20)          -- "pro", "team", "enterprise"
  features    JSONB               -- ["jira", "confluence", "odoo", "gitlab"]
  seats       Integer             -- max active members
  status      String(20)          -- "active", "expired", "revoked"
  expires_at  DateTime(tz)
  created_at  DateTime(tz)
  updated_at  DateTime(tz)
```

### Modified: `raise_server.auth`

Current `verify_api_key` returns `OrgContext(org_id, org_name)`.
New `verify_member` returns `MemberContext(org_id, org_name, member_id, email, role, plan, features)`.

The auth flow becomes:
```
Bearer rsk_xxx
  → hash key → lookup in members (not api_keys)
  → load org
  → load active license for org
  → return MemberContext with plan + features
```

### New: `raise_server.middleware.license`

Plan-check middleware or dependency:
```python
def requires_plan(minimum: str) -> Depends:
    """FastAPI dependency that checks member's org has sufficient plan."""
    ...
```

Endpoints annotate their required plan:
```python
@router.post("/sync")
async def graph_sync(ctx: Annotated[MemberContext, Depends(requires_plan("team"))]):
    ...
```

### New: `raise_server.services.license`

Service layer:
- `generate_license(session_factory, org_id, plan, features, seats, expires_at) → LicenseInfo`
- `check_license(session_factory, org_id) → LicenseStatus`
- `create_member(session_factory, org_id, email, name, role) → MemberInfo` (returns raw API key once)

### New: `raise_server.api.v1.admin`

Router `/api/v1/admin` (requires admin role):
- `POST /license/generate` — create/update license for an org
- `POST /members` — create member, returns API key
- `GET /members` — list org members
- `DELETE /members/{id}` — deactivate member

### Modified: `raise_server.app.create_app`

Register new router: `admin_router`. Swap `verify_api_key` dependency for
`verify_member` across all existing routers.

## Key Contracts

### Auth Flow (all endpoints)

```
Request: Authorization: Bearer rsk_abc123...

→ Server resolves:
  member = lookup(hash(rsk_abc123))
  org = member.org
  license = org.active_license

→ Returns MemberContext:
  {
    "org_id": "uuid",
    "org_name": "humansys",
    "member_id": "uuid",
    "email": "emilio@humansys.ai",
    "role": "admin",
    "plan": "pro",
    "features": ["jira", "confluence", "odoo", "gitlab"]
  }

→ Plan check:
  endpoint requires "pro" → member.plan == "pro" → ✓ 200
  endpoint requires "team" → member.plan == "pro" → ✗ 403
```

### POST /api/v1/admin/license/generate (admin only)

```
Request:
  {
    "org_id": "uuid",     -- optional, defaults to caller's org
    "plan": "pro",
    "features": ["jira", "confluence", "odoo", "gitlab"],
    "seats": 5,
    "expires_at": "2027-03-25T00:00:00Z"
  }

Response 201:
  {
    "id": "uuid",
    "plan": "pro",
    "features": ["jira", "confluence", "odoo", "gitlab"],
    "seats": 5,
    "status": "active",
    "expires_at": "2027-03-25T00:00:00Z"
  }
```

### POST /api/v1/admin/members (admin only)

```
Request:
  {
    "email": "fernando@humansys.ai",
    "name": "Fernando",
    "role": "member"
  }

Response 201:
  {
    "id": "uuid",
    "email": "fernando@humansys.ai",
    "role": "member",
    "api_key": "rsk_xxxxxxxx..."   ← shown ONCE, never again
  }
```

### 403 Response (insufficient plan)

```
{
  "detail": "This feature requires the 'team' plan. Current plan: 'pro'. Contact your admin.",
  "required_plan": "team",
  "current_plan": "pro",
  "upgrade_url": "https://raise.dev/pricing"
}
```

## Architectural Decisions

### D1: Always-connected — no offline JWT

raise-pro requires server connectivity for its features (graphs, governance).
License validation happens server-side on every request. No client-side crypto,
no embedded keys, no JWT files. Simplifies both server and client.

**Trade-off:** No offline grace period. If server is down, pro features are down.
Acceptable because those features need the server anyway.

### D2: Members replace api_keys

Instead of adding a separate identity layer, `members` absorbs `api_keys` with
added fields (email, name, role). Migration renames and adds columns.
One API key per member. Admin creates members, gets raw key once.

**Trade-off:** Breaking change for existing API keys. Mitigated by migration
that preserves existing keys as "admin" members with placeholder emails.

### D3: Plan hierarchy is linear

`community < pro < team < enterprise`. A `team` plan includes all `pro` features.
No need for set intersection — simple ordinal comparison.

```python
PLAN_RANK = {"community": 0, "pro": 1, "team": 2, "enterprise": 3}

def has_plan(current: str, required: str) -> bool:
    return PLAN_RANK.get(current, 0) >= PLAN_RANK.get(required, 0)
```

### D4: One active license per org

MVP constraint. No license stacking, no multiple concurrent plans.
Simplifies queries: `WHERE org_id = ? AND status = 'active' LIMIT 1`.

### D5: Seat enforcement is member count

`seats` = max active members in the org. Checked at member creation time,
not at request time. If seat limit is 5 and there are 5 active members,
`POST /admin/members` returns 409 until a member is deactivated.

## Story Breakdown (Revised)

### S616.1: Migration + models (members, licenses) (S)

Migration 003: `members` table (absorbing `api_keys`), `licenses` table.
SQLAlchemy models. Pydantic schemas. Data migration for existing api_keys → members.

**Size:** S
**Dependencies:** None

### S616.2: Auth refactor + license middleware (M)

Replace `verify_api_key` with `verify_member`. New `MemberContext` with plan/features.
`requires_plan()` dependency for endpoint-level plan checks. Update all existing
routers to use new auth. License service: check_license, generate_license.

**Size:** M (touches all routers, but changes are mechanical)
**Dependencies:** S616.1

### S616.3: Admin API + seed (S)

`/api/v1/admin` router: generate license, CRUD members. Seed script for first
client org + license + admin member. Deployment docs update.

**Size:** S
**Dependencies:** S616.2

## Dependency Graph

```
S616.1 (migration/models)
    ↓
S616.2 (auth refactor + license check)
    ↓
S616.3 (admin API + seed)
```

3 stories, linear chain. Each independently testable.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| api_keys → members migration breaks existing clients | Medium | High | Migration preserves key hashes. Existing keys become admin members with placeholder email. Test with current seed data. |
| Auth refactor touches all endpoints | Low | Medium | Mechanical change: swap dependency type. All endpoints already use `Annotated[OrgContext, Depends(...)]` — change to `MemberContext`. Run full test suite after. |
| Seat counting at creation vs request time | Low | Low | MVP simplification. If admin deactivates member but they still have cached key, key lookup returns `is_active=False` → 401. |

## Deferred (Parking Lot → V2+)

- **Admin web console** — CRUD members, manage licenses, view usage (promote when >5 clients)
- **Per-member feature override** — granular entitlements per member (promote for enterprise)
- **SSO/SAML integration** — enterprise auth (promote when enterprise client requests)
- **Roles beyond admin/member** — viewer, billing, etc. (promote when needed)
- **Phone-home / usage telemetry** — track which features are used (promote for billing)
- **License revocation with grace period** — soft revoke with warning (promote when >20 clients)
- **Self-service member invitation** — email invite flow (promote when admin console exists)
- **On-prem deployment guide** — enterprise self-hosted (promote for first enterprise client)

## Plan Hierarchy Reference

| Plan | Includes | Target |
|------|----------|--------|
| community | raise-cli (no server, no license) | OSS users |
| pro | + Jira, Confluence, Odoo, GitLab adapters | Small teams |
| team | + raise-server (governance, metrics, cross-repo graphs) | Teams with multiple repos |
| enterprise | + raise-agent, SSO, audit, per-member permissions, on-prem | Large orgs |
