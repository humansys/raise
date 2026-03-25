# E616: raise-server License MVP — Scope

**Jira:** RAISE-616
**Labels:** pro-launch, v2.4
**Branch:** dev (stories branch from dev)
**Depends on:** None (E621 depends on this)
**Design:** [design.md](design.md)

## Objective

Add server-side license and member management to raise-server. Organizations
have a plan, members inherit plan features, server enforces on every request.

## Stories

### S616.1: Data model, auth, and plan enforcement (M)

Migration 003: drop old `api_keys`, create `members`, `api_keys` (new schema),
`licenses`. SQLAlchemy models + Pydantic schemas. Replace `verify_api_key` →
`verify_member` returning `MemberContext`. `requires_plan()` and `requires_role()`
dependencies. Update all existing routers.

**Dependencies:** None

### S616.2: Organization, member, key, and license endpoints + seed (M)

REST endpoints nested under `/api/v1/organizations/{id}/`:
- Organizations: POST, GET list, GET one, PATCH, DELETE (soft)
- Members: POST (create), GET list, PATCH (role), DELETE (soft)
- API Keys: POST (show-once), GET list (metadata), DELETE (revoke)
- License: POST (create/replace), GET (current)

Seed script for first client. Deployment docs.

**Dependencies:** S616.1

## Done Criteria

- [ ] `members`, `api_keys` (new), `licenses` tables exist
- [ ] Auth returns `MemberContext` with plan + features
- [ ] `requires_plan()` returns 403 with clear message
- [ ] `requires_role()` gates admin-only endpoints
- [ ] 15 new endpoints operational (5 org + 4 member + 3 key + 2 license + health)
- [ ] API key shown once on creation, never in GET
- [ ] Soft delete for members/orgs, hard delete for keys
- [ ] Scopes field on API keys (`full_access` default)
- [ ] Seat limit enforced at member creation
- [ ] First client org + license + admin seeded

## Plan

```
S616.1 (models + auth + plan check) → S616.2 (15 endpoints + seed)
```

**M1 (after S616.1):** Existing endpoints work with new auth + plan enforcement.
**M2 (after S616.2):** Full admin API. First client seeded. Epic complete.

## Progress Tracking

| Story | Status | Est | Actual | Notes |
| ----- | ------ | --- | ------ | ----- |
| S616.1 Models + auth | **done** | M | M (90min) | 33 tests, 1.33x velocity. M1 reached. |
| S616.2 Endpoints + seed | pending | M | | |
