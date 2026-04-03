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
- **Users**: Zero. PoC only. No data to migrate.

## Key Insight: Always-Connected Model

raise-pro **requires** raise-server for its core features (cross-repo graphs,
governance, shared memory). No disconnected scenario exists.

License validation happens server-side on every request as part of auth flow.
No offline JWT, no embedded keys, no client-side crypto.

Enterprise clients get an **on-prem** server, not a disconnected client.

## Vision: Organization → Members → Permissions

### MVP (E616)

```
Organization
  ├── License (plan=pro, features=[...], seats=5, expires_at)
  └── Members (email, name, role)
       ├── API Keys (N per member, scopes, show-once)
       └── all inherit org plan features
```

### V2 (future)

```
Organization
  ├── License (plan=enterprise)
  ├── Members
  │    ├── member_features (per-member override)
  │    └── roles (admin, developer, viewer, billing)
  └── Admin Console (web UI)
```

### Enterprise (future)

```
Organization
  ├── SSO/SAML integration
  ├── Per-member feature granularity
  ├── Audit log API
  └── On-prem server deployment
```

## Data Model

### `organizations` (exists, unchanged)

```
id          UUID PK
name        String(255)
slug        String(63) unique
created_at  DateTime(tz)
```

### New: `members`

```
members:
  id          UUID PK
  org_id      FK → organizations
  email       String(255)
  name        String(255)
  role        String(20)          -- "admin" | "member"
  is_active   Boolean DEFAULT true
  deleted_at  DateTime(tz) NULL   -- soft delete
  created_at  DateTime(tz)
  updated_at  DateTime(tz)

  UNIQUE (org_id, email)
```

### New: `api_keys`

Separate from members. One member can have N keys (CLI, CI, etc.).

```
api_keys:
  id          UUID PK
  member_id   FK → members
  org_id      FK → organizations  -- denormalized for fast auth lookup
  key_hash    String(128)         -- SHA-256
  key_prefix  String(12)          -- for identification in logs
  scopes      JSONB DEFAULT '["full_access"]'
  last_used_at DateTime(tz) NULL
  is_active   Boolean DEFAULT true
  created_at  DateTime(tz)

  INDEX (key_hash)               -- primary lookup path
```

### New: `licenses`

One active license per org (MVP constraint).

```
licenses:
  id          UUID PK
  org_id      FK → organizations
  plan        String(20)          -- "pro" | "team" | "enterprise"
  features    JSONB               -- ["jira", "confluence", "odoo", "gitlab"]
  seats       Integer             -- max active members
  status      String(20)          -- "active" | "expired" | "revoked"
  expires_at  DateTime(tz)
  created_at  DateTime(tz)
  updated_at  DateTime(tz)
```

### Dropped: old `api_keys`

Zero users — drop and recreate clean. No migration needed.

## Auth Flow

```
Bearer rsk_xxx
  → SHA-256(rsk_xxx)
  → lookup api_keys WHERE key_hash = ? AND is_active = true
  → load member (WHERE is_active AND deleted_at IS NULL)
  → load org
  → load license (WHERE org_id = ? AND status = 'active')
  → return MemberContext(org_id, org_name, member_id, email, role, plan, features)
  → update api_keys.last_used_at
```

## API Surface (V1)

### URL Design

Resource-nested under organization. No `/admin/` prefix — authorization
lives in middleware via role checks, not URL structure.

### Organizations (5 endpoints)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/organizations` | superadmin | Create org |
| GET | `/api/v1/organizations` | superadmin | List all orgs |
| GET | `/api/v1/organizations/{id}` | member (own org) | Org details |
| PATCH | `/api/v1/organizations/{id}` | admin | Update name/settings |
| DELETE | `/api/v1/organizations/{id}` | superadmin | Soft delete |

### Members (4 endpoints)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/organizations/{id}/members` | admin | Create member |
| GET | `/api/v1/organizations/{id}/members` | admin | List members |
| PATCH | `/api/v1/organizations/{id}/members/{mid}` | admin | Update role |
| DELETE | `/api/v1/organizations/{id}/members/{mid}` | admin | Soft delete |

### API Keys (3 endpoints)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/organizations/{id}/api-keys` | admin or self | Create, raw key shown ONCE |
| GET | `/api/v1/organizations/{id}/api-keys` | admin | List metadata (never raw key) |
| DELETE | `/api/v1/organizations/{id}/api-keys/{kid}` | admin or owner | Hard delete (revoke) |

### License (2 endpoints)

| Method | Path | Auth | Notes |
|--------|------|------|-------|
| POST | `/api/v1/organizations/{id}/license` | superadmin | Create/replace license |
| GET | `/api/v1/organizations/{id}/license` | member (own org) | Current license info |

### Existing (unchanged paths, new auth)

| Method | Path | Plan Required |
|--------|------|---------------|
| GET | `/health` | none (public) |
| POST | `/api/v1/graph/sync` | team |
| GET | `/api/v1/graph/query` | team |
| POST | `/api/v1/memory/patterns` | team |
| GET | `/api/v1/memory/patterns` | team |
| POST | `/api/v1/agent/events` | team |
| GET | `/api/v1/agent/events` | team |

**Total: 15 new + 7 updated = 22 endpoints**

## Key Contracts

### Auth: MemberContext

```python
class MemberContext(BaseModel):
    org_id: uuid.UUID
    org_name: str
    member_id: uuid.UUID
    email: str
    role: str           # "admin" | "member"
    plan: str           # "pro" | "team" | "enterprise" | "community"
    features: list[str] # ["jira", "confluence", ...]
```

### Plan Check Dependency

```python
PLAN_RANK = {"community": 0, "pro": 1, "team": 2, "enterprise": 3}

def requires_plan(minimum: str):
    """FastAPI dependency — returns 403 if plan insufficient."""
    async def check(ctx: MemberContext = Depends(verify_member)):
        if PLAN_RANK.get(ctx.plan, 0) < PLAN_RANK.get(minimum, 0):
            raise HTTPException(403, detail={
                "message": f"Requires '{minimum}' plan. Current: '{ctx.plan}'.",
                "required_plan": minimum,
                "current_plan": ctx.plan,
            })
        return ctx
    return Depends(check)
```

### Role Check Dependency

```python
def requires_role(role: str):
    """FastAPI dependency — returns 403 if role insufficient."""
    ...
```

### POST /organizations/{id}/members → 201

```json
{
  "id": "uuid",
  "email": "fernando@humansys.ai",
  "name": "Fernando",
  "role": "member",
  "api_key": "rsk_xxxxxxxx..."   // shown ONCE
}
```

### POST /organizations/{id}/api-keys → 201

```json
{
  "id": "uuid",
  "key": "rsk_xxxxxxxx...",      // shown ONCE
  "prefix": "rsk_xxxxxxxx",
  "scopes": ["full_access"],
  "created_at": "2026-03-25T..."
}
```

### GET /organizations/{id}/api-keys → 200

```json
{
  "data": [
    {
      "id": "uuid",
      "prefix": "rsk_xxxxxxxx",
      "scopes": ["full_access"],
      "last_used_at": "2026-03-25T...",
      "created_at": "2026-03-25T..."
    }
  ]
}
```

Note: raw key NEVER in GET responses.

### 403 (insufficient plan)

```json
{
  "message": "Requires 'team' plan. Current: 'pro'.",
  "required_plan": "team",
  "current_plan": "pro"
}
```

## Architectural Decisions

### D1: Always-connected — no offline JWT

raise-pro requires server for features. License validated server-side
on every request. No client-side crypto.

### D2: API keys separate from members

A member can have multiple keys (CLI, CI, different scopes).
Universal pattern across GitLab, Keygen, Temporal, PostHog.
Keys have their own lifecycle (create show-once → list metadata → revoke).

### D3: Resource-nested URLs, no /admin/ prefix

`/organizations/{id}/members`, not `/admin/members`.
Authorization via role in middleware, not URL structure.
Matches GitLab, Clerk, WorkOS, PostHog patterns.

### D4: Plan hierarchy is linear

`community < pro < team < enterprise`. Simple ordinal comparison.
No set intersection needed.

### D5: Soft delete for members/orgs, hard delete for API keys

Members and orgs use `deleted_at` timestamp (recoverable, audit trail).
API keys use hard delete (security — no resurrection of revoked keys).

### D6: Scopes on API keys from day 1

V1 only has `full_access` scope, but the `scopes` JSONB field exists
from the start. Retrofitting scopes onto existing keys is painful.

### D7: One active license per org

MVP constraint. No stacking. Simplifies to:
`WHERE org_id = ? AND status = 'active' LIMIT 1`.

### D8: Seat enforcement at member creation

`seats` = max active members. Checked when creating member (409 on limit).
Not at request time — simpler, fewer queries per request.

## Deferred (V2+)

- Admin web console (promote when >5 clients)
- Per-member feature override (promote for enterprise)
- SSO/SAML (promote when enterprise client requests)
- Roles beyond admin/member (promote when needed)
- API key rotation endpoint (manual revoke+create works for <10 clients)
- Email invitation flow (admin-managed onboarding is fine early)
- Audit log API (log internally from day 1, expose API later)
- Bulk operations (not needed at small scale)
- Undelete endpoints (admin can restore via DB)
- Self-service org creation (admin-managed is safer early)
- Cursor pagination (offset acceptable for <10 clients, cursor for V2)

## Plan Hierarchy Reference

| Plan | Includes | Target |
|------|----------|--------|
| community | raise-cli (no server, no license) | OSS users |
| pro | + Jira, Confluence, Odoo, GitLab adapters | Small teams |
| team | + raise-server (governance, metrics, cross-repo graphs) | Teams with multiple repos |
| enterprise | + raise-agent, SSO, audit, per-member permissions, on-prem | Large orgs |
