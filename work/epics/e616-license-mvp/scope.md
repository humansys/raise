# E616: raise-server License MVP — Scope

**Jira:** RAISE-616
**Labels:** pro-launch, v2.4
**Branch:** dev (stories branch from dev)
**Depends on:** None (E621 depends on this)
**Design:** [design.md](design.md)

## Objective

Add server-side license and member management to raise-server. Organizations
have a plan (pro/team/enterprise), members inherit plan features, and the
server enforces plan requirements on every request.

## In Scope

- Alembic migration 003: `members` (absorbing `api_keys`) + `licenses` tables
- `MemberContext` auth replacing `OrgContext` (member-aware, plan-aware)
- `requires_plan()` dependency for endpoint plan enforcement
- License service: generate, check
- Admin API: generate license, CRUD members
- Seed script for first client org + license + admin member
- Deployment docs update

## Out of Scope

- Offline JWT / client-side crypto (always-connected model)
- CLI commands (`rai activate`, etc.) — that's E621
- Entry point gating / graceful degradation — that's E621
- Admin web console (seed via API/SQL for now)
- Per-member feature override (V2, enterprise)
- SSO/SAML (enterprise)
- Phone-home / usage telemetry
- Payment/billing integration

## Stories

### S616.1: Migration + models (members, licenses) (S)

Migration 003: `members` table (absorbs `api_keys` with email, name, role),
`licenses` table (org plan, features, seats, status, expiry). Data migration
for existing api_keys → members. SQLAlchemy models + Pydantic schemas.

**Dependencies:** None

### S616.2: Auth refactor + license middleware (M)

Replace `verify_api_key` → `verify_member`. `MemberContext` includes plan
and features from org's active license. `requires_plan(minimum)` dependency
for endpoint-level plan checks. License service. Update all existing routers.

**Dependencies:** S616.1

### S616.3: Admin API + seed (S)

`/api/v1/admin` router: `POST /license/generate`, `POST /members`,
`GET /members`, `DELETE /members/{id}`. Seed script for first client.
Deployment docs.

**Dependencies:** S616.2

## Done Criteria

- [ ] `members` and `licenses` tables exist via migration 003
- [ ] Existing api_keys migrated to members (no broken auth)
- [ ] `MemberContext` includes plan + features on every request
- [ ] Endpoints enforce plan requirements via `requires_plan()`
- [ ] Insufficient plan → 403 with clear message + upgrade hint
- [ ] Admin can generate licenses via API
- [ ] Admin can create/list/deactivate members via API
- [ ] Seat limit enforced at member creation
- [ ] First client org + license + admin member seeded
- [ ] raise-server deployed with new schema

## Dependency Graph

```
S616.1 (migration/models)
    ↓
S616.2 (auth refactor + license check)
    ↓
S616.3 (admin API + seed)
```

## Progress Tracking

| Story | Status | Notes |
| ----- | ------ | ----- |
| S616.1 Migration + models | pending | |
| S616.2 Auth + license middleware | pending | |
| S616.3 Admin API + seed | pending | |
