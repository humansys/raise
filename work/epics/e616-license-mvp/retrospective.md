# E616: raise-server License MVP — Epic Retrospective

**Epic:** E616 | **Date:** 2026-03-25 | **Duration:** 1 session (~4h)
**Stories:** 3 (S616.1 M, S616.2 M, S616.3 S)

## Objective (was)

Add server-side license and member management to raise-server. Organizations
have a plan, members inherit plan features, server enforces on every request.

## Delivered

- **Data model:** `members`, `api_keys` (new schema), `licenses` tables + migration 003
- **Auth chain:** Bearer rsk_... → SHA-256 → member → org → license → MemberContext
- **Plan enforcement:** `requires_plan()`, `requires_role()`, `requires_org_role()`
- **13 REST endpoints:** 4 org + 4 member + 3 key + 2 license
- **Seed script:** First client (HumanSys) + admin + team license + API key
- **90 tests:** 68 unit + 22 E2E against real PG

## What Went Well

### Pre-implementation arch reviews (PAT-E-003)
Ran before both M stories. S616.1: caught 2 simplifications. S616.2: caught 3
(org-scoping dependency, auto-key, defer org delete). **Zero rework across the
entire epic.** This practice is now proven and should be standard.

### TDD with the right abstraction level
- Unit tests: mock session factory for auth gates + schema validation
- E2E: real PG for cross-story integration
- Never needed SQLite-faking-PG (PAT-E-002 confirmed)

### Zero-user advantage
Drop+recreate migration, no backwards compat, no data migration scripts.
This window closes once the first client is seeded in production.

### Dependency factory composition
`requires_plan()` → `requires_role()` → `requires_org_role()` — each builds
on the same pattern. Clean, composable, impossible to bypass (Jidoka).

## What to Improve

### Mock session factory duplication
`_mock_session_factory()` repeated in 4 test files with slight variations.
Extract to shared `conftest.py` fixture before next raise-server story.

### asyncpg connection pool + last_used_at commit
The `last_used_at` update + commit inside `verify_member` leaves asyncpg pool
connections in a dirty state. Fixed in E2E with `NullPool`, but production should
use a connection pool. **Action:** investigate `pool_reset_on_return="rollback"`
or move `last_used_at` to a background task.

### PAT-E-597 keeps recurring
`from __future__ import annotations` breaks FastAPI's runtime `Annotated[]`
resolution. Caught in tests but should be flagged at design time for any
FastAPI project. **Action:** add to project-level guardrails.

## Patterns Discovered

| ID | Pattern | Origin |
|----|---------|--------|
| PAT-E-001 | FastAPI tests with Annotated[] must NOT use future annotations | S616.1 |
| PAT-E-002 | Pure logic tests + real PG smoke > SQLite-faking-PG | S616.1 |
| PAT-E-003 | Pre-implementation arch review saves rework | S616.1, S616.2 |
| PAT-E-004 | requires_org_role() — Jidoka for org-scoping | S616.2 |
| PAT-E-005 | Security-critical logic in single module (auth.py) | S616.2 |
| PAT-E-006 | NullPool for asyncpg E2E tests avoids stale connections | S616.3 |

## Metrics

| Metric | S616.1 | S616.2 | S616.3 | Total |
|--------|--------|--------|--------|-------|
| Size | M | M | S | — |
| Estimated | M | M | S | ~5h |
| Actual | 90min | 90min | 45min | ~4h |
| Unit tests | 33 | 35 | 0 | 68 |
| E2E tests | 6 (smoke) | 14 (smoke) | 22 | 22 (reusable) |
| Files (src) | 6 | 8 | 0 | 14 |
| Files (test) | 4 | 6 | 3 | 13 |
| Endpoints | 0 (updated 3) | 13 | 0 | 13 new |
| Pyright errors | 0 | 0 | 0 | 0 |
| Plan deviations | 0 | 1 | 0 | 1 |

## Architecture Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | Admin = superadmin for MVP | 1 org, seed creates initial data |
| D2 | Single schemas/admin.py | ~15 schemas, not enough for per-resource files |
| D3 | Inline CRUD in routers | 5-10 lines per handler, service would be pass-through |
| D4 | requires_org_role() dependency | Jidoka — impossible to bypass org-scoping |
| D5 | POST /members auto-creates first API key | Value stream — one call to onboard |
| D6 | Defer org DELETE | YAGNI — 0 usage at MVP |
| D7 | generate_api_key() in auth.py | Security-critical code in one place |

## What's Next

- **E621: CLI-side licensing** — raise-pro/raise-cli validates license against server
- **Deploy raise-server** — production environment needed before E621
- **Extract mock session factory** — shared fixture for next raise-server work
