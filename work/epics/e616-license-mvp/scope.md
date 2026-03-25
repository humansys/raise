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

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Linear chain — each story builds on the previous. The risk is in S616.2
(auth refactor touches all existing endpoints), so we build the foundation
(S616.1) first and validate the migration, then tackle the riskiest story
(S616.2) while we have maximum time to course-correct.

### Story Sequence

| # | Story | Size | Rationale | Enables |
|---|-------|------|-----------|---------|
| 1 | S616.1: Migration + models | S | Foundation — tables and models must exist first | S616.2, S616.3 |
| 2 | S616.2: Auth refactor + license middleware | M | Riskiest — touches all routers, breaking change to auth flow | S616.3, E621 |
| 3 | S616.3: Admin API + seed | S | Capstone — admin endpoints + first client seed, validates E2E | Epic close |

**No parallel opportunities** — strict linear dependency chain. Each story
reads from the previous story's output (models → auth → API).

### Milestones

#### M1: Schema Ready (after S616.1)

- [ ] Migration 003 runs cleanly on existing DB
- [ ] Existing api_keys data migrated to members (zero data loss)
- [ ] `MemberRow` and `LicenseRow` models pass unit tests
- [ ] Pydantic schemas cover all API contracts
- **Demo:** `alembic upgrade head` on dev DB, query members table

#### M2: Auth Live (after S616.2) — E2E Integration Checkpoint

- [ ] All existing endpoints use `MemberContext` (not `OrgContext`)
- [ ] `requires_plan()` returns 403 with clear message for insufficient plan
- [ ] Existing graph/memory/agent endpoints still work with migrated keys
- [ ] No regression in existing functionality
- **Demo:** `curl` existing endpoints with migrated API key → 200.
  `curl` with plan-gated endpoint on community plan → 403.
- **E2E:** docker compose up, run migrations, seed data, hit all endpoints

#### M3: Epic Complete (after S616.3)

- [ ] Admin can generate license via `POST /admin/license/generate`
- [ ] Admin can create member via `POST /admin/members` (gets raw key)
- [ ] Seat limit enforced at member creation (409 on limit)
- [ ] First client org + license + admin seeded
- [ ] All done criteria met
- **Demo:** Full onboarding flow: create org → generate license → create
  member → member hits graph endpoint → 200 with pro plan

### Sequencing Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| api_keys → members migration breaks existing dev/CI setups | High | Write reversible migration. Test on copy of prod-like data first. Keep api_keys as view or alias during transition. |
| Auth refactor (S616.2) introduces regressions in graph/memory/agent | Medium | Run full existing test suite after each router change. Mechanical replacement: `OrgContext` → `MemberContext` is additive (MemberContext is superset). |
| Seed script assumptions don't match real client data | Low | Seed is a starting point. Admin API (S616.3) allows manual adjustments. |

## Progress Tracking

| Story | Status | Est | Actual | Notes |
| ----- | ------ | --- | ------ | ----- |
| S616.1 Migration + models | pending | S | | |
| S616.2 Auth + license middleware | pending | M | | |
| S616.3 Admin API + seed | pending | S | | |
