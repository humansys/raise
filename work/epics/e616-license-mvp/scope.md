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

## Stories

### S616.1: Members, licenses, and auth (M)

Migration 003: drop `api_keys`, create `members` and `licenses` from scratch.
Replace `verify_api_key` → `verify_member` returning `MemberContext` with
plan/features. `requires_plan()` dependency. Update all routers. License service.

**Dependencies:** None

### S616.2: Admin API + seed (S)

`/api/v1/admin` router: generate license, CRUD members. Seed script for
first client org + license + admin member. Deployment docs.

**Dependencies:** S616.1

## Done Criteria

- [ ] `members` and `licenses` tables exist
- [ ] `MemberContext` includes plan + features on every request
- [ ] Endpoints enforce plan requirements via `requires_plan()`
- [ ] Insufficient plan → 403 with clear message
- [ ] Admin can generate licenses and manage members via API
- [ ] Seat limit enforced at member creation
- [ ] First client org + license + admin member seeded

## Plan

```
S616.1 (members + licenses + auth) → S616.2 (admin API + seed)
```

**M1 (after S616.1):** All existing endpoints work with new auth. Plan check works.
**M2 (after S616.2):** Admin can onboard clients. First client seeded. Epic complete.

## Progress Tracking

| Story | Status | Est | Actual | Notes |
| ----- | ------ | --- | ------ | ----- |
| S616.1 Members + licenses + auth | pending | M | | |
| S616.2 Admin API + seed | pending | S | | |
